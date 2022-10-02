import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
import datetime


class Log(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'logs'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    test_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('tests.id'))
    subtheme_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('subthemes.id'))
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    success = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    resolved = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    user = orm.relationship('User')
    test = orm.relationship('Test')
    subtheme = orm.relationship('Subtheme')
