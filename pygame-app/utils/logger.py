import json
import time

def log_data(shared_data):
    """
    Logs all relevant data to a JSON file.
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"logs/game_log_{timestamp}.json"

    # Prepare the data to save
    log = {
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "dots_pressed": shared_data["dots_pressed"],
        "end_reason": shared_data["end_reason"],
        "feedback": shared_data["feedback"],
        "total_duration_seconds": None,
        "press_times": [],
    }

    # Calculate total duration if available
    if shared_data["start_time"]:
        log["total_duration_seconds"] = round(time.time() - shared_data["start_time"], 2)

    # Include all recorded press times
    if shared_data["start_time"]:
        log["press_times"] = [
            {
                "time_since_start": round(press_time - shared_data["start_time"], 2),
                "circle_id": circle_id,
            }
            for press_time, circle_id in shared_data["press_times"]
        ]

    # Save to JSON
    with open(filename, "w") as json_file:
        json.dump(log, json_file, indent=4)

    print(f"Log saved to {filename}")
