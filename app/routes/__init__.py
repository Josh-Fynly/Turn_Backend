"""
API routes package.
All routes use FastAPI with comprehensive validation, error handling, and OpenAPI documentation.
"""

from .auth_routes import router as auth_router
from .user_routes import router as user_router
from .gamification_routes import router as gamification_router
from .admin_routes import router as admin_router
from app.api.direct_application import router as direct_application_router
from .project_routes import router as project_router
from .cv_routes import router as cv_router
from .job_routes import router as job_router
from .email_routes import router as email_router
from app.api.demo_simulations import router as demo_router
routers.append(demo_router)
# List of all routers to be included in the main app
routers = [
    auth_router,
    user_router,
    admin_router,
    gamification_router,
    direct_application_router,
    project_router,
    cv_router,
    job_router,
    email_router,
    demo_router,
]

__all__ = [
    "auth_router",
    "user_router",
    "admin_router",
    "project_router",
    "cv_router",
    "job_router",
    "direct_application_router",
    "demo_router",
    "routers"
]
