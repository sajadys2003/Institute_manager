from app.models import Permission
from app.schemas import PermissionResponse


from .security import CurrentUser, authorized
from inspect import currentframe
from fastapi import APIRouter
from fastapi import HTTPException
from app.dependencies import SessionDep, CommonsDep


router = APIRouter(prefix="/permissions", tags=["permissions"])


async def get_by_id(db: SessionDep, permission_id: int) -> Permission:
    stored_record = db.get(Permission, permission_id)
    if not stored_record:
        raise HTTPException(status_code=404, detail="Not found")
    return stored_record


@router.get("/", response_model=list[PermissionResponse])
async def get_permissions(
        db: SessionDep,
        commons: CommonsDep,
        current_user: CurrentUser

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):

        if q := commons.q:
            criteria = Permission.name.ilike(q)
            stored_records = db.query(Permission).where(criteria)

        else:
            stored_records = db.query(Permission)
        return stored_records.offset(commons.offset).limit(commons.limit).all()


@router.get(path="/{permission_id}", response_model=PermissionResponse)
async def get_permission(
        db: SessionDep,
        permission_id: int,
        current_user: CurrentUser

):
    operation = currentframe().f_code.co_name
    if authorized(current_user, operation):
        stored_record = await get_by_id(db, permission_id)
        return stored_record
