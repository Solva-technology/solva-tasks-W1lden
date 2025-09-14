from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from tasks.api.schemas.user import UserOut
from tasks.api.deps import get_current_user, get_db, require_roles
from tasks.core.enums import UserRole
from tasks.db.crud.user import user_crud

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
async def me(current=Depends(get_current_user)):
    return current

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db), _: object = Depends(require_roles(UserRole.admin, UserRole.teacher))):
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user
