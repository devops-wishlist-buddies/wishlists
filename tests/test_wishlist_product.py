import os
import logging
import unittest
from werkzeug.exceptions import NotFound
from service.models.model_utils import Availability, DataValidationError, db
from service.models.wishlist_product import WishlistProduct
from service.models.wishlist import Wishlist
from service.models.product import Product
from service import app
from tests.factories import ProductFactory, WishlistFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  W I S H L I S T P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################

class TestWishlistProduct(unittest.TestCase):
    """Test Cases for WishlistProduct Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Wishlist.init_db(app)
        WishlistProduct.init_db(app)

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

    def test_create_a_wishlist_product(self):
        """Create a WishlistProduct and assert that it exists"""
        wp_instance = WishlistProduct(wishlist_id = 1, product_id = 15)
        self.assertIsNotNone(wp_instance)
        self.assertEqual(wp_instance.id, None)
        self.assertEqual(wp_instance.wishlist_id, 1)
        self.assertEqual(wp_instance.product_id, 15)
        wp_instance = WishlistProduct(wishlist_id = 10, product_id = 15)
        self.assertEqual(wp_instance.wishlist_id, 10)
    
    def test_add_a_wishlist_product(self):
        """Create a WishlistProduct and add it to the database"""
        wps = WishlistProduct.find_all()
        self.assertListEqual(wps,[])
        w_instance = Wishlist(name="test wishlist",user_id = 11)
        w_instance.create()
        p_instance = Product(name="book",price=12.5,status=Availability.Available,pic_url="www.google.com",short_desc="this is a test")
        p_instance.create()
        wp_instance = WishlistProduct(wishlist_id = w_instance.id, product_id = p_instance.id)
        self.assertIsNotNone(wp_instance)
        self.assertEqual(wp_instance.id, None)
        wp_instance.create()
        self.assertEqual(wp_instance.id,1)
        wps = WishlistProduct.find_all()
        self.assertEqual(len(wps),1)
    
    def test_update_a_wishlist_product(self):
        """Update a WishlistProduct"""
        w_instance = Wishlist(name="test wishlist",user_id = 11)
        w_instance.create()
        p_instance_1 = Product(name="book",price=12.5,status=Availability.Available,pic_url="www.google.com",short_desc="this is a test book")
        p_instance_1.create()
        p_instance_2 = Product(name="toy",price=121.5,status=Availability.Available,pic_url="www.google.com",short_desc="this is a test toy")
        p_instance_2.create()
        wp_instance = WishlistProduct(wishlist_id = w_instance.id, product_id = p_instance_1.id)
        wp_instance.id = None
        logging.debug(wp_instance)
        wp_instance.create()
        logging.debug(wp_instance)
        self.assertEqual(wp_instance.id, 1)
        # Change it an save it
        wp_instance.product_id = p_instance_2.id
        original_id = wp_instance.id
        wp_instance.update()
        self.assertEqual(wp_instance.id, original_id)
        self.assertEqual(wp_instance.product_id, p_instance_2.id)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        wps = WishlistProduct.find_all()
        self.assertEqual(len(wps), 1)
        self.assertEqual(wps[0].id, 1)

        wp_instance.id = None
        self.assertRaises(DataValidationError,wp_instance.update)

    def test_delete_a_wishlist_product(self):
        """Delete a wishlist product"""
        w_instance = Wishlist(name="test wishlist",user_id = 11)
        w_instance.create()
        p_instance = Product(name="book",price=12.5,status=Availability.Available,pic_url="www.google.com",short_desc="this is a test")
        p_instance.create()
        wp_instance = WishlistProduct(wishlist_id = w_instance.id, product_id = p_instance.id)
        wp_instance.create()
        self.assertEqual(len(WishlistProduct.find_all()),1)
        wp_instance.delete()
        self.assertEqual(len(WishlistProduct.find_all()),0)

    def test_serialize_a_wishlist_product(self):
        """Test serialize a wishlist product"""
        wp_instance = WishlistProduct(wishlist_id = 1, product_id = 12)
        data = wp_instance.serialize()
        self.assertIsNotNone(data)
        self.assertIn('id',data)
        self.assertEqual(data['id'],wp_instance.id)
        self.assertIn('wishlist_id',data)
        self.assertEqual(data['wishlist_id'],wp_instance.wishlist_id)
        self.assertIn('product_id',data)
        self.assertEqual(data['product_id'],wp_instance.product_id)

    def test_deserialize_a_wishlist_product(self):
        """Test deserialize a wishlist product"""
        data = {
            'id':1,
            'wishlist_id':2,
            'product_id':3
        }

        wp_instance = WishlistProduct()
        wp_instance.deserialize(data)
        self.assertIsNotNone(wp_instance)
        self.assertEqual(wp_instance.id,None)
        self.assertEqual(wp_instance.wishlist_id, 2)
        self.assertEqual(wp_instance.product_id, 3)

        data = {
            'id':1,
            'wishlist_id':"fake id",
            'product_id':3
        }

        wp_instance = WishlistProduct()
        self.assertRaises(DataValidationError, wp_instance.deserialize,data)


    def test_deserialize_missing_data(self):
        """Test deserialization of a WishlistProduct with missing data"""
        data = {
            'id':1,
            'wishlist_id':10
        }

        wp_instance = WishlistProduct()
        self.assertRaises(DataValidationError, wp_instance.deserialize, data)
        
    def test_find_all_by_wishlist_id(self):
        """Test find wishlist products by wishlist id"""
        w_instances = WishlistFactory.create_batch(3)
        for item in w_instances:
            item.create()
        
        p_instances = ProductFactory.create_batch(3)
        for item in p_instances:
            item.create()

        wp_instance = WishlistProduct(wishlist_id = 2, product_id = 1)
        wp_instance.create()
        wp_instance = WishlistProduct(wishlist_id = 1, product_id = 1)
        wp_instance.create()
        wp_instance = WishlistProduct(wishlist_id = 2, product_id = 3)
        wp_instance.create()

        self.assertEqual(len(WishlistProduct.find_all()),3)
        wps = WishlistProduct.find_all_by_wishlist_id(2)
        self.assertEqual(len(wps),2)
        self.assertEqual(wps[1].product_id,3)
        self.assertEqual(wps[0].product_id,1)
    
    def test_find_by_wishlist_id_and_product_id(self):
        """Test find one wishtlist product by wishlist id and product id"""
        w_instances = WishlistFactory.create_batch(3)
        for item in w_instances:
            item.create()
        
        p_instances = ProductFactory.create_batch(3)
        for item in p_instances:
            item.create()

        wp_instance = WishlistProduct(wishlist_id = 2, product_id = 1)
        wp_instance.create()
        wp_instance = WishlistProduct(wishlist_id = 1, product_id = 1)
        wp_instance.create()
        wp_instance = WishlistProduct(wishlist_id = 2, product_id = 3)
        wp_instance.create()

        self.assertEqual(len(WishlistProduct.find_all()),3)
        wp_instance = WishlistProduct.find_by_wishlist_id_and_product_id(2,3)
        self.assertIsNotNone(wp_instance)
        self.assertEqual(wp_instance.product_id,3)
        wp_instance = WishlistProduct.find_by_wishlist_id_and_product_id(2,4)
        self.assertIsNone(wp_instance)

    def test_delete_all_by_wishlist_id_and_product_id(self):
        """Test delete all wishlist products by wishlist id and product ids"""
        w_instances = WishlistFactory.create_batch(3)
        for item in w_instances:
            item.create()
        
        p_instances = ProductFactory.create_batch(3)
        for item in p_instances:
            item.create()

        wp_instance = WishlistProduct(wishlist_id = 2, product_id = 1)
        wp_instance.create()
        wp_instance = WishlistProduct(wishlist_id = 1, product_id = 1)
        wp_instance.create()
        wp_instance = WishlistProduct(wishlist_id = 2, product_id = 3)
        wp_instance.create()
        self.assertEqual(len(WishlistProduct.find_all()),3)
        cnt = WishlistProduct.delete_all_by_wishlist_id_and_product_id(2,[1,3])
        self.assertEqual(cnt,2)
        self.assertEqual(len(WishlistProduct.find_all()),1)

        cnt = WishlistProduct.delete_all_by_wishlist_id_and_product_id(2,[6])
        self.assertEqual(cnt,0)
        self.assertEqual(len(WishlistProduct.find_all()),1)
    
    def test_delete_all_by_wishlist_id(self):
        """Test delete all wishlist products by wishlist id"""
        w_instances = WishlistFactory.create_batch(3)
        for item in w_instances:
            item.create()
        
        p_instances = ProductFactory.create_batch(3)
        for item in p_instances:
            item.create()

        wp_instance = WishlistProduct(wishlist_id = 2, product_id = 1)
        wp_instance.create()
        wp_instance = WishlistProduct(wishlist_id = 1, product_id = 1)
        wp_instance.create()
        wp_instance = WishlistProduct(wishlist_id = 2, product_id = 3)
        wp_instance.create()

        self.assertEqual(len(WishlistProduct.find_all()),3)
        self.assertEqual(WishlistProduct.delete_all_by_wishlist_id(2), 2)
        self.assertEqual(len(WishlistProduct.find_all()),1)
        self.assertEqual(WishlistProduct.delete_all_by_wishlist_id(4), 0)
        self.assertEqual(len(WishlistProduct.find_all()),1)


