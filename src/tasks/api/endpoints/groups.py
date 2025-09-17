from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from tasks.api.deps import get_db, require_roles
from tasks.api.schemas.group import GroupCreateIn, GroupOut
from tasks.core.enums import UserRole
from tasks.db.crud.group import group_crud
from tasks.db.crud.user import user_crud

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=GroupOut)
async def create_group(
    payload: GroupCreateIn,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_roles(UserRole.admin, UserRole.teacher)),
):
    manager = None
    teacher = None

    if payload.manager_id is not None:
        manager = await user_crud.get_by_id(db, payload.manager_id)
        if not manager:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if payload.teacher_id is not None:
        teacher = await user_crud.get_by_id(db, payload.teacher_id)
        if not teacher or teacher.role != UserRole.teacher:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="teacher_id must belong to user with role=teacher",
            )

    try:
        group = await group_crud.create(db, payload.name, manager, teacher)
    except ValueError as e:
        if str(e) == "group_name_exists":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="group_name_exists",
            )
        raise

    return GroupOut(
        id=group.id,
        name=group.name,
        manager_id=group.manager_id,
        teacher_id=group.teacher_id,
        students=[s.id for s in group.students],
    )


@router.get("/", response_model=list[GroupOut])
async def list_groups(db: AsyncSession = Depends(get_db)):
    items = await group_crud.list_groups(db)
    return [
        GroupOut(
            id=g.id,
            name=g.name,
            manager_id=g.manager_id,
            teacher_id=g.teacher_id,
            students=[s.id for s in g.students],
        )
        for g in items
    ]


@router.get("/{group_id}", response_model=GroupOut)
async def group_detail(group_id: int, db: AsyncSession = Depends(get_db)):
    g = await group_crud.get(db, group_id)
    if g is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return GroupOut(
        id=g.id,
        name=g.name,
        manager_id=g.manager_id,
        teacher_id=g.teacher_id,
        students=[s.id for s in g.students],
    )


@router.post("/{group_id}/add_student", response_model=GroupOut)
async def add_student(
    group_id: int,
    student_id: int,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_roles(UserRole.admin, UserRole.teacher)),
):
    g = await group_crud.get(db, group_id)
    if not g:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    s = await user_crud.get_by_id(db, student_id)
    if not s:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    g = await group_crud.add_student(db, g, s)
    return GroupOut(
        id=g.id,
        name=g.name,
        manager_id=g.manager_id,
        teacher_id=g.teacher_id,
        students=[x.id for x in g.students],
    )
