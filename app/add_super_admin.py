from sqlalchemy.orm import Session
from app.dependencies import engine
from app.models import User
from datetime import datetime
from app.routers.security import pwd_context
from app.routers import roles

def add_super_admin():
    with Session(engine) as db:
        super_admin = User(first_name="super",
                           last_name="admin",
                           father_name="dad",
                           gender="male",
                           date_of_birth=datetime(2020, 11, 2),
                           national_code="7777",
                           phone_number="1234",
                           recruitment_date=datetime.now(),
                           password=pwd_context.hash("password"),
                           is_super_admin=True,
                           is_panel_user=True,
                           record_date=datetime.now())
        db.add(super_admin)
        db.commit()

# add_super_admin()
def add_permissions():
    permissions = ["get_all_roles", "get_role_by_id", "create_role", "update_role", "delete_role",
                   "get_all_permissions", "get_permission_by_id", "create_permission",
                   "update_permission", "delete_permission"]



print(list(filter(lambda st: "role" in st, dir(roles))))







