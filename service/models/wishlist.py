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
from sqlalchemy.orm import query
from service.models.product import Product
from service.models.wishlist_product import WishlistProduct
from .model_utils import EntityNotFoundError, db,logger,Availability,DataValidationError

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
      self.name = data['name']
      self.user_id = data['user_id']

    except KeyError as error:
      raise DataValidationError("Invalid Wishlist: missing " + error.args[0])
    except TypeError as error:
      raise DataValidationError("Invalid Wishlist: body of request contained bad or no data")
    return self

  def create(self):
    logger.info("Creating %s ...", self.name)
    self.id = None
    db.session.add(self)
    db.session.commit()

  def update(self):
    logger.info("Updating wishlist %s ...", self.name)
    if not self.id:
      raise DataValidationError("Update called with empty ID field")
    db.session.commit()
  
  def read(self):
    wishlist = Wishlist.find_by_id(self.id)
    if wishlist is None:
      raise EntityNotFoundError("Cannot find wishlist with id %s" % self.id)
    else:
      product_ids = [wp.product_id for wp in WishlistProduct.find_all_by_wishlist_id(self.id)]
      products = []
      if len(product_ids) != 0:
        products = Product.find_all_by_id(product_ids)
      return WishlistVo(self,products).serialize()
  
  def add_items(self,product_ids:list):
    cnt = 0
    for pid in product_ids:
      if WishlistProduct.find_by_wishlist_id_and_product_id(self.id,pid) is None:
        cnt += 1
        WishlistProduct(wishlist_id=self.id,product_id=pid).create()
    return cnt

  def delete_items(self, product_ids:list):
    cnt = 0
    for pid in product_ids:
      entity = WishlistProduct.find_by_wishlist_id_and_product_id(self.id, pid)
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
      logger.info("Wishlist: cannot find this wishlist")
      return 0
    else:
      WishlistProduct.delete_all_by_wishlist_id(self.id)
      logger.info("Deleting wishlist % s" % self.name)
      db.session.delete(self)
      db.session.commit()
      return 1

  @classmethod
  def init_db(cls, app:Flask):
    logger.info("Wishlist: Initializing database")
    cls.app = app

    db.init_app(app)
    app.app_context().push()
    db.create_all()
  
  @classmethod
  def find_all(cls):
    logger.info("Wishlist: processing lookup for all wishlists")
    return cls.query.all()

  @classmethod
  def find_by_id(cls, wishlist_id:int):
    logger.info("Wishlist: processing deletion for id %s ..." % wishlist_id)
    return cls.query.get(wishlist_id)
  
  @classmethod
  def find_all_by_user_id(cls,user_id:int)->list:
    logger.info("Wishlist: porcessing lookup for user id: %s ..." % user_id)
    query_res = cls.query.filter(cls.user_id == user_id)
    if query_res.count() == 0:
      return []
    else:
      wishlists = [r for r in query_res]
      res = []
      for w in wishlists:
        wishlist_products = WishlistProduct.find_all_by_wishlist_id(w.id)
        products = []
        if len(wishlist_products) != 0:
          products = Product.find_all_by_id([wp.product_id for wp in wishlist_products])
        res.append(WishlistVo(w,products))
      
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
            'products':[p.serialize() for p in self.products]
        }