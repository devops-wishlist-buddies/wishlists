from enum import Enum
import logging
import decimal
from flask.json import JSONEncoder
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")
db = SQLAlchemy()

def get_non_null_product_fields():
  """"Returns non-null fields for Product model"""
  return ['name', 'price', 'status','inventory_product_id', 'wishlist_id']

class DataValidationError(ValueError):
  pass

class EntityNotFoundError(KeyError):
  pass

class Availability(Enum):
  AVAILABLE = 1
  UNAVAILABLE = 0

class JsonEncoder(JSONEncoder):
  def default(self, obj):
    if isinstance(obj, decimal.Decimal):
      return float(obj)
    if isinstance(obj, Availability):
      return obj.name
    return JSONEncoder.default(self, obj)
