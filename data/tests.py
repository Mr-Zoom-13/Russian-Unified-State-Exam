import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class Test(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tests'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, unique=True)
    subthemes = orm.relationship('Subtheme', back_populates="test")
