"""
Models for Wishlists Service

Model
------
wishlist_product - A relational schema between products and wishlists

Attributes:
-----------
TBD

"""

from flask import Flask
from service.models.product import Product
from .model_utils import db,logger,DataValidationError

class WishlistProduct(db.Model):
    __tablename__ = "wishlistProduct"
    
    app:Flask = None

    id = db.Column(db.Integer,primary_key = True)
    product_id = db.Column(db.Integer,db.ForeignKey("product.id"),nullable = False)
    wishlist_id = db.Column(db.Integer,db.ForeignKey("wishlist.id"),nullable=False)

    def create(self):
        logger.info("Creating product with id %s and wishlist with id %s ..." % (self.product_id, self.wishlist_id))
        self.id = None
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        logger.info("Updating tuple (product %s and wishlist %s) ..." % (self.product_id, self.wishlist_id))
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()
    
    def delete(self):
        logger.info("Deleting tuple (product %s and wishlish %s) ..." % (self.product_id, self.wishlist_id))
        db.session.delete(self)
        db.session.commit()

    def serialize(self)->dict:
        return {
            "id":self.id,
            "product_id":self.product_id,
            "wishlist_id":self.wishlist_id
        }

    def deserialize(self,data:dict):
        try:
            if isinstance(data['product_id'], int) and isinstance(data['wishlist_id'], int):
                self.product_id = data['product_id']
                self.wishlist_id = data['wishlist_id']
            else:
                raise DataValidationError("Invalid type for field product_id or wishlist_id, integer expected")
        except KeyError as error:
            raise DataValidationError("Invalid WishlistProduct: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError("Invalud WishlistProduct: body of request contained bad or no data")
        return self

    @classmethod
    def init_db(cls, app:Flask):
        logger.info("WishlistProduct: initializing database")
        cls.app = app

        db.init_app(app)
        app.app_context().push()
        db.create_all()
    
    @classmethod
    def find_all(cls):
        logger.info("WistlistProduct: processing lookup for all wishlist products")
        return cls.query.all()

    @classmethod
    def find_all_by_wishlist_id(cls, wishlist_id:int)->list:
        logger.info("WishlistProduct: processing lookup for wishlist_id %s ..." % wishlist_id)
        res = cls.query.filter(cls.wishlist_id == wishlist_id)
        return [r for r in res]
    
    @classmethod
    def find_by_wishlist_id_and_product_id(cls, wishlist_id:int,product_id:int):
        logger.info("WishlistProduct: processing lookup for wishlist_id: %s and product_id %s ..." % (wishlist_id,product_id))
        res = cls.query.filter(cls.wishlist_id == wishlist_id, cls.product_id == product_id)
        if res.count() == 0:
            return None
        else:
            return res[0]

    @classmethod
    def delete_all_by_wishlist_id_and_product_id(cls, wishlist_id:int, product_ids:list) -> int:
        logger.info("WishlistProduct: processing deletion for wishlist_id %s and product_id in %s ..." % (wishlist_id, product_ids))
        cnt = 0;
        for pid in product_ids:
            entity = WishlistProduct.find_by_wishlist_id_and_product_id(wishlist_id, pid)
            if entity is not None:
                cnt += 1
                entity.delete()
        return cnt

    @classmethod
    def delete_all_by_wishlist_id(cls, wishlist_id:int):
        logger.info("WishlistProduct: processing deletion for wishlist_id %s ..." % wishlist_id)
        entities = WishlistProduct.find_all_by_wishlist_id(wishlist_id)
        cnt = 0
        if len(entities) != 0:
            for entity in entities:
                cnt += 1
                entity.delete()
        return cnt