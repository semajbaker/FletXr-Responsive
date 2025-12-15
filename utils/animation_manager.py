"""
Animation management system for FletXr applications using proper lifecycle methods.

File: utils/animation_manager.py
"""
import flet as ft 
from math import pi, sin, cos
from fletx import FletX
from typing import Optional, Callable
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
    _listener_callback: Optional[Callable] = None
    
    @classmethod
    def get_controller(cls) -> AnimationController:
        """Get the animation controller from FletX dependency injection"""
        controller = FletX.find(AnimationController, tag='animation_ctrl')
        
        if controller is None:
            raise RuntimeError("AnimationController not found! Make sure it's initialized in main.py")
        
        return controller
    
    @classmethod
    def cleanup_listener(cls):
        """Remove the current listener from the controller"""
        if cls._listener_callback is not None:
            controller = cls.get_controller()
            try:
                # Remove the listener
                controller.rx_animation_status.dispose()
                print("AnimationManager: Listener removed")
            except (ValueError, AttributeError) as e:
                print(f"AnimationManager: Error removing listener: {e}")
            finally:
                cls._listener_callback = None
    
    @classmethod
    def cleanup(cls):
        """Cleanup for page navigation - reset animation state but keep controller"""
        # Stop animation first
        controller = cls.get_controller()
        controller.stop_animation()
        
        # Remove listener
        cls.cleanup_listener()
        
        # Reset animation state
        cls._angle = 0
        cls._scale_factor = 0
        cls._opacity_factor = 0
        cls._boxes = []
        cls._page = None
        
        print("AnimationManager: Page cleanup completed (controller preserved)")
    
    @classmethod
    def initialize_with_page(cls, page: ft.Page):
        """Initialize the animation system with a page reference"""
        # Clean up any existing listener first
        cls.cleanup_listener()
        
        cls._page = page
        
        # Get the global controller
        controller = cls.get_controller()
        
        # Create and store the listener callback
        cls._listener_callback = cls._on_animation_status_changed
        
        # Subscribe to animation status changes
        controller.rx_animation_status.listen(cls._listener_callback)
        
        print("AnimationManager: Initialized with page and new listener attached")
    
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
        """Stop the animation"""
        controller = cls.get_controller()
        controller.stop_animation()
    
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