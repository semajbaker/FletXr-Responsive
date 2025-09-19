from fletx.core import FletXController, RxBool

class AnimationController(FletXController):
    def __init__(self):
        super().__init__()
        self.rx_animation_status = RxBool(False)

    def start_animation(self):
        self.rx_animation_status.value = True
        print("Animation started.")
        return self.rx_animation_status.value

    def stop_animation(self):
        self.rx_animation_status.value = False
        print("Animation stopped.")
        return self.rx_animation_status.value