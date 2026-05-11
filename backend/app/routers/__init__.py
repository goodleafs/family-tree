from app.routers.auth import router as auth_router
from app.routers.family import router as family_router
from app.routers.person import router as person_router
from app.routers.album import router as album_router
from app.routers.document import router as document_router
from app.routers.biography import router as biography_router

__all__ = [
    "auth_router", "family_router", "person_router",
    "album_router", "document_router", "biography_router"
]
