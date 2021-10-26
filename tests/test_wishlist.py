# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Wishlist Model

Test cases can be run with:
    nosetests
    coverage report -m

"""
import os
import logging
import unittest
import factory
import json
from service.models.product import Product
from service.models.wishlist import Wishlist, WishlistVo
from service.models.wishlist_product import WishlistProduct
from service import app
from service.models.model_utils import Availability, DataValidationError,EntityNotFoundError, db
from .factories import ProductFactory, WishlistFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  W I S H L I S T   M O D E L   T E S T   C A S E S
######################################################################
class TestWishlistModel(unittest.TestCase):
    """ Test Cases for Wishlist Model """

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)
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

    def test_create_a_wishlist(self):
        """Create a Wishlist and assert that it exists"""
        wishlist_instance = Wishlist(user_id=1,name="My first wishlist")
        self.assertIsNotNone(wishlist_instance)
        self.assertEqual(wishlist_instance.user_id,1)
        self.assertEqual(wishlist_instance.name,"My first wishlist")

        wishlist_instance = Wishlist(user_id=1,name="Your first wishlist")
        self.assertEqual(wishlist_instance.name, 'Your first wishlist')

    def test_add_wishlist(self):
        """Create a wishlist and add it to database"""
        ws = Wishlist.find_all()
        self.assertEqual(len(ws),0)
        w_instance = Wishlist(name="test wishlist",user_id = 1)
        w_instance.create()
        ws = Wishlist.find_all()
        self.assertEqual(len(ws),1)
        self.assertEqual(ws[0].name,"test wishlist")

    def test_update_a_wishlist(self):
        """Test update a wishlist"""
        w_instance = WishlistFactory()
        w_instance.create()
        self.assertEqual(w_instance.id, 1)
        original_id = w_instance.id
        original_name = w_instance.name
        w_instance.name = "something different"
        w_instance.update()
        self.assertEqual(w_instance.id, original_id)
        self.assertNotEqual(w_instance.name,original_name)
        ws = Wishlist.find_all()
        self.assertEqual(len(ws),1)
        self.assertEqual(ws[0].name,"something different")

        w_instance.id = None
        self.assertRaises(DataValidationError,w_instance.update)

    def test_delete_a_wishlist(self):
        """Test delete a wishlist and its corresponding wishlist products"""
        w_instance_1 = Wishlist(name="test wishlist",user_id = 11)
        w_instance_1.create()
        w_instance_2 = Wishlist(name="test wishlist 2",user_id = 13)
        w_instance_2.create()
        p_instance_1 = Product(name="book",price=12.5,status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test book")
        p_instance_1.create()
        p_instance_2 = Product(name="toy",price=121.5,status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test toy")
        p_instance_2.create()
        wp_instance = WishlistProduct(wishlist_id = w_instance_1.id, product_id = p_instance_1.id)
        wp_instance.create()
        wp_instance = WishlistProduct(wishlist_id = w_instance_1.id, product_id = p_instance_2.id)
        wp_instance.create()
        wp_instance = WishlistProduct(wishlist_id = w_instance_2.id, product_id = p_instance_1.id)
        wp_instance.create()

        self.assertEqual(len(Wishlist.find_all()),2)
        self.assertEqual(len(WishlistProduct.find_all()),3)
        self.assertEqual(len(Product.find_all()),2)

        w_instance_1.delete()

        ws = Wishlist.find_all()
        self.assertEqual(len(ws),1)
        self.assertEqual(ws[0].name,"test wishlist 2")
        wps = WishlistProduct.find_all()
        self.assertEqual(len(wps),1)
        self.assertEqual(wps[0].wishlist_id,2)
        self.assertEqual(len(Product.find_all()),2)

        w = WishlistFactory()
        w.id = 20193
        self.assertEqual(w.delete(),0)
        w.id = None
        self.assertEqual(w.delete(),0)

    def test_read_a_wishlist(self):
        """Test read information from a wishlist"""
        w_instance_1 = Wishlist(name="test wishlist",user_id = 11)
        w_instance_1.create()
        w_instance_2 = Wishlist(name="test wishlist 2",user_id = 13)
        w_instance_2.create()
        p_instance_1 = Product(name="book",price=12.5,status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test book")
        p_instance_1.create()
        p_instance_2 = Product(name="toy",price=121.5,status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test toy")
        p_instance_2.create()
        wp_instance = WishlistProduct(wishlist_id = w_instance_1.id, product_id = p_instance_1.id)
        wp_instance.create()
        wp_instance = WishlistProduct(wishlist_id = w_instance_1.id, product_id = p_instance_2.id)
        wp_instance.create()
        wp_instance = WishlistProduct(wishlist_id = w_instance_2.id, product_id = p_instance_1.id)
        wp_instance.create()

        w_instance = Wishlist.find_by_id(1)
        self.assertIsNotNone(w_instance)
        self.assertEqual(w_instance.read(),WishlistVo(w_instance_1,[p_instance_1,p_instance_2]).serialize())

        w_instance = Wishlist(id = 9, name="test wishlist", user_id = 3)
        self.assertRaises(EntityNotFoundError,w_instance.read)

    def test_serialize_a_wishlist(self):
        """Test serialize a wishlist"""
        w_instance = WishlistFactory()
        data = w_instance.serialize()
        self.assertIsNotNone(data)
        self.assertIn('id',data)
        self.assertEqual(data['id'],w_instance.id)
        self.assertIn('name',data)
        self.assertEqual(data['name'],w_instance.name)
        self.assertIn('user_id',data)
        self.assertEqual(data['user_id'],w_instance.user_id)

    def test_deserialize_a_wishlist(self):
        """Test deserialize a wishlist"""
        data = {
            'id':1,
            'name':"Test wishlist",
            'user_id':3
        }

        w_instance = Wishlist()
        w_instance.deserialize(data)
        self.assertIsNotNone(w_instance)
        self.assertEqual(w_instance.id,None)
        self.assertEqual(w_instance.name, "Test wishlist")
        self.assertEqual(w_instance.user_id, 3)

        data = {
            'id':1,
            'name':1,
            'user_id':3
        }
        w_instance = Wishlist()
        self.assertRaises(DataValidationError, w_instance.deserialize, data)

    def test_deserialize_missing_data(self):
        """Test deserialization of a WishlistProduct with missing data"""
        data = {
            'id':1,
            'user_id':10
        }

        w_instance = Wishlist()
        self.assertRaises(DataValidationError, w_instance.deserialize, data)

    def test_add_items(self):
        """Test adding items to a wishlist"""
        products = ProductFactory.create_batch(6)
        for p in products:
            p.create()

        w_instance = WishlistFactory()
        w_instance.create()
        cnt = w_instance.add_items([p.id for p in products])
        self.assertEqual(cnt,6)
        wps = WishlistProduct.find_all_by_wishlist_id(w_instance.id)
        self.assertEqual(len(wps),6)
        self.assertEqual(wps[0].product_id, products[0].id)
        self.assertEqual(wps[3].product_id, products[3].id)
        self.assertNotEqual(wps[5].product_id, products[4].id)

    def test_add_items_with_duplicates(self):
        """Test adding duplicated items to a wishlist"""
        p_instance_1 = Product(name="book",price=12.5,status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test book")
        p_instance_1.create()
        p_instance_2 = Product(name="toy",price=121.5,status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test toy")
        p_instance_2.create()

        products = [p_instance_1,p_instance_2,p_instance_1]

        w_instance = WishlistFactory()
        w_instance.create()
        cnt = w_instance.add_items([p.id for p in products])
        self.assertEqual(cnt,2)
        wps = WishlistProduct.find_all_by_wishlist_id(w_instance.id)
        self.assertEqual(len(wps),2)
        self.assertEqual(wps[0].product_id, products[0].id)

    def test_add_existing_items(self):
        """Test adding existing items to a wishlist"""
        p_instance_1 = Product(name="book",price=12.5,status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test book")
        p_instance_1.create()
        p_instance_2 = Product(name="toy",price=121.5,status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test toy")
        p_instance_2.create()
        w_instance = WishlistFactory()
        w_instance.create()
        wp_instance = WishlistProduct(wishlist_id = w_instance.id, product_id = p_instance_1.id)
        wp_instance.create()

        products = [p_instance_1,p_instance_2]


        cnt = w_instance.add_items([p.id for p in products])
        self.assertEqual(cnt,1)
        wps = WishlistProduct.find_all_by_wishlist_id(w_instance.id)
        self.assertEqual(len(wps),2)
        self.assertEqual(wps[0].product_id, products[0].id)
        self.assertEqual(wps[1].product_id, products[1].id)

    def test_delete_items(self):
        """Test deleting items from a wishlist"""
        p_instance_1 = Product(name="book",price=12.5,status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test book")
        p_instance_1.create()
        p_instance_2 = Product(name="toy",price=121.5,status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test toy")
        p_instance_2.create()
        p_instance_3 = Product(name="TV",price=1210.5,status=Availability.AVAILABLE,pic_url="www.tv.com",short_desc="this is a test tv")
        p_instance_3.create()
        w_instance_1 = WishlistFactory()
        w_instance_1.create()
        w_instance_2 = WishlistFactory()
        w_instance_2.create()
        WishlistProduct(wishlist_id = w_instance_1.id, product_id = p_instance_1.id).create()
        WishlistProduct(wishlist_id = w_instance_1.id, product_id = p_instance_2.id).create()
        WishlistProduct(wishlist_id = w_instance_1.id, product_id = p_instance_3.id).create()
        WishlistProduct(wishlist_id = w_instance_2.id, product_id = p_instance_3.id).create()

        cnt = w_instance_1.delete_items([1,3])
        self.assertEqual(cnt, 2)
        wps = WishlistProduct.find_all()
        self.assertEqual(len(wps),2)
        self.assertEqual(wps[1].wishlist_id,2)
        self.assertEqual(wps[0].product_id,2)

    def test_find_all(self):
        """Test finding all wishlists from the database"""
        w_instance_1 = WishlistFactory()
        w_instance_1.create()
        w_instance_2 = WishlistFactory()
        w_instance_2.create()
        w_instance_3 = WishlistFactory()
        w_instance_3.create()

        ws = Wishlist.find_all()
        self.assertIsNotNone(ws)
        self.assertEqual(len(ws),3)

    def test_find_by_id(self):
        """"Test find one wishlist from database by its id"""
        w_instance_1 = WishlistFactory()
        w_instance_1.create()
        w_instance_2 = WishlistFactory()
        w_instance_2.create()
        w_instance_3 = WishlistFactory()
        w_instance_3.create()

        w_instance = Wishlist.find_by_id(1)
        self.assertIsNotNone(w_instance)
        self.assertEqual(w_instance.user_id,w_instance_1.user_id)

        w_instance = Wishlist.find_by_id(4)
        self.assertIsNone(w_instance)

    def test_find_all_by_user_id(self):
        """Test finding all wishlists belongs to a user"""
        p_1 = Product(name="book",price=12.5,status=Availability.AVAILABLE,pic_url="www.book.com",short_desc="this is a test book")
        p_1.create()
        p_2 = Product(name="toy",price=15.5,status=Availability.AVAILABLE,pic_url="www.toy.com",short_desc="this is a test toy")
        p_2.create()
        p_3 = Product(name="TV",price=1200.5,status=Availability.AVAILABLE,pic_url="www.tv.com",short_desc="this is a test tv")
        p_3.create()
        p_4 = Product(name="milk",price=6.5,status=Availability.AVAILABLE,pic_url="www.milk.com",short_desc="this is a test milk")
        p_4.create()

        w_1 = Wishlist(name="Test wishlist 1", user_id = 3)
        w_1.create()
        w_2 = Wishlist(name="Test wishlist 2", user_id = 67)
        w_2.create()
        w_3 = Wishlist(name="Test wishlist 3", user_id = 3)
        w_3.create()

        WishlistProduct(wishlist_id = 1, product_id = 1).create()
        WishlistProduct(wishlist_id = 1, product_id = 2).create()
        WishlistProduct(wishlist_id = 2, product_id = 3).create()
        WishlistProduct(wishlist_id = 3, product_id = 4).create()

        w_vo = Wishlist.find_all_by_user_id(4)
        self.assertEqual(w_vo,[])

        w_vo = Wishlist.find_all_by_user_id(3)
        self.assertEqual(w_vo, \
            [WishlistVo(w_1,products=[p_1,p_2]).serialize(),\
                WishlistVo(w_3,products=[p_4]).serialize()])
