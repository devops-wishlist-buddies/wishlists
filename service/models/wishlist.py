"""
Models for Wishlists Service

Model
------
Wishlist - A wishlist used in an e-commerce site

Attributes:
-----------
TBD

"""

from flask import Flask
from .model_utils import db,logger,Availability,DataValidationError

class Wishlist(db.Model):
  __tableName__ = 'wishlist'

  app:Flask = None

  id = db.Column(db.Integer,primary_key = True)
  name = db.Column(db.String(255), nullable = False)
  status = db.Column(db.Enum(Availability), nullable = True, default = 1)

  def create():
    pass
  
  def add_items():
    pass

  def delete_items():
    pass

  def read():
    pass
  
  def delete():
    pass

  def serialize():
    pass

  def deserialize():
    pass