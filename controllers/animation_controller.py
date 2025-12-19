"""
Animation Controller with proper FletXController initialization.

File: controllers/animation_controller.py
"""
from fletx import FletX
from fletx.core import FletXController

class AnimationController(FletXController):
    def __init__(self):
        super().__init__()
        self.rx_animation_status = self.create_rx_bool(False)

    def start_animation(self):
        """Start the animation"""
        self.rx_animation_status.value = True
        print("Animation started.")
        return self.rx_animation_status.value

    def stop_animation(self):
        """Stop the animation"""
        self.rx_animation_status.value = False
        print("Animation stopped.")
        return self.rx_animation_status.value

FletX.put(AnimationController(), tag='animation_ctrl')