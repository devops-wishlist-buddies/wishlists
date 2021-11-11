"""
Test cases for Product Model
Test cases can be run with:
    nosetests
    coverage report -m
While debugging just these tests it's convinient to use this:
    nosetests --stop tests/test_Products.py:TestProductModel
"""

import os
import json
import logging
import unittest
from werkzeug.exceptions import NotFound
from service.models.model_utils import Availability, DataValidationError, db
from service.models.product import Product
from service.models.wishlist import Wishlist
from service import app
from .factories import ProductFactory, WishlistFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.environ['VCAP_SERVICES'])
    DATABASE_URI = vcap['user-provided'][0]['credentials']['url']

######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
class TestProductModel(unittest.TestCase):
  """Test Cases for Product Model"""

  @classmethod
  def setUpClass(cls):
    """This runs once before the entire test suite"""
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.logger.setLevel(logging.CRITICAL)
    Product.init_db(app)
    Wishlist.init_db(app)

  @classmethod
  def tearDownClass(cls):
    """This runs once after the entire test suite"""
    db.session.close()

  def setUp(self):
    """This runs before each test"""
    db.drop_all()  # clean up the last tests
    db.create_all()  # make our sqlalchemy tables

    w_instances = WishlistFactory.create_batch(2)
    w_instances[0].create()
    w_instances[1].create()

    self.w_1 = w_instances[0]
    self.w_2 = w_instances[1]

  def tearDown(self):
    """This runs after each test"""
    db.session.remove()
    db.drop_all()

    self.w_1 = None
    self.w_2 = None

  ######################################################################
  #  T E S T   C A S E S
  ######################################################################

  def test_create_a_product(self):
    """Create a Product locally and assert the constructor works"""
    product_instance = Product(wishlist_id =1, name="book",price=12.5,\
      status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test", inventory_product_id=4)
    self.assertTrue(product_instance is not None)
    self.assertEqual(product_instance.id, None)
    self.assertEqual(product_instance.name, "book")
    self.assertEqual(product_instance.price, 12.5)
    self.assertEqual(product_instance.status, Availability.AVAILABLE)
    self.assertEqual(product_instance.pic_url, "www.google.com")
    self.assertEqual(product_instance.short_desc, "this is a test")
    self.assertEqual(product_instance.wishlist_id, 1)
    product_instance = Product(wishlist_id =1, name="book",price=12.5,\
      status=Availability.UNAVAILABLE,pic_url="www.google.com",short_desc="this is a test", inventory_product_id=4)
    self.assertEqual(product_instance.status, Availability.UNAVAILABLE)

  def test_add_a_product(self):
    """Create a Product and add it to the database"""
    products = Product.find_all()
    self.assertEqual(products, [])

    product_instance = Product(wishlist_id=self.w_1.id, name="book",price=12.5,\
      status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test",inventory_product_id=4)
    self.assertTrue(product_instance is not None)
    self.assertEqual(product_instance.id, None)
    product_instance.create()

    # Asert that it was assigned an id and shows up in the database
    self.assertEqual(product_instance.id, 1)
    products = Product.find_all()
    self.assertEqual(len(products), 1)
    self.assertEqual(products[0].price, 12.5)

  def test_update_a_product(self):
    """Update a Product"""

    product_instance = ProductFactory()
    product_instance.wishlist_id = self.w_1.id
    product_instance.id = None
    product_instance.create()
    self.assertEqual(product_instance.id, 1)

    # Change it an save it
    product_instance.name = "toy"
    original_id = product_instance.id
    product_instance.update()
    self.assertEqual(product_instance.id, original_id)
    self.assertEqual(product_instance.name, "toy")

    # Fetch it back and make sure the id hasn't changed
    # but the data did change
    products = Product.find_all()
    self.assertEqual(len(products), 1)
    self.assertEqual(products[0].id, 1)
    self.assertEqual(products[0].name, "toy")

    product_instance.id = None
    self.assertRaises(DataValidationError, product_instance.update)

  def test_delete_a_product(self):
    """Delete a Product"""
    product_instance = ProductFactory()
    product_instance.wishlist_id = self.w_1.id
    product_instance.create()
    self.assertEqual(len(Product.find_all()), 1)
    # delete the Product and make sure it isn't in the database
    product_instance.delete()
    self.assertEqual(len(Product.find_all()), 0)

  def test_delete_all_products_by_wishlist_id(self):
    """Delete all products that belong to wishlist_id"""
    products = ProductFactory.create_batch(5)
    for product in products:
      product.wishlist_id = self.w_1.id
      product.create()

    self.assertEqual(len(Product.find_all()), 5)
    self.assertEqual(len(Product.find_all_by_wishlist_id(self.w_1.id)), 5)
    Product.delete_all_by_wishlist_id(self.w_1.id)

    self.assertEqual(len(Product.find_all_by_wishlist_id(self.w_1.id)), 0)

  def test_delete_by_wishlist_id_and_product_id(self):
    """Delete a product with product_id that belong to wishlist_id"""
    products = ProductFactory.create_batch(3)
    for product in products:
      product.wishlist_id = self.w_1.id
      product.create()

    self.assertEqual(len(Product.find_all_by_wishlist_id(self.w_1.id)), 3)
    Product.delete_by_wishlist_id_and_product_id(self.w_1.id, products[0].id)

    self.assertEqual(len(Product.find_all_by_wishlist_id(self.w_1.id)), 2)
    self.assertEqual(Product.find_by_id(products[0].id), None)

  def test_serialize_a_product(self):
    """Test serialization of a Product"""
    product_instance = ProductFactory()
    data = product_instance.serialize()
    self.assertNotEqual(data, None)
    self.assertIn("id", data)
    self.assertEqual(data["id"], product_instance.id)
    self.assertIn("name", data)
    self.assertEqual(data["name"], product_instance.name)
    self.assertIn("status", data)
    self.assertEqual(data["status"], product_instance.status)
    self.assertIn("price", data)
    self.assertEqual(data["price"], product_instance.price)
    self.assertIn("pic_url", data)
    self.assertEqual(data["pic_url"], product_instance.pic_url)
    self.assertIn("short_desc", data)
    self.assertEqual(data["short_desc"], product_instance.short_desc)
    self.assertIn("inventory_product_id", data)
    self.assertEqual(data["inventory_product_id"], product_instance.inventory_product_id)

  def test_deserialize_a_product(self):
    """Test deserialization of a Product"""
    data = {
      'id': 1,
      'name': "piggy",
      'price': 100.5,
      'status': Availability.UNAVAILABLE,
      'pic_url': "www.piggy.com/1.png",
      'short_desc': "this is a piggy",
      'wishlist_id': 5,
      'inventory_product_id': 315
    }
    product_instance = Product()
    product_instance.deserialize(data)
    self.assertNotEqual(product_instance, None)
    self.assertEqual(product_instance.id, None)
    self.assertEqual(product_instance.name, "piggy")
    self.assertEqual(product_instance.status, Availability.UNAVAILABLE)
    self.assertEqual(product_instance.price, 100.5)
    self.assertEqual(product_instance.pic_url, "www.piggy.com/1.png")
    self.assertEqual(product_instance.short_desc,"this is a piggy")
    self.assertEqual(product_instance.wishlist_id,5)
    self.assertEqual(product_instance.inventory_product_id,315)

  def test_deserialize_missing_data(self):
    """Test deserialization of a Product with missing data"""
    data = {"id": 1, "name": "kitty", "status": Availability.UNAVAILABLE}
    product_instance = Product()
    self.assertRaises(DataValidationError, product_instance.deserialize, data)

  def test_deserialize_bad_data(self):
    """Test deserialization of bad data"""
    data = "this is not a dictionary"
    product_instance = Product()
    self.assertRaises(DataValidationError, product_instance.deserialize, data)

  def test_deserialize_bad_status(self):
    """ Test deserialization of bad available attribute """
    test_product = ProductFactory()
    data = test_product.serialize()
    data["status"] = 1
    product_instance = Product()
    self.assertRaises(DataValidationError, product_instance.deserialize, data)

  def test_find_product(self):
    """Find a Product by ID"""
    products = ProductFactory.create_batch(3)
    wishlist_ids = [self.w_1.id, self.w_1.id, self.w_2.id]
    for product_instance, w_id in zip(products, wishlist_ids):
      product_instance.wishlist_id = w_id
      product_instance.create()
    logging.debug(products)
    # make sure they got saved
    self.assertEqual(len(Product.find_all()), 3)
    # find the 2nd Product in the list
    product_instance = Product.find_by_id(products[1].id)
    self.assertIsNot(product_instance, None)
    self.assertEqual(product_instance.id, products[1].id)
    self.assertEqual(product_instance.name, products[1].name)
    self.assertEqual(product_instance.status, products[1].status)
    self.assertEqual(product_instance.wishlist_id, wishlist_ids[1])


  def test_find_all_by_ids(self):
    """Find products by ids list"""

    Product(wishlist_id=self.w_1.id, name="toy", status=Availability.AVAILABLE,\
      price = 12.5, pic_url="www.toy.com/1.png", short_desc = "this is a toy",inventory_product_id=3).create()
    Product(wishlist_id=self.w_1.id,name="book", status=Availability.AVAILABLE,\
      price=13.5, pic_url="www.book.com/1.png", short_desc = "this is a book",inventory_product_id=4).create()
    Product(wishlist_id=self.w_2.id,name="table", status=Availability.UNAVAILABLE,\
      price=103.5, pic_url="www.table.com/1.png", short_desc = "this is a table",inventory_product_id=12).create()
    products = Product.find_all_by_ids([1,2,3])
    self.assertEqual(len(products),3)
    self.assertEqual(products[1].name, "book")
    self.assertEqual(products[1].price, 13.5)
    self.assertEqual(products[1].status, Availability.AVAILABLE)
    self.assertEqual(products[0].name, "toy")
    self.assertEqual(products[2].wishlist_id, self.w_2.id)


  def test_find_all_by_ids_and_status(self):
    """Find products by ids list and status"""
    Product(wishlist_id=self.w_1.id,name="toy", status=Availability.AVAILABLE, price = 12.5,\
      pic_url="www.toy.com/1.png", short_desc = "this is a toy",inventory_product_id=3).create()
    Product(wishlist_id=self.w_1.id,name="book", status=Availability.AVAILABLE, price=13.5,\
      pic_url="www.book.com/1.png", short_desc = "this is a book",inventory_product_id=4).create()
    Product(wishlist_id=self.w_1.id,name="table", status=Availability.UNAVAILABLE, price=103.5,\
      pic_url="www.table.com/1.png", short_desc = "this is a table",inventory_product_id=12).create()

    products = Product.find_all_by_ids_and_status([1,2,3],Availability.AVAILABLE)
    self.assertEqual(len(products),2)
    self.assertEqual(products[1].name, "book")
    self.assertEqual(products[1].price, 13.5)
    self.assertEqual(products[1].status, Availability.AVAILABLE)

  def test_find_by_id_and_status(self):
    """Find product by id and status"""
    Product(wishlist_id=self.w_1.id,name="toy", status=Availability.AVAILABLE, price = 12.5,\
      pic_url="www.toy.com/1.png", short_desc = "this is a toy",inventory_product_id=3).create()
    Product(wishlist_id=self.w_1.id,name="book", status=Availability.AVAILABLE, price=13.5,\
      pic_url="www.book.com/1.png", short_desc = "this is a book",inventory_product_id=4).create()
    Product(wishlist_id=self.w_1.id,name="table", status=Availability.UNAVAILABLE, price=103.5,\
      pic_url="www.table.com/1.png", short_desc = "this is a table",inventory_product_id=12).create()

    product_instance = Product.find_by_id_and_status(2,Availability.AVAILABLE)
    self.assertIsNotNone(product_instance)
    self.assertEqual(product_instance.name,"book")
    self.assertEqual(product_instance.price,13.5)
    self.assertEqual(product_instance.status,Availability.AVAILABLE)
    self.assertEqual(product_instance.inventory_product_id,4)

    product_instance = Product.find_by_id_and_status(1,Availability.UNAVAILABLE)
    self.assertIsNone(product_instance)

  def test_find_or_404_not_found(self):
    """Find or return 404 not found"""
    products = ProductFactory.create_batch(3)
    for product in products:
      product.wishlist_id = self.w_1.id
      product.create()

    product = Product.find_or_404(products[1].id)
    self.assertIsNot(product, None)
    self.assertEqual(product.id, products[1].id)
    self.assertEqual(product.name, products[1].name)
    self.assertEqual(product.status, products[1].status)

    self.assertRaises(NotFound, Product.find_or_404, 17)

  def test_find_by_name(self):
    """Find a product by its name"""
    Product(wishlist_id = self.w_1.id,name="toy", status=Availability.AVAILABLE, price = 12.5,\
      pic_url="www.toy.com/1.png", short_desc = "this is a toy",inventory_product_id=3).create()
    Product(wishlist_id = self.w_1.id,name="toy", status=Availability.AVAILABLE, price = 22.5,\
      pic_url="www.toy.com/2.png", short_desc = "this is another toy",inventory_product_id=10).create()
    Product(wishlist_id = self.w_1.id,name="book", status=Availability.AVAILABLE, price=13.5,\
      pic_url="www.book.com/1.png", short_desc = "this is a book",inventory_product_id=4).create()
    Product(wishlist_id = self.w_2.id,name="table", status=Availability.UNAVAILABLE, price=103.5,\
      pic_url="www.table.com/1.png", short_desc = "this is a table",inventory_product_id=12).create()

    self.assertEqual(len(Product.find_by_name("book")),1)
    self.assertEqual(len(Product.find_by_name("toy")),2)
