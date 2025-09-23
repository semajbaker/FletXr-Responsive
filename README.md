# FletXr Responsive System

A production-ready responsive UI system for FletXr applications that automatically adapts components to different screen sizes using reactive breakpoints.

## The Problem

FletXr doesn't include a built-in responsive system, making it challenging to create applications that work seamlessly across mobile, tablet, and desktop devices. Developers often resort to manual width calculations or static layouts that don't adapt to screen changes.

## The Solution

This responsive system provides:

- **Automatic breakpoint detection** - Detects mobile, tablet, and desktop screen sizes
- **Reactive UI updates** - Components automatically resize when breakpoints change
- **Zero boilerplate** - Simple API that integrates seamlessly with existing FletXr apps
- **Performance optimized** - Uses FletXr's native reactive properties for efficient updates
- **Type-safe** - Full Dart/Flutter-style typing and structure

## Quick Start

### 1. Install Dependencies

```bash
pip install flet fletxr
```

### 2. Basic Setup

```python
import flet as ft
from fletx.app import FletXApp
from utils.responsive_manager import MediaQuery

def main(page: ft.Page):
    # Initialize responsive system
    MediaQuery.initialize_with_page(page)
    
    # Register breakpoints (mobile: 0-768px, tablet: 768-1024px, desktop: 1024px+)
    MediaQuery.register('mobile', 0, 768)
    MediaQuery.register('tablet', 768, 1024)
    MediaQuery.register('desktop', 1024, 1920)
    
    # Complete setup
    MediaQuery.complete_registration()
    
    # Your app code here
    app = FletXApp(title="Responsive App", initial_route="/")
    app._main(page)

ft.app(target=main)
```

### 3. Create Responsive Components

```python
from widgets.input_field import input_field

# This input field automatically adapts to screen size
email_field = input_field("Enter email", ft.Icons.EMAIL, False)
```

## Features

### Automatic Screen Size Detection
- **Mobile**: 0-768px (compact input fields, smaller containers)
- **Tablet**: 768-1024px (medium-sized components)
- **Desktop**: 1024px+ (full-width components with optimal spacing)

### Reactive Component Updates
Components using the responsive system automatically update their dimensions when users:
- Resize the browser window
- Rotate mobile devices
- Switch between desktop and mobile views

### Clean Architecture
```
/controllers     # Core responsive logic
/utils          # Static access layer  
/widgets        # Responsive UI components
/constants      # Breakpoint definitions
```

## API Reference

### MediaQuery Class

```python
# Setup
MediaQuery.initialize_with_page(page)
MediaQuery.register(name, min_width, max_width)
MediaQuery.complete_registration()

# Current state
current_breakpoint = MediaQuery.get_current_breakpoint()  # 'mobile', 'tablet', 'desktop'
window_width = MediaQuery.get_current_width()            # Current pixel width

# Reactive properties (for custom components)
container_width_rx = MediaQuery.get_container_width_rx()
field_width_rx = MediaQuery.get_field_width_rx()
```

### Custom Responsive Components

```python
class ResponsiveCard(ft.Container):
    def __init__(self):
        self.width_rx = MediaQuery.get_container_width_rx()
        super().__init__(width=self.width_rx.value)
        
        # Listen for changes
        self.width_rx.listen(self._on_width_changed)
    
    def _on_width_changed(self):
        self.width = self.width_rx.value
        if hasattr(self, 'page') and self.page:
            self.update()
```

## Real-World Example

See the complete signin screen implementation in `/pages/auth/signin_screen.py` that demonstrates:
- Responsive input fields that adapt from mobile (180px) to desktop (280px)
- Container layouts that scale appropriately
- Smooth transitions between breakpoints

## Architecture

### Controller Pattern
- **MediaQueryController**: Core reactive state management
- **MediaQuery**: Static utility class for easy access
- **Shared State**: Prevents multiple instance conflicts using class-level properties

### Reactive Flow
```
Window Resize → Breakpoint Detection → Update Reactive Properties → Component Updates → UI Refresh
```

## Browser Support

Works in all environments that support FletXr:
- Desktop applications (Windows, macOS, Linux)
- Web browsers (Chrome, Firefox, Safari, Edge)
- Mobile web views

## Contributing

This is an early implementation for the growing FletXr ecosystem. Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Test with multiple screen sizes
4. Submit a pull request

## Why This Matters

FletXr is a powerful but young framework. This responsive system fills a critical gap by providing the building blocks for modern, adaptive user interfaces. As FletXr matures, patterns like this help establish best practices for the community.

**Built for the FletXr community** - Helping create responsive, professional applications with Python