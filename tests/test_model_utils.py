"""Test for utility functions used by models"""
from decimal import Decimal
import unittest
import logging
import os
import json

from service.models.model_utils import Availability, JsonEncoder, db, init_db, seeds
from service.models.product import Product
from service.models.wishlist import Wishlist
from service import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.environ['VCAP_SERVICES'])
    DATABASE_URI = vcap['user-provided'][0]['credentials']['url']

class TestModelUtils(unittest.TestCase):
  """Test for utility functions used by models"""

  @classmethod
  def setUpClass(cls):
    """This runs once before the entire test suite"""
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.logger.setLevel(logging.CRITICAL)
    init_db(app)

  @classmethod
  def tearDownClass(cls):
    """This runs once after the entire test suite"""
    db.session.close()

  def setUp(self):
    """This runs before each test"""
    db.drop_all()  # clean up the last tests
    db.create_all()  # make our sqlalchemy tables

  def tearDown(self):
    """This runs after each test"""
    db.session.remove()
    db.drop_all()

  def test_json_serialize(self):
    """Test for custom json serializer"""
    encoder = JsonEncoder()
    self.assertEqual(encoder.default(Availability.AVAILABLE),Availability.AVAILABLE.name)
    dec = Decimal(200.2)
    self.assertEqual(encoder.default(dec),200.2)

  def test_seeds(self):
    seeds()

    self.assertEqual(len(Wishlist.find_all()),3)
    self.assertEqual(len(Product.find_all()),9)

    w_1 = Wishlist.find_by_id(1)
    self.assertIsNotNone(w_1)
    self.assertEqual(w_1.name, "User 1 first wishlist")

    p_3 = Product.find_by_id(3)
    self.assertIsNotNone(p_3)
    self.assertEqual(p_3.wishlist_id, w_1.id)
