import time


class GameInterface:
    def __init__(self, manager, level=None):
        self.manager = manager
        self.level = level
        self.game_ended = False

    def start(self):
        self.manager.shared_data["start_time"] = time.time()

    def handle_event(self, event):
        pass

    def update(self, finger_x=None, finger_y=None):
        pass

    def draw(self, screen):
        pass

    def end_game(self):
        self.game_ended = True
