import os 
import json
import time
from pathlib import Path
import csv

class Logger: 
    def __init__(self): 
        
        # Create a folder to store all logs from one session       
        self.folder_name = Path(f"logs/game_{time.strftime("%Y%m%d-%H%M%S")}")
        os.makedirs(self.folder_name, exist_ok=True)
        
        # Initialize the filenames
        self.game_log_filename = None
        self.trajectory_filename = None

        
    def start_new_game(self): 
        '''
        Creates a new game log file and a new trajectory file (starts on each entry of the game screen; 
        all game log and trajectory files from one session get stored in the same folder)
        '''
        current_time = time.strftime("%Y%m%d-%H%M%S")
        
        # create a JSON file(name) to log the game
        self.game_log_filename = self.folder_name / f"game_log_{current_time}.json"
        
        # create a CSV file to log the trajectory
        self.trajectory_filename = self.folder_name / f"trajectory_{current_time}.json"
        with open(self.trajectory_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
        
            # Write header, if it does not exist (it should not, as it's the start of the game)
            file_exists = os.path.isfile(self.trajectory_filename)
            if not file_exists:
                writer.writerow(['timepoint', 'finger_x', 'finger_y'])
                
            print("Created trajectory file.")
                
    def append_finger_data(self, finger_x, finger_y):
        '''
        Check if the file exists to determine if headers need to be written
        '''
        # Raise warning if the filename is not set
        if self.trajectory_filename is None:
            raise ValueError("trajectory_filename is not set. Call start_new_game() first.")
        
        # Add current trajectory data to the trajectory csv file 
        current_time = time.strftime("%H:%M:%S")
        with open(self.trajectory_filename, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Write the data row
            print("Trying to write data into trajectory file.")
            writer.writerow([current_time, finger_x, finger_y])


    def log_shared_data(self, shared_data): 
        '''
        Logs all relevant data to a JSON file.
        '''
        # Raise warning if the filename is not set
        if self.game_log_filename is None:
            raise ValueError("game_log_filename is not set. Call start_new_game() first.")
        
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
        with open(self.game_log_filename, "w") as json_file:
            json.dump(log, json_file, indent=4)

        print(f"Log saved to {self.game_log_filename}")