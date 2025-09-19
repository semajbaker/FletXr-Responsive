import flet as ft 
import time
from math import pi, sin, cos
 
def animate_boxes(self, box1, box2, box3, box4, animate):
    self.angle = 0
    self.scale_factor = 0
    self.opacity_factor = 0

    while animate == True:
        # Create orbital motion with varying speeds
        self.angle += 0.1
        self.scale_factor += 0.05
        self.opacity_factor += 0.08
        
        # Box 1 - Large circular orbit
        self.x1 = 70 + 30 * cos(self.angle)
        self.y1 = 30 + 20 * sin(self.angle)
        box1.scale = ft.Scale(1.0 + 0.3 * sin(self.scale_factor))
        box1.rotate = self.angle * 2
        box1.opacity = 0.8 + 0.2 * sin(self.opacity_factor)
        
        # Box 2 - Figure-8 pattern
        self.x2 = 130 + 25 * cos(self.angle * 1.5)
        self.y2 = 50 + 15 * sin(self.angle * 3)
        box2.scale = ft.Scale(0.8 + 0.4 * cos(self.scale_factor * 1.2))
        box2.rotate = -self.angle * 1.5
        box2.opacity = 0.7 + 0.3 * cos(self.opacity_factor * 1.1)
        
        # Box 3 - Pendulum-like motion
        self.x3 = 40 + 35 * sin(self.angle * 0.8)
        self.y3 = 60 + 10 * cos(self.angle * 2)
        box3.scale = ft.Scale(1.2 + 0.2 * sin(self.scale_factor * 0.9))
        box3.rotate = self.angle * 3
        box3.opacity = 0.9 + 0.1 * sin(self.opacity_factor * 1.3)
        
        # Box 4 - Spiral motion
        radius = 20 + 10 * sin(self.angle * 0.5)
        self.x4 = 100 + radius * cos(self.angle * 2.5)
        self.y4 = 10 + radius * sin(self.angle * 2.5)
        box4.scale = ft.Scale(0.9 + 0.5 * cos(self.scale_factor * 0.7))
        box4.rotate = -self.angle * 2.5
        box4.opacity = 0.8 + 0.2 * cos(self.opacity_factor * 0.8)
        
        # Update all boxes
        for i, box in enumerate([box1, box2, box3, box4]):
            box.update()
        
        time.sleep(0.05)  # Smooth 20fps animation