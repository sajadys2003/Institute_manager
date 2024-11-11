from inspect import currentframe

from app.models import User
from sqlalchemy import select
from app.schemas import UserOut
from app.dependencies import SessionDep


def Hello():
    h = currentframe().f_code.co_name
    return print(h)


Hello()
