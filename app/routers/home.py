from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.database import get_db
from app.models.user_model import User
from app.schemas.home_schemas import HomeDashboardResponse
from app.services.home_service import home_service
from password.common.dependencies.auth_dependencies import get_current_user

router = APIRouter(prefix="/home", tags=["home"])


# main endpoint for home screen data

@router.get("/dashboard", response_model=HomeDashboardResponse)
async def get_home_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all data needed for the home screen in one request."""
    return await home_service.get_home_dashboard(current_user, db)