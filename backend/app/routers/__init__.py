from app.routers.auth import router as auth_router
from app.routers.family import router as family_router
from app.routers.person import router as person_router

__all__ = ["auth_router", "family_router", "person_router"]
