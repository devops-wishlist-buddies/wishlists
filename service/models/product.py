"""
Models for Wishlists Service

Model
------
Product - A product used in wishlists on an e-commerce site

Attributes:
-----------
id
name
price
status
pic_url
short_desc
inventory_product_id
wishlist_id
"""

from sqlalchemy import asc
from .model_utils import MAX_NAME_LENGTH, db, logger, \
  Availability, InCartStatus, DataValidationError, get_non_null_product_fields

class Product(db.Model):

  __tablename__= 'product'

  id = db.Column(db.Integer,primary_key = True)
  name = db.Column(db.String(64), nullable=False)
  price = db.Column(db.DECIMAL,nullable=False)
  status = db.Column(db.Enum(Availability),nullable=False,default=Availability.AVAILABLE)
  pic_url = db.Column(db.Text,nullable=True)
  short_desc = db.Column(db.Text,nullable=True)
  # corresponds to real product in inventory
  inventory_product_id = db.Column(db.Integer,nullable=False)
  # wishlist id it belongs to
  wishlist_id = db.Column(db.Integer,db.ForeignKey("wishlist.id"),nullable=False)
  in_cart_status = db.Column(db.Enum(InCartStatus),nullable=False,default=InCartStatus.DEFAULT)

  def create(self):
    """Create Product instance in database"""
    logger.info("Creating %s ...", self.name)
    self.id = None
    self.in_cart_status = InCartStatus.DEFAULT #ensure default value upon creation
    db.session.add(self)
    try:
      db.session.commit()
    except:
      db.session.rollback()

    return self.id

  def update(self):
    """Update Product instance in database"""
    logger.info("Updating %s ...", self.name)
    if not self.id:
      raise DataValidationError("Update called with empty ID field")
    try:
      db.session.commit()
    except:
      db.session.rollback()

  def delete(self):
    """Delete Product instance in database"""
    logger.info("Deleting %s ...", self.name)
    db.session.delete(self)
    try:
      db.session.commit()
    except:
      db.session.rollback()

  def serialize(self) -> dict:
    """serialize a Product into a dictionary"""
    prep_data = {
      "id": self.id,
      "name": self.name,
      "price": self.price,
      "status": self.status.name,
      "pic_url": self.pic_url,
      "short_desc": self.short_desc,
      "inventory_product_id": self.inventory_product_id,
      "wishlist_id": self.wishlist_id,
      "in_cart_status": self.in_cart_status.name,
    }

    return {k: v for k, v in prep_data.items() if v}


  def deserialize(self, data:dict):
    """Deserialize a Product from dictionary"""
    table_keys = Product.__table__.columns.keys()
    non_null_fields = get_non_null_product_fields()
    try:
      for key in data.keys():
        if key not in table_keys:
          raise DataValidationError(
            "Invalid argument {0} with value {1} for Product: ".format(key, data.get(key))
          )

      for non_null_key in non_null_fields:
        if data.get(non_null_key) is None:
          raise DataValidationError("Field {0} cannot be null".format(non_null_key))

      if len(data.get('name')) > MAX_NAME_LENGTH:
        raise AttributeError(f"Name field should be shorter than {MAX_NAME_LENGTH} characters")

      self.name = data.get('name')
      self.price = float(data.get('price'))

      status_candidate = data.get('status')
      if isinstance(status_candidate,Availability) and \
        status_candidate in [Availability.AVAILABLE, Availability.UNAVAILABLE]:
        self.status = status_candidate
      elif isinstance(status_candidate, str):
        if status_candidate == "1" or status_candidate == "0":
          self.status = int(status_candidate)
        else:
          self.status = getattr(Availability, status_candidate.upper())
      elif isinstance(status_candidate, int):
        self.status = Availability(status_candidate)
      else:
        raise DataValidationError(
          "Invalid type for field \'status\', expected 1/0, or available/unavailable"
        )
      self.pic_url = data.get('pic_url')
      self.short_desc = data.get('short_desc')
      self.inventory_product_id = int(data.get('inventory_product_id'))
      self.wishlist_id = int(data.get('wishlist_id'))
    except AttributeError as error:
      logger.error(error)
      raise DataValidationError(error.args[0])
    return self

  @classmethod
  def find_all(cls)->list:
    """ Finds all Products in database """
    logger.info("Products: processing all products")
    return list(cls.query.all())

  @classmethod
  def find_by_id(cls, product_id:int):
    """ Find a Product by its id """
    logger.info('Products: processing product lookup for id %s ...', product_id)
    return cls.query.get(product_id)

  @classmethod
  def find_by_id_and_status(cls, product_id:int, status:Availability):
    """ Find a Product by its id and availability status"""
    logger.info('Products: processing product lookup for id' \
      '%s and status %s ...', product_id, status.value)
    res = list(cls.query.filter(cls.id == product_id, cls.status == status)\
      .order_by(asc(Product.id)))
    if len(res) == 0:
      return None

    return res[0]

  @classmethod
  def find_or_404(cls,product_id:int):
    """ Find a Product by its id. Returns a product or a 404"""
    logger.info("Products: processing lookup or 404 for id %s ...", product_id)
    return cls.query.get_or_404(product_id)

  @classmethod
  def find_all_by_ids(cls, product_ids:list) -> list:
    """Find a product by id"""
    logger.info("Products: processing lookup for ids in %s ...", product_ids)
    res = cls.query.filter(cls.id.in_(product_ids)).order_by(asc(Product.id))
    return list(res)

  @classmethod
  def find_all_by_ids_and_status \
    (cls, product_ids:list, status:Availability=Availability.AVAILABLE) -> list:
    """Find products by id and its status"""
    logger.info("Products: processing lookup for ids in %s and status %s ...",\
      product_ids, status)
    res = cls.query.filter(cls.id.in_(product_ids), cls.status == status).order_by(asc(Product.id))
    return list(res)

  @classmethod
  def find_by_name(cls,name:str)->list:
    """Find a product by its name"""
    logger.info("Products: processing name query for %s ...", name)
    return list(cls.query.filter(cls.name == name).order_by(asc(Product.id)))

  @classmethod
  def find_all_by_wishlist_id(cls,wishlist_id:int)->list:
    """Find products by wishlist id they belong to"""
    logger.info("Products: processing name query for %s ...", wishlist_id)
    return list(cls.query.filter(cls.wishlist_id == wishlist_id).order_by(asc(Product.id)))

  @classmethod
  def find_by_wishlist_id_and_product_id(cls,wishlist_id:int,product_id:int)->list:
    """Find products by wishlist id they belong to and product id"""
    logger.info("Products: processing name query for wishlist %s and product %s...",\
      wishlist_id, product_id)
    res = cls.query.filter(cls.wishlist_id == wishlist_id, cls.id == product_id)\
      .order_by(asc(Product.id))
    if res.count() == 0:
      return None

    return res[0]

  @classmethod
  def delete_by_wishlist_id_and_product_id(cls, wishlist_id:int, pid:int) -> int:
    """Delete products by wishlist id they belong to and product id"""
    logger.info("Products: processing deletion for wishlist_id %s"\
      "and product_id %s ...", wishlist_id, pid)
    entity = Product.find_by_wishlist_id_and_product_id(wishlist_id, pid)
    if entity is not None:
      entity.delete()

  @classmethod
  def delete_all_by_wishlist_id(cls, wishlist_id:int):
    """Delete all products by wishlist id they belong to"""
    logger.info("Product: processing deletion for wishlist_id %s ...", wishlist_id)
    entities = Product.find_all_by_wishlist_id(wishlist_id)
    cnt = 0
    if len(entities) != 0:
      for entity in entities:
        cnt += 1
        entity.delete()
    return cnt
