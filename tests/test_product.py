"""
Test cases for Product Model
Test cases can be run with:
    nosetests
    coverage report -m
While debugging just these tests it's convinient to use this:
    nosetests --stop tests/test_Products.py:TestProductModel
"""

import os
import logging
import unittest
from werkzeug.exceptions import NotFound
from service.models.model_utils import Availability, DataValidationError, db
from service.models.product import Product
from service import app
from .factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)

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

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_Product(self):
        """Create a Product and assert that it exists"""
        product_instance = Product(name="book",price=12.5,status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test")
        self.assertTrue(product_instance != None)
        self.assertEqual(product_instance.id, None)
        self.assertEqual(product_instance.name, "book")
        self.assertEqual(product_instance.price, 12.5)
        self.assertEqual(product_instance.status, Availability.AVAILABLE)
        self.assertEqual(product_instance.pic_url,"www.google.com")
        self.assertEqual(product_instance.short_desc,"this is a test")
        product_instance = Product(name="book",price=12.5,status=Availability.UNAVAILABLE,pic_url="www.google.com",short_desc="this is a test")
        self.assertEqual(product_instance.status, Availability.UNAVAILABLE)

    def test_add_a_Product(self):
        """Create a Product and add it to the database"""
        products = Product.find_all()
        self.assertEqual(products, [])
        product_instance = Product(name="book",price=12.5,status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test")
        self.assertTrue(product_instance != None)
        self.assertEqual(product_instance.id, None)
        product_instance.create()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(product_instance.id, 1)
        products = Product.find_all()
        self.assertEqual(len(products), 1)

    def test_update_a_Product(self):
        """Update a Product"""
        product_instance = ProductFactory()
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

    def test_delete_a_Product(self):
        """Delete a Product"""
        product_instance = ProductFactory()
        product_instance.create()
        self.assertEqual(len(Product.find_all()), 1)
        # delete the Product and make sure it isn't in the database
        product_instance.delete()
        self.assertEqual(len(Product.find_all()), 0)

    def test_serialize_a_Product(self):
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

    def test_deserialize_a_Product(self):
        """Test deserialization of a Product"""
        data = {
            'id': 1,
            'name': "piggy",
            'price': 100.5,
            'status': Availability.UNAVAILABLE,
            'pic_url': "www.piggy.com/1.png",
            'short_desc': "this is a piggy"
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
        test_Product = ProductFactory()
        data = test_Product.serialize()
        data["status"] = 1
        product_instance = Product()
        self.assertRaises(DataValidationError, product_instance.deserialize, data)

    def test_find_Product(self):
        """Find a Product by ID"""
        Products = ProductFactory.create_batch(3)
        for product_instance in Products:
            product_instance.create()
        logging.debug(Products)
        # make sure they got saved
        self.assertEqual(len(Product.find_all()), 3)
        # find the 2nd Product in the list
        product_instance = Product.find_by_id(Products[1].id)
        self.assertIsNot(product_instance, None)
        self.assertEqual(product_instance.id, Products[1].id)
        self.assertEqual(product_instance.name, Products[1].name)
        self.assertEqual(product_instance.status, Products[1].status)

    def test_find_all_by_id(self):
        Product(name="toy", status=Availability.AVAILABLE, price = 12.5, pic_url="www.toy.com/1.png", short_desc = "this is a toy").create()
        Product(name="book", status=Availability.AVAILABLE, price=13.5, pic_url="www.book.com/1.png", short_desc = "this is a book").create()
        Product(name="table", status=Availability.UNAVAILABLE, price=103.5, pic_url="www.table.com/1.png", short_desc = "this is a table").create()
        products = Product.find_all_by_id([1,2,3])
        self.assertEqual(len(products),3)
        self.assertEqual(products[1].name, "book")
        self.assertEqual(products[1].price, 13.5)
        self.assertEqual(products[1].status, Availability.AVAILABLE)

    def test_find_all_by_id_and_status(self):
        """Find products by id and status"""
        Product(name="toy", status=Availability.AVAILABLE, price = 12.5, pic_url="www.toy.com/1.png", short_desc = "this is a toy").create()
        Product(name="book", status=Availability.AVAILABLE, price=13.5, pic_url="www.book.com/1.png", short_desc = "this is a book").create()
        Product(name="table", status=Availability.UNAVAILABLE, price=103.5, pic_url="www.table.com/1.png", short_desc = "this is a table").create()

        products = Product.find_all_by_id_and_status([1,2,3],Availability.AVAILABLE)
        self.assertEqual(len(products),2)
        self.assertEqual(products[1].name, "book")
        self.assertEqual(products[1].price, 13.5)
        self.assertEqual(products[1].status, Availability.AVAILABLE)

    def test_find_by_id_and_status(self):
        """Find product by id and status"""
        Product(name="toy", status=Availability.AVAILABLE, price = 12.5, pic_url="www.toy.com/1.png", short_desc = "this is a toy").create()
        Product(name="book", status=Availability.AVAILABLE, price=13.5, pic_url="www.book.com/1.png", short_desc = "this is a book").create()
        Product(name="table", status=Availability.UNAVAILABLE, price=103.5, pic_url="www.table.com/1.png", short_desc = "this is a table").create()

        product_instance = Product.find_by_id_and_status(2,Availability.AVAILABLE)
        self.assertIsNotNone(product_instance)
        self.assertEqual(product_instance.name,"book")
        self.assertEqual(product_instance.price,13.5)
        self.assertEqual(product_instance.status,Availability.AVAILABLE)

        product_instance = Product.find_by_id_and_status(1,Availability.UNAVAILABLE)
        self.assertIsNone(product_instance)

    def test_find_or_404_found(self):
        """Find or return 404 found"""
        Products = ProductFactory.create_batch(3)
        for Product in Products:
            Product.create()

        Product = Product.find_or_404(Products[1].id)
        self.assertIsNot(Product, None)
        self.assertEqual(Product.id, Products[1].id)
        self.assertEqual(Product.name, Products[1].name)
        self.assertEqual(Product.status, Products[1].status)

    def test_find_or_404_not_found(self):
        """Find or return 404 NOT found"""
        self.assertRaises(NotFound, Product.find_or_404, 0)

    def test_find_by_name(self):
        """Find a product by its name"""
        Product(name="toy", status=Availability.AVAILABLE, price = 12.5, pic_url="www.toy.com/1.png", short_desc = "this is a toy").create()
        Product(name="toy", status=Availability.AVAILABLE, price = 22.5, pic_url="www.toy.com/2.png", short_desc = "this is another toy").create()
        Product(name="book", status=Availability.AVAILABLE, price=13.5, pic_url="www.book.com/1.png", short_desc = "this is a book").create()
        Product(name="table", status=Availability.UNAVAILABLE, price=103.5, pic_url="www.table.com/1.png", short_desc = "this is a table").create()

        self.assertEqual(len(Product.find_by_name("book")),1)
        self.assertEqual(len(Product.find_by_name("toy")),2)
