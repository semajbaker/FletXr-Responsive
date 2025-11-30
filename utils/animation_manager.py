"""
Animation management system for FletXr applications using proper lifecycle methods.

File: utils/animation_manager.py
"""
import flet as ft 
from math import pi, sin, cos
from fletx import FletX
from typing import Optional
from controllers.animation_controller import AnimationController

class AnimationManager:
    """
    Static utility class for easier access to animation functionality.
    Uses FletX dependency injection system.
    """
    
    _page: Optional[ft.Page] = None
    _angle = 0
    _scale_factor = 0
    _opacity_factor = 0
    _boxes = []
    
    @classmethod
    def get_controller(cls) -> AnimationController:
        """Get the animation controller from FletX dependency injection"""
        controller = FletX.find(AnimationController, tag='animation_ctrl')
        
        if controller is None:
            # If not found, create and register it
            controller = AnimationController()
            FletX.put(controller, tag='animation_ctrl')
            
            # Subscribe to animation status changes
            controller.rx_animation_status.listen(cls._on_animation_status_changed)
        
        return controller
    
    @classmethod
    def dispose_controller(cls):
        """Dispose the animation controller and clean up resources"""
        controller = FletX.find(AnimationController, tag='animation_ctrl')
        
        if controller is not None:
            # Stop animation first
            controller.stop_animation()
            
            # Clean up listeners
            if hasattr(controller.rx_animation_status, '_listeners'):
                if hasattr(controller.rx_animation_status._listeners, 'clear'):
                    controller.rx_animation_status._listeners.clear()
            
            # Remove from FletX dependency injection
            try:
                from fletx.core.di import DI
                tag = 'animation_ctrl'
                if AnimationController in DI._instances:
                    if tag in DI._instances[AnimationController]:
                        # Call dispose if available
                        if hasattr(controller, 'dispose'):
                            controller.dispose()
                        # Remove from DI
                        del DI._instances[AnimationController][tag]
                        print("AnimationController removed from DI")
            except Exception as e:
                print(f"Error removing controller from DI: {e}")
        
        return controller
    
    @classmethod
    def cleanup(cls):
        """Full cleanup of animation system"""
        # Dispose controller
        cls.dispose_controller()
        
        # Reset class-level state
        cls._angle = 0
        cls._scale_factor = 0
        cls._opacity_factor = 0
        cls._boxes = []
        cls._page = None
        
        print("AnimationManager completely cleaned up")
    
    @classmethod
    def initialize_with_page(cls, page: ft.Page):
        """Initialize the animation system with a page reference"""
        cls._page = page
        print("AnimationManager initialized with page")
    
    @classmethod
    def _on_animation_status_changed(cls):
        """Called when animation status changes"""
        controller = cls.get_controller()
        is_animating = controller.rx_animation_status.value
        
        if is_animating and cls._boxes:
            print("Animation status changed: Starting")
            cls._animate_frame()
        else:
            print("Animation status changed: Stopping")
    
    @classmethod
    def set_boxes(cls, box1, box2, box3, box4):
        """Set the boxes to be animated"""
        cls._boxes = [box1, box2, box3, box4]
    
    @classmethod
    def start_animation(cls):
        """Start the animation"""
        controller = cls.get_controller()
        controller.start_animation()
    
    @classmethod
    def stop_animation(cls):
        """Stop the animation and cleanup"""
        controller = cls.get_controller()
        controller.stop_animation()
        
        # Perform cleanup after stopping
        cls.cleanup()
    
    @classmethod
    def is_animating(cls) -> bool:
        """Check if animation is currently running"""
        controller = cls.get_controller()
        return controller.rx_animation_status.value
    
    @classmethod
    def _animate_frame(cls):
        """Single animation frame - called repeatedly by timer"""
        controller = cls.get_controller()
        
        if not controller.rx_animation_status.value:
            return
        
        if not cls._boxes or len(cls._boxes) < 4:
            print("Animation error: Insufficient boxes")
            controller.stop_animation()
            return
            
        # Update animation values
        cls._angle += 0.1
        cls._scale_factor += 0.05
        cls._opacity_factor += 0.08
        
        box1, box2, box3, box4 = cls._boxes
        
        # Box 1 - Large circular orbit
        x1 = 70 + 30 * cos(cls._angle)
        y1 = 30 + 20 * sin(cls._angle)
        box1.scale = ft.Scale(1.0 + 0.3 * sin(cls._scale_factor))
        box1.rotate = cls._angle * 2
        box1.opacity = 0.8 + 0.2 * sin(cls._opacity_factor)
        
        # Box 2 - Figure-8 pattern
        x2 = 130 + 25 * cos(cls._angle * 1.5)
        y2 = 50 + 15 * sin(cls._angle * 3)
        box2.scale = ft.Scale(0.8 + 0.4 * cos(cls._scale_factor * 1.2))
        box2.rotate = -cls._angle * 1.5
        box2.opacity = 0.7 + 0.3 * cos(cls._opacity_factor * 1.1)
        
        # Box 3 - Pendulum-like motion
        x3 = 40 + 35 * sin(cls._angle * 0.8)
        y3 = 60 + 10 * cos(cls._angle * 2)
        box3.scale = ft.Scale(1.2 + 0.2 * sin(cls._scale_factor * 0.9))
        box3.rotate = cls._angle * 3
        box3.opacity = 0.9 + 0.1 * sin(cls._opacity_factor * 1.3)
        
        # Box 4 - Spiral motion
        radius = 20 + 10 * sin(cls._angle * 0.5)
        x4 = 100 + radius * cos(cls._angle * 2.5)
        y4 = 10 + radius * sin(cls._angle * 2.5)
        box4.scale = ft.Scale(0.9 + 0.5 * cos(cls._scale_factor * 0.7))
        box4.rotate = -cls._angle * 2.5
        box4.opacity = 0.8 + 0.2 * cos(cls._opacity_factor * 0.8)
        
        # Update all boxes
        try:
            for box in cls._boxes:
                box.update()
        except Exception as e:
            print(f"Animation update error: {e}")
            controller.stop_animation()
            cls.cleanup()
            return
        
        # Schedule next frame (50ms = 20fps)
        if controller.rx_animation_status.value and cls._page:
            cls._page.run_task(cls._schedule_next_frame)
    
    @classmethod
    async def _schedule_next_frame(cls):
        """Schedule the next animation frame"""
        import asyncio
        await asyncio.sleep(0.05)
        
        controller = cls.get_controller()
        if controller.rx_animation_status.value:
            cls._animate_frame()