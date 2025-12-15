"""
Animation Controller with proper FletXController initialization.

File: controllers/animation_controller.py
"""
from fletx.core import FletXController, RxBool

class AnimationController(FletXController):
    def __init__(self):
        # IMPORTANT: Use auto_initialize=False to prevent event loop issues
        super().__init__(auto_initialize=False)
        self.rx_animation_status = self.create_rx_bool(False)
        
        # Now manually initialize
        self.initialize()
        self.ready()
        print("AnimationController initialized")

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