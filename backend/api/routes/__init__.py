"""API route modules."""

from .health import router as health_router
from .financial import router as financial_router
from .personal import router as personal_router
from .feed import router as feed_router
from .onboarding import router as onboarding_router
from .learning import router as learning_router
from .admin import router as admin_router

__all__ = [
    "health_router",
    "financial_router",
    "personal_router",
    "feed_router",
    "onboarding_router",
    "learning_router",
    "admin_router"
]

