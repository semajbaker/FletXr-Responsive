from fletx.navigation import ModuleRouter
from fletx.decorators import register_router

from app.utils.route_guards import AuthGuard
from app.pages.auth.signin_screen import SignInScreen
from app.pages.auth.signup_screen import SignUpScreen
from app.pages.auth.forgot_password_screen import ForgotPasswordScreen
from app.pages.core.dashboard_screen import HomeScreen

routes = [
    {
        "path": "/",
        "component": HomeScreen,
        "guards": [AuthGuard()],
    },
    {
        'path': '/signin', 'component': SignInScreen
    },
    {
        'path': '/signup', 'component': SignUpScreen
    },
    {
        'path': '/forgot-password', 'component': ForgotPasswordScreen
    }
]

@register_router
class AppRouter(ModuleRouter):
    name = "AppRoutes"
    base_path = "/"
    is_root = True
    routes = routes
    sub_routers = []
