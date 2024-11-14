from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


# class Country(Base):
#     __tablename__ = "countries"
#
#     id: Mapped[int] = mapped_column(primary_key=True, unique=True)
#     name: Mapped[str] = mapped_column(unique=True)
#
#     people: Mapped[list["Person"]] = relationship(
#         back_populates="country",
#         passive_deletes="all"
#     )
#
#     def __repr__(self):
#         return f"Country(id={self.id}, name={self.name})"
#
#
# class Person(Base):
#     __tablename__ = "people"
#
#     id: Mapped[int] = mapped_column(primary_key=True, unique=True)
#     name: Mapped[str] = mapped_column(unique=True)
#     country_id = mapped_column(ForeignKey("countries.id"))
#
#     country: Mapped["Country"] = relationship(
#         back_populates="people",
#     )
#
#     def __repr__(self):
#         return f"Person(id={self.id}, name={self.name}, country_id={self.country_id})"

class Test2(Base):
    __tablename__ = "test2s"

    a: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    b: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    c: Mapped[int] = mapped_column(primary_key=True, nullable=False)

    def __repr__(self):
        return f"Test2(a={self.a}, b={self.b})"

url = "postgresql+psycopg://postgres:password@localhost:5432/rel"
engine = create_engine(url)

Base.metadata.create_all(bind=engine)

with Session(engine) as db:
    try:
        r1 = Test2(a=1, b=1, c=1)
        got = db.query(Test2).where(Test2.b == 1 or False)
        print(got.all())
        # db.add(r1)
        # db.commit()
    except IntegrityError as e:
        print(e.args)