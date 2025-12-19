from fletx.navigation import ModuleRouter
from fletx.decorators import register_router
from pages.auth.signin_screen import SignInScreen
from pages.auth.signup_screen import SignUpScreen
from pages.auth.forgot_password_screen import ForgotPasswordScreen

routes = [
    {
        'path': '/signin', 'component': SignInScreen
    },
    {
        'path': '/signup', 'component': SignUpScreen
    },
    {
        'path': '/forgot-password', 'component': ForgotPasswordScreen
    },
]

@register_router
class AppRouter(ModuleRouter):
    name = "AppRoutes"
    base_path = "/"
    is_root = True
    routes = routes
    sub_routers = []
