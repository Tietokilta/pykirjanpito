import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
from decimal import Decimal
from database import Base, db

class Event(Base):
    __tablename__ = 'event'
    id = sa.Column(sa.Integer, sa.Sequence('user_id_seq'), primary_key=True)
    name = sa.Column(sa.String(255))
    regular_expression = sa.Column(sa.String(255))
    keyword = sa.Column(sa.String(255))
    price = sa.Column(sa.Numeric(15,2))
    

class Order(Base):
    __tablename__ = 'order'
    id = sa.Column(sa.Integer, sa.Sequence('user_id_seq'), primary_key=True)
    name = sa.Column(sa.String(255))
    email = sa.Column(sa.String(255))
    is_paid = sa.Column(sa.Boolean)
    paid_date = sa.Column(sa.Date)
    payment = sa.Column(sa.Numeric(16,2))
    requested_payment = sa.Column(sa.Numeric(16,2))
    comments = sa.Column(sa.Text)
    event_id = sa.Column(sa.Integer, sa.ForeignKey(Event.id))
    last_checked = sa.Column(sa.DateTime)
    event = relationship(Event, backref="orders", order_by=name)

    """
    @staticmethod
    def query(x):
        return db.session.query(x)
    """