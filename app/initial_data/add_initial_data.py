from sqlalchemy.orm import Session
from app.models import engine, User, Permission
import csv
import json


def get_super_admin() -> User:
    with open("super_admin.json", "r") as mf:
        return User(**json.load(mf))


def add_super_admin():
    with Session(engine) as db:
        super_admin = get_super_admin()
        db.add(super_admin)
        db.commit()


def get_permissions() -> list[Permission]:
    with open("permissions.csv", "r") as mf:
        csvreader = csv.reader(mf, delimiter=" ")

        return [Permission(name=p) for line in csvreader for p in line]


def test():
    with open("permissions.csv", "r") as mf:
        csvreader = csv.reader(mf, delimiter=" ")
        # ps = json.dumps([{"id": 1, "name": p} for line in csvreader for p in line])

        ls = []
        permission_id = 1
        parent_id = 1
        for category in csvreader:

            for permission in category:
                ls.append({"id": permission_id, "name": permission, "parent_id": parent_id})
                permission_id += 1
            parent_id += 1
        for i in ls:
            print(i)

    with open("permissions.json", "w") as mf:
        ls = json.dumps(ls)
        mf.write(ls)


test()


def add_permissions():
    with Session(engine) as db:
        permissions = get_permissions()
        db.add_all(permissions)
        db.commit()

# add_super_admin()
# add_permissions()
