import time


class GameInterface:
    def __init__(self, manager):
        self.manager = manager
        self.game_ended = False
        self.rescale_to_game_screen = False
        self.game_screen_width = None
        self.game_screen_height = None
        self.shared_data = {}

    def start(self):
        self.manager.shared_data["start_time"] = time.time()

    def handle_event(self, event):
        pass

    def update(self, finger_x=None, finger_y=None):
        pass

    def draw(self, screen):
        pass

    def add_shared_data(self):
        self.manager.shared_data.update(self.shared_data)

    def rmv_shared_data(self):
        for key in self.shared_data.keys():
            if key in self.manager.shared_data.keys():
                self.manager.shared_data.pop(key)

    def end_game(self):
        self.manager.shared_data["end_time"] = time.time()
        self.game_ended = True
