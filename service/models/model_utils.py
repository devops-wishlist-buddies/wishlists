"""
Utility classes and methods to support API Models
"""

from enum import Enum
import logging
import decimal
from flask.json import JSONEncoder
from flask_sqlalchemy import SQLAlchemy

MAX_NAME_LENGTH = 64

logger = logging.getLogger("flask.app")
db = SQLAlchemy()

def get_non_null_product_fields():
  """"Returns non-null fields for Product model"""
  return ['name', 'price', 'status', 'inventory_product_id', 'wishlist_id']

class DataValidationError(ValueError):
  pass

class EntityNotFoundError(KeyError):
  pass

class Availability(Enum):
  """Enumerator denoting possible values of Product availability"""

  AVAILABLE = 1
  UNAVAILABLE = 0

class InCartStatus(Enum):
  """Enumerator denoting possible values of Product in-cart status"""

  ORDERED = 2
  IN_CART = 1
  DEFAULT = 0

class JsonEncoder(JSONEncoder):
  def default(self, obj):
    if isinstance(obj, decimal.Decimal):
      return float(obj)
    if isinstance(obj, Availability):
      return obj.name
    if isinstance(obj, InCartStatus):
      return obj.name
    return JSONEncoder.default(self, obj)

from .wishlist import Wishlist
from .product import Product

def seeds():
  """Populate our database if necessary"""
  logging.info('Creating dummy data')

  w_1 = Wishlist(name = "User 1 first wishlist", user_id = 1)
  w_1.create()
  w_2 = Wishlist(name = "User 1 second wishlist", user_id = 1)
  w_2.create()
  w_3 = Wishlist(name = "User 2 first wishlist", user_id = 2)
  w_3.create()

  p_1 = Product(wishlist_id=w_1.id,name = "toy",price=11.5,status=Availability.AVAILABLE, \
    pic_url="www.toy.com/1.png",short_desc="this is a toy",inventory_product_id=3)
  p_2 = Product(wishlist_id=w_1.id,name = "book",price=20.5,status=Availability.AVAILABLE, \
    pic_url="www.book.com/1.png",short_desc="this is a book",inventory_product_id=4)
  p_3 = Product(wishlist_id=w_1.id,name = "tv",price=1001.5,status=Availability.AVAILABLE,\
    pic_url="www.tv.com/1.png",short_desc="this is a tv",inventory_product_id=15)
  p_4 = Product(wishlist_id=w_1.id,name = "pepsi",price=7.5,status=Availability.AVAILABLE,\
    pic_url="www.drinks.com/pepsi.png",short_desc="this is pepsi coke",inventory_product_id=1)
  p_5 = Product(wishlist_id=w_1.id,name = "bread",price=3.5,status=Availability.AVAILABLE,\
    pic_url="www.bakery.com/1.png",short_desc="this is a bread",inventory_product_id=20)
  p_6 = Product(wishlist_id=w_1.id,name = "soccer",price=23.5,status=Availability.AVAILABLE,\
    pic_url="www.soccer.com/1.png",short_desc="this is a soccer",inventory_product_id=5)
  p_7 = Product(wishlist_id=w_2.id,name = "bread",price=3.5,status=Availability.AVAILABLE,\
    pic_url="www.bakery.com/1.png",short_desc="this is a bread",inventory_product_id=20)
  p_8 = Product(wishlist_id=w_2.id,name = "soccer",price=23.5,status=Availability.AVAILABLE,\
    pic_url="www.soccer.com/1.png",short_desc="this is a soccer",inventory_product_id=5)
  p_9 = Product(wishlist_id=w_2.id,name = "toy",price=11.5,status=Availability.AVAILABLE, \
    pic_url="www.toy.com/1.png",short_desc="this is a toy",inventory_product_id=3)

  products = [p_1,p_2,p_3,p_4,p_5,p_6,p_7,p_8,p_9]
  for product in products:
    product.create()
