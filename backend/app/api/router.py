"""Main API router that aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.endpoints import auth, folders, ideas, notes, attachments, prices, earnings, guidance

api_router = APIRouter(prefix="/api")

# Include all routers
api_router.include_router(auth.router)
api_router.include_router(folders.router)
api_router.include_router(ideas.router)
api_router.include_router(notes.router)
api_router.include_router(attachments.router)
api_router.include_router(prices.router)
api_router.include_router(earnings.router)
api_router.include_router(guidance.router)
