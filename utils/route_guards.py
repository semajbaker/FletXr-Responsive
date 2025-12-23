from fletx.core.routing.guards import RouteGuard
from fletx import FletX
from controllers.auth_controller import SessionController

class AuthGuard(RouteGuard):

    async def can_activate(self, context) -> bool:
        """Check if user is authenticated"""
        session: SessionController = FletX.find(
            SessionController, tag="session_ctrl"
        )

        allowed = session.get_token()

        if not allowed:
            print("AuthGuard: access denied")

        return allowed

    async def can_deactivate(self, context) -> bool:
        """
        Allow navigation away from the route
        """
        return True

    async def redirect_to(self, context) -> str | None:
        """
        Route to redirect to if can_activate() returns False
        """
        return "/signin"