from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db


class Users(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def __repr__(self):
        return '<User {}>'.format(self.username)


# define the database model
class Fystboll(db.Model):
    pallet: so.Mapped[str] = so.mapped_column(sa.String(10))
    item_code: so.Mapped[str] = so.mapped_column(sa.String(10))
    item_description: so.Mapped[str] = so.mapped_column(sa.String(50))
    width: so.Mapped[str] = so.mapped_column(sa.String(10))
    length: so.Mapped[str] = so.mapped_column(sa.String(10))
    quantity: so.Mapped[str] = so.mapped_column(sa.String(10))
    coil: so.Mapped[str] = so.mapped_column(sa.String(10), primary_key=True)
    customer: so.Mapped[str] = so.mapped_column(sa.String(10))
    customer_firm_name: so.Mapped[str] = so.mapped_column(sa.String(50))
    date: so.Mapped[str] = so.mapped_column(sa.String(12))
    doc_number: so.Mapped[str] = so.mapped_column(sa.String(15))
    ord_number: so.Mapped[str] = so.mapped_column(sa.String(10))
    ord_date: so.Mapped[str] = so.mapped_column(sa.String(12))
    # Id = db.Column(db.Integer)
    # Pallet = db.Column(db.String(10)) # Adjust length as needed
    # Item_code = db.Column(db.String(10))
    # Item_description = db.Column(db.String(50))
    # Width = db.Column(db.String(10))
    # Length = db.Column(db.String(10))
    # Quantity = db.Column(db.String(10))
    # Coil = db.Column(db.String(10), primary_key=True)
    # Customer = db.Column(db.String(10))
    # Customer_firm_name = db.Column(db.String(50))
    # Date = db.Column(db.String(12))
    # Doc_number = db.Column(db.String(15))
    # Ord_number = db.Column(db.String(10))
    # Ord_date = db.Column(db.String(12))

    def __repr__(self):
        return f'<Fystboll {self.id}>'