import flet as ft 
from math import pi, sin, cos

class AnimationManager:
    def __init__(self, page: ft.Page, animation_controller):
        self.page = page
        self.animation_ctrl = animation_controller
        self.angle = 0
        self.scale_factor = 0
        self.opacity_factor = 0
        self.boxes = []
        
        # Subscribe to animation status changes
        self.animation_ctrl.rx_animation_status.listen(self._on_animation_status_changed)
        
    def _on_animation_status_changed(self):
        """Called when animation status changes"""
        is_animating = self.animation_ctrl.rx_animation_status.value
        if is_animating and self.boxes:
            print("Animation status changed: Starting")
            self._animate_frame()
        else:
            print("Animation status changed: Stopping")
    
    def set_boxes(self, box1, box2, box3, box4):
        """Set the boxes to be animated"""
        self.boxes = [box1, box2, box3, box4]
    
    def _animate_frame(self):
        """Single animation frame - called repeatedly by timer"""
        if not self.animation_ctrl.rx_animation_status.value:
            return
            
        # Update animation values
        self.angle += 0.1
        self.scale_factor += 0.05
        self.opacity_factor += 0.08
        
        box1, box2, box3, box4 = self.boxes
        
        # Box 1 - Large circular orbit
        x1 = 70 + 30 * cos(self.angle)
        y1 = 30 + 20 * sin(self.angle)
        box1.scale = ft.Scale(1.0 + 0.3 * sin(self.scale_factor))
        box1.rotate = self.angle * 2
        box1.opacity = 0.8 + 0.2 * sin(self.opacity_factor)
        
        # Box 2 - Figure-8 pattern
        x2 = 130 + 25 * cos(self.angle * 1.5)
        y2 = 50 + 15 * sin(self.angle * 3)
        box2.scale = ft.Scale(0.8 + 0.4 * cos(self.scale_factor * 1.2))
        box2.rotate = -self.angle * 1.5
        box2.opacity = 0.7 + 0.3 * cos(self.opacity_factor * 1.1)
        
        # Box 3 - Pendulum-like motion
        x3 = 40 + 35 * sin(self.angle * 0.8)
        y3 = 60 + 10 * cos(self.angle * 2)
        box3.scale = ft.Scale(1.2 + 0.2 * sin(self.scale_factor * 0.9))
        box3.rotate = self.angle * 3
        box3.opacity = 0.9 + 0.1 * sin(self.opacity_factor * 1.3)
        
        # Box 4 - Spiral motion
        radius = 20 + 10 * sin(self.angle * 0.5)
        x4 = 100 + radius * cos(self.angle * 2.5)
        y4 = 10 + radius * sin(self.angle * 2.5)
        box4.scale = ft.Scale(0.9 + 0.5 * cos(self.scale_factor * 0.7))
        box4.rotate = -self.angle * 2.5
        box4.opacity = 0.8 + 0.2 * cos(self.opacity_factor * 0.8)
        
        # Update all boxes
        try:
            for box in self.boxes:
                box.update()
        except Exception as e:
            print(f"Animation update error: {e}")
            self.animation_ctrl.stop_animation()
            return
        
        # Schedule next frame (50ms = 20fps)
        if self.animation_ctrl.rx_animation_status.value:
            self.page.run_task(self._schedule_next_frame)
    
    async def _schedule_next_frame(self):
        """Schedule the next animation frame"""
        import asyncio
        await asyncio.sleep(0.05)
        if self.animation_ctrl.rx_animation_status.value:
            self._animate_frame()