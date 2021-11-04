"""
Models for Wishlists Service

Model
------
Wishlist - A wishlist used in an e-commerce site

Attributes:
-----------
id
user_id
name

"""

from flask import Flask
from sqlalchemy import asc

from service.models.product import Product
from service.models.model_utils import EntityNotFoundError, db,logger,DataValidationError

class Wishlist(db.Model):
  __tablename__ = 'wishlist'

  app:Flask = None

  id = db.Column(db.Integer,primary_key = True)
  name = db.Column(db.String(64), nullable=False)
  user_id = db.Column(db.Integer, nullable=False)

  def serialize(self)->dict:
    return {
      'id':self.id,
      'user_id':self.user_id,
      'name':self.name,
    }

  def deserialize(self,data):
    try:
      if isinstance(data['name'],str) and isinstance(data['user_id'],int):
        self.name = data['name']
        self.user_id = data['user_id']
      else:
        raise TypeError("Invalid type of name or user_id, string" \
          "expected for name and integer expected for user_id")
    except KeyError as error:
      raise DataValidationError("Invalid Wishlist: missing " + error.args[0])
    except TypeError as error:
      raise DataValidationError(error.args[0])
    return self

  def create(self):
    logger.info("Creating %s ...", self.name)
    self.id = None
    db.session.add(self)
    db.session.commit()
    return self.id

  def update(self):
    logger.info("Updating wishlist %s ...", self.name)
    if not self.id:
      raise DataValidationError("Update called with empty ID field")
    db.session.commit()

  def read(self):
    logger.info("Wishlist: reading content from wishlist with id %s ...", self.id)
    wishlist = Wishlist.find_by_id(self.id)
    if wishlist is None:
      raise EntityNotFoundError("Cannot find wishlist with id {}".format(self.id))

    products = Product.find_all_by_wishlist_id(self.id)
    return WishlistVo(self,products).serialize()

  def add_products(self,product_ids:list):
    logger.info("Wishlist: adding products to wishlist with id %s. products are %s ...",\
      self.id, product_ids)
    cnt = 0
    for pid in product_ids:
      if Product.find_by_wishlist_id_and_product_id(self.id,pid) is None:
        cnt += 1
        Product(wishlist_id=self.id).create()
    return cnt

  def delete_products(self, product_ids:list):
    logger.info("Wishlist: deleting products from wishlist with id %s. products are %s ...",\
      self.id,product_ids)
    cnt = 0
    for pid in product_ids:
      entity = Product.find_by_wishlist_id_and_product_id(self.id, pid)
      if entity is not None:
        cnt += 1
        entity.delete()
    return cnt

  def delete(self):
    if self.id is None:
      logger.info("Wishlist: delete a wishlist with id None")
      return 0

    wishlist = Wishlist.find_by_id(self.id)
    if wishlist is None:
      logger.info("Wishlist: cannot find wishlist with id %s ...", self.id)
      return 0

    Product.delete_all_by_wishlist_id(self.id)
    logger.info("Deleting wishlist %s", self.name)
    db.session.delete(self)
    db.session.commit()
    return 1

  @classmethod
  def init_db(cls, app:Flask):
    logger.info("Wishlist: Initializing database")
    cls.app = app

    db.init_app(app)
    with app.app_context():
      db.drop_all()
      db.create_all()

  @classmethod
  def find_all(cls):
    logger.info("Wishlist: processing lookup for all wishlists")
    return cls.query.all()

  @classmethod
  def find_by_id(cls, wishlist_id:int):
    logger.info("Wishlist: processing deletion for id %s ...", wishlist_id)
    return cls.query.get(wishlist_id)

  @classmethod
  def find_all_by_user_id(cls,user_id:int)->list:
    logger.info("Wishlist: porcessing lookup for user id: %s ...",\
      user_id)
    query_res = cls.query.filter(cls.user_id == user_id).order_by(asc(Wishlist.id))
    if query_res.count() == 0:
      return []

    wishlists = [r for r in query_res]
    res = []
    for wishlist in wishlists:
      wishlist_products = Product.find_all_by_wishlist_id(wishlist.id)
      res.append(WishlistVo(wishlist,wishlist_products))

    return [vo.serialize() for vo in res]

class WishlistVo:
  def __init__(self,wishlist:Wishlist,products:list) -> None:
    self.id = wishlist.id
    self.name = wishlist.name
    self.user_id = wishlist.user_id
    self.products = products

  def serialize(self)->dict:
    return {
      'id': self.id,
      'name':self.name,
      'user_id': self.user_id,
      'products':[p.serialize() for p in self.products]
    }
