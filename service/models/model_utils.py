from enum import Enum
import logging
import decimal
from sqlalchemy import asc
from flask.json import JSONEncoder
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")
db = SQLAlchemy()

class DataValidationError(ValueError):
    pass

class EntityNotFoundError(KeyError):
  pass

class Availability(Enum):
  Available = 1
  Unavailable = 0

class JsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, Availability):
            return obj.name
        return JSONEncoder.default(self, obj)