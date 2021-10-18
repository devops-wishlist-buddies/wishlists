"""
Models for Wishlists Service

Model
------
Product - A product used in wishlists on an e-commerce site

Attributes:
-----------
TBD

"""

from flask import Flask
from .model_utils import db,logger,Availability,DataValidationError

class Product(db.Model):

  __tablename__= 'product'

  app:Flask = None

  id = db.Column(db.Integer,primary_key = True)
  name = db.Column(db.String(64), nullable=False)
  price = db.Column(db.DECIMAL,nullable=False)
  status = db.Column(db.Enum(Availability),nullable=False,default=1)
  pic_url = db.Column(db.Text,nullable=True)
  short_desc = db.Column(db.Text,nullable=True)
  
  def create(self):
    logger.info("Creating %s ...", self.name)
    self.id = None
    db.session.add(self)
    db.session.commit()

  def update(self):
    logger.info("Updating %s ...", self.name)
    if not self.id:
      raise DataValidationError("Update called with empty ID field")
    db.session.commit()
  
  def delete(self):
    logger.info("Deleting %s ...", self.name)
    db.session.delete(self)
    db.session.commit()

  def serialize(self) -> dict:
    """serialize a Product into a dictionary"""
    return {
      "id":self.id,
      "name":self.name,
      "price":self.price,
      "status":self.status,
      "pic_url":self.pic_url,
      "short_desc":self.short_desc
    }

  def deserialize(self, data:dict):
    try:
      self.name = data['name']
      self.price = data['price']
      if isinstance(data["status"],Availability) and data['status'] in [Availability.Available, Availability.Unavailable]:
        self.status = data['status']
      else:
        raise DataValidationError("Invalid type for field status, integer expected")
      self.pic_url = data['pic_url']
      self.short_desc = data['short_desc']

    except KeyError as error:
      raise DataValidationError("Invalid Product: missing " + error.args[0])
    except TypeError as error:
      raise DataValidationError("Invalud Product: body of request contained bad or no data")
    return self
  
  @classmethod
  def init_db(cls, app:Flask):
    logger.info("Product: initializing database")
    cls.app = app

    db.init_app(app)
    app.app_context().push()
    db.create_all()

  @classmethod
  def find_all(cls)->list:
    logger.info("Products: processing all products")
    return cls.query.all()

  @classmethod
  def find_by_id(cls, product_id:int):
    """ Find a Product by it's id """
    logger.info('Products: processing product lookup for id %s ...', product_id)
    return cls.query.get(product_id)

  @classmethod
  def find_by_id_and_status(cls, product_id:int, status:Availability):
    logger.info('Products: processing product lookup for id %s and status %s ...' % (product_id, status))
    res = [r for r in cls.query.filter(cls.id == product_id, cls.status == status)]
    if len(res) == 0:
      return None
    else:
      return res[0]

  @classmethod
  def find_or_404(cls,product_id:int):
    logger.info("Products: processing lookup or 404 for id %s ...", product_id)
    return cls.query.get_or_404(product_id)

  @classmethod
  def find_all_by_id(cls, product_ids:list) -> list:
    """Find a product by id and its status"""
    logger.info("Products: processing lookup for ids in %s ...", product_ids)
    res = cls.query.filter(cls.id.in_(product_ids))
    return [r for r in res]
  
  @classmethod
  def find_all_by_id_and_status(cls, product_ids:list, status:Availability=Availability.Available) -> list:
    """Find products by id and its status"""
    logger.info("Products: processing lookup for ids in %s and status %s ...", product_ids, status)
    res = cls.query.filter(cls.id.in_(product_ids), cls.status == status)
    return [r for r in res]
  
  @classmethod
  def find_by_name(cls,name:str)->list:
    """Find a product by its name"""
    logger.info("Products: processing name query for %s ...", name)
    return cls.query.filter(cls.name == name)