from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.collections as mc
from datetime import datetime
import matplotlib.animation as animation
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter

# Fixed parameters for plotting
plt.rcParams.update({"font.size": 14})
bigger_font_size = 14


def interpolate_bad_angles(angle, lower_bound=-50, upper_bound=50):
    """Interpolate out-of-bound values smoothly."""
    angle = np.array(angle, dtype=float)
    valid_mask = (angle >= lower_bound) & (angle <= upper_bound)
    indices = np.arange(len(angle))

    # Interpolate only the out-of-bound values
    angle[~valid_mask] = np.interp(
        indices[~valid_mask], indices[valid_mask], angle[valid_mask]
    )
    return angle


def colorline(ax, t, y, norm, cmap="cividis"):
    """Creates and returns a time-colored LineCollection (1D: time vs. angle)."""
    # Build points
    points = np.array([t, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    lc = mc.LineCollection(segments, cmap=cmap, norm=norm)
    lc.set_array(t)
    ax.add_collection(lc)

    # Adjust axes
    ax.set_xlim(min_t, max_t)
    ax.set_ylim(y.min(), y.max())

    return lc


def colorline_2d(ax, t, x, y, norm, cmap="cividis"):
    """Creates and returns a time-colored LineCollection for 2D data: x(t), y(t)."""
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    lc = mc.LineCollection(segments, cmap=cmap, norm=norm)
    lc.set_array(t)  # color segments by time
    ax.add_collection(lc)

    ax.set_xlim(min_x - 20, max_x + 20)
    ax.set_ylim(min_y - 20, max_y + 20)

    return lc


def animate_kinetics_knee(
    timepoints_in_ms_angle, angle, timepoints_in_s_finger, finger_x, finger_y
):
    """Same layout as 'analyze_kinetics_knee', but creates an animation"""

    # Preprocess the angle data
    angle = interpolate_bad_angles(angle)
    timepoints_in_s_angle = timepoints_in_ms_angle / 1000.0
    dt_angle = np.mean(np.diff(timepoints_in_s_angle))

    # Smooth the angle
    angle_smooth = savgol_filter(angle, window_length=15, polyorder=3)

    # Compute derivatives
    v_angle = savgol_filter(np.gradient(angle_smooth, dt_angle), 15, 3)
    a_angle = savgol_filter(np.gradient(v_angle, dt_angle), 15, 3)
    j_angle = savgol_filter(np.gradient(a_angle, dt_angle), 15, 3)

    # Some numeric metrics
    path_length = np.sum(angle_smooth)
    print("Kinetic Analysis Metrics:")
    print(f"Total path length: {path_length:.2f} units")
    print(f"Average velocity: {np.mean(v_angle):.2f} units/s")
    print(f"Max velocity: {np.max(v_angle):.2f} units/s")
    print(f"Average acceleration: {np.mean(a_angle):.2f} units/s^2")
    print(f"Max acceleration: {np.max(a_angle):.2f} units/s^2")
    print(f"Average jerk: {np.mean(j_angle):.2f} units/s^3")
    print(f"Max jerk: {np.max(j_angle):.2f} units/s^3")

    # Animate up to the length of the angle array. If trajectory is a different length, find factor to align them
    n_frames = len(timepoints_in_s_angle)

    # Norm across all time-based color lines to keep the colors consistent
    max_time_val = max(timepoints_in_s_finger[-1], timepoints_in_s_angle[-1])
    norm = plt.Normalize(0, max_time_val)

    # Data arrays for each angle subplot
    angle_series = [angle_smooth, v_angle, a_angle, j_angle]
    labels = ["θ [deg]", "ω [deg/s]", "α [deg/s²]", "β [deg/s³]"]

    # Figure and GridSpec
    fig = plt.figure(figsize=(14, 8), constrained_layout=True)
    gs = fig.add_gridspec(
        6,
        3,
        width_ratios=[1, 2, 0.1],
        height_ratios=[0.3, 1, 1, 1, 1, 0.3],
        hspace=0.3,
        wspace=0.4,
    )

    # Trajectory subplot
    ax_traj = fig.add_subplot(gs[1:5, 0:1])
    ax_traj.set_xlabel("X position [pixels]", fontsize=bigger_font_size)
    ax_traj.set_ylabel("Y position [pixels]", fontsize=bigger_font_size)

    # Four subplots for angle, velocity, accel, jerk
    axs = [fig.add_subplot(gs[i, 1]) for i in range(1, 5)]
    for i, ax in enumerate(axs):
        ax.set_ylabel(labels[i], fontsize=bigger_font_size)
        ax.grid(True)

        # Set x-lims and y-lims dynamically in the update
        if i < len(axs) - 1:
            ax.set_xticklabels([])
        else:
            ax.set_xlabel("Time [s]", fontsize=bigger_font_size)
            ax.set_xticks(range(0, int(max_time_val), 5))

    # Store references to the "LineCollections". Is deleted each frame, and then a new partial one is created.
    traj_lc = None
    angle_lcs = [None] * 4  # one for each subplot

    def init():
        # Don't draw anything yet
        return []

    def update(frame):
        nonlocal traj_lc, angle_lcs

        # Remove old line collections if they exist
        if traj_lc is not None:
            if traj_lc in ax_traj.collections:
                traj_lc.remove()
            traj_lc = None
        for i in range(4):
            if angle_lcs[i] is not None:
                # Check the correct Axes
                if angle_lcs[i] in axs[i].collections:
                    angle_lcs[i].remove()
            angle_lcs[i] = None

        # Partial data for the trajectory
        t_traj_part = timepoints_in_s_finger[:frame]
        x_part = finger_x[:frame]
        y_part = finger_y[:frame]

        # Create a new partial line collection for the trajectory
        if len(x_part) > 1:
            traj_lc = colorline_2d(
                ax_traj, t_traj_part, x_part, y_part, norm, cmap="cividis"
            )

        # Get min and max values for plotting
        np_angle_arr = np.array(angle_series)
        np_angle_arr_min = np.min(np_angle_arr, axis=1)
        np_angle_arr_max = np.max(np_angle_arr, axis=1)
        limits = [
            (
                min_val - (0.1 * (max_val - min_val)),
                max_val + (0.1 * (max_val - min_val)),
            )
            for min_val, max_val in zip(np_angle_arr_min, np_angle_arr_max)
        ]

        # Create a new partial line collection for each angle subplot
        for i, ax in enumerate(axs):
            data_part = angle_series[i][:frame]
            t_part = timepoints_in_s_angle[:frame]

            if len(data_part) > 1:
                angle_lcs[i] = colorline(ax, t_part, data_part, norm, cmap="cividis")

            ax.set_ylim(limits[i][0], limits[i][1])
            ax.set_xticklabels([])  # no x-axis labels

        axs[-1].set_xlabel("Time [s]", fontsize=bigger_font_size)
        axs[-1].set_xticks(range(0, int(max_time_val), 5))

        # Return updated artists
        updated_objs = []
        if traj_lc is not None:
            updated_objs.append(traj_lc)
        for lc in angle_lcs:
            if lc is not None:
                updated_objs.append(lc)
        return updated_objs

    dt = np.mean(np.diff(timepoints_in_ms_angle))
    # Run FuncAnimation
    ani = animation.FuncAnimation(
        fig,
        update,
        frames=n_frames,
        init_func=init,
        interval=dt,
        blit=False,
    )

    # Save files and make the layout nicer
    plt.tight_layout()
    plt.show()
    # saving to m4 using ffmpeg writer
    ani.save("increasingStraightLine.gif")


def convert_time_to_seconds(time_str):
    """Convert time in HH:MM:SS format to seconds since midnight."""
    try:
        t = datetime.strptime(time_str, "%H:%M:%S")
        return t.hour * 3600 + t.minute * 60 + t.second
    except ValueError:
        return np.nan


def load_data(csv_file, has_headers=False):
    """Load 2D trajectory data (x,y) from a CSV file."""
    if has_headers:
        df = pd.read_csv(csv_file)
    else:
        df = pd.read_csv(
            csv_file,
            header=None,
            names=["timepoint", "time_in_microseconds", "finger_x", "finger_y"],
        )

    # Ensure needed columns exist
    required_cols = {"timepoint", "time_in_microseconds", "finger_x", "finger_y"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV file must contain columns: {required_cols}")

    # Convert columns
    df["finger_x"] = pd.to_numeric(df["finger_x"], errors="coerce")
    df["finger_y"] = pd.to_numeric(df["finger_y"], errors="coerce")
    df["time_in_microseconds"] = pd.to_numeric(
        df["time_in_microseconds"], errors="coerce"
    )
    df["timepoint"] = df["timepoint"].astype(str)

    # Drop invalid rows
    df.dropna(
        subset=["timepoint", "time_in_microseconds", "finger_x", "finger_y"],
        inplace=True,
    )

    # Convert time strings to seconds
    timepoints = df["timepoint"].tolist()
    times_in_seconds = np.array([convert_time_to_seconds(tp) for tp in timepoints])

    # Combine with microseconds
    additional_time_in_ms = df["time_in_microseconds"].to_numpy() / 1000
    timepoints_in_ms = times_in_seconds * 1000 + additional_time_in_ms

    finger_x = df["finger_x"].to_numpy()
    finger_y = df["finger_y"].to_numpy()

    return timepoints_in_ms, finger_x, finger_y


def load_angle_data(csv_file):
    """Load knee-angle data from CSV with columns like [timepoint, time_in_microseconds, knee_angle]."""
    df = pd.read_csv(csv_file)
    if not {"timepoint", "time_in_microseconds", "knee_angle"}.issubset(df.columns):
        raise ValueError(
            "CSV must have columns: timepoint, time_in_microseconds, knee_angle"
        )

    # Convert angle
    angle = pd.to_numeric(df["knee_angle"], errors="coerce")

    # Convert time
    df["time_in_microseconds"] = pd.to_numeric(
        df["time_in_microseconds"], errors="coerce"
    )
    df["timepoint"] = df["timepoint"].astype(str)

    # Drop invalid rows
    df.dropna(subset=["timepoint", "time_in_microseconds", "knee_angle"], inplace=True)

    timepoints = df["timepoint"].tolist()
    times_in_seconds = np.array([convert_time_to_seconds(tp) for tp in timepoints])

    additional_time_in_ms = df["time_in_microseconds"].to_numpy() / 1000
    timepoints_in_ms = times_in_seconds * 1000 + additional_time_in_ms

    return timepoints_in_ms, angle.to_numpy()


def synchronize_and_resample(
    timepoints_in_ms_angle, timepoints_in_ms_finger, angle, finger_x, finger_y
):
    dt1 = np.mean(np.diff(timepoints_in_ms_angle))
    dt2 = np.mean(np.diff(timepoints_in_ms_finger))
    # dt_new = int((dt1 + dt2) / 2)
    dt_new = min(dt1, dt2)

    # Define the new common time grid
    t_min, t_max = (
        max(timepoints_in_ms_finger[0], timepoints_in_ms_angle[0]),
        min(timepoints_in_ms_finger[-1], timepoints_in_ms_angle[-1]),
    )
    t_new = np.arange(t_min, t_max, dt_new)

    # Interpolate both time series onto the new grid
    interp_angle = interp1d(
        timepoints_in_ms_angle, angle, kind="linear", fill_value="extrapolate"
    )
    interp_finger_x = interp1d(
        timepoints_in_ms_finger, finger_x, kind="linear", fill_value="extrapolate"
    )
    interp_finger_y = interp1d(
        timepoints_in_ms_finger, finger_y, kind="linear", fill_value="extrapolate"
    )

    angle_new = interp_angle(t_new)
    finger_x_new = interp_finger_x(t_new)
    finger_y_new = interp_finger_y(t_new)
    t_new -= t_new[0]
    return t_new, angle_new, finger_x_new, finger_y_new


if __name__ == "__main__":

    traj_path = Path(
        "/Users/clarkbaeker/Documents/projects/rehab-game/pygame-app/logs/game_20250204-143649/trajectory_20250204-144020.csv"
    )
    angle_path = Path(
        "/Users/clarkbaeker/Documents/projects/rehab-game/pygame-app/logs/game_20250204-143649/knee_angle_20250204-144020.csv"
    )

    # Load 2D trajectory
    timepoints_in_ms_finger, finger_x, finger_y = load_data(traj_path, has_headers=True)

    # Load knee-angle
    timepoints_in_ms_angle, angle = load_angle_data(angle_path)

    # Synchronize angle and finger data
    time_in_ms, angle, finger_x, finger_y = synchronize_and_resample(
        timepoints_in_ms_angle, timepoints_in_ms_finger, angle, finger_x, finger_y
    )

    # Convert timepoints to seconds for finger data
    timepoints_in_s = time_in_ms / 1000.0

    # Flip Y to match screen coordinates if needed
    finger_y = 800 - finger_y

    # Get min and max positions
    min_x = finger_x.min()
    max_x = finger_x.max()
    min_y = finger_y.min()
    max_y = finger_y.max()
    min_t = timepoints_in_s.min()
    max_t = timepoints_in_s.max()
    min_angle = angle.min()
    max_angle = angle.max()

    # Animate the data
    animate_kinetics_knee(time_in_ms, angle, timepoints_in_s, finger_x, finger_y)
