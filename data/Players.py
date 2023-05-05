import datetime
import sqlalchemy as sa
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Player(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "Players"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    login = sa.Column(sa.String(16), nullable=False)
    weap = sa.Column(sa.TupleType, default=None)
    ans = sa.Column(sa.Boolean, default=True)
