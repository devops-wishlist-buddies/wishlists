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
Wishlists API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

"""

import os
import logging
import unittest
from urllib.parse import quote_plus
from service import status  # HTTP Status Codes
from service.models.model_utils import db, Availability
from service.models.product import Product
from service.models.wishlist import Wishlist
from service.models.wishlist_product import WishlistProduct
from service.routes import app, init_db
from .factories import WishlistFactory

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/wishlists"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestWishlistsServer(unittest.TestCase):
    """ Wishlists Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)
        Wishlist.init_db(app)
        WishlistProduct.init_db(app)

    @classmethod
    def tearDownClass(cls):
        db.session.close()

    def setUp(self):
        """ Runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index(self):
      """Test the index page"""
      resp = self.app.get("/")
      self.assertEqual(resp.status_code, status.HTTP_200_OK)
      data = resp.get_json()
      self.assertEqual(data["name"], "Wishlists REST API Service")
      self.assertEqual(data["version"], "1.0")

    def test_create_wishlist(self):
      new_wl = {"name": "test", "user_id": 1}
      resp = self.app.post("/wishlists", json=new_wl, content_type="application/json")
      self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
      new_json = resp.get_json()
      wl = Wishlist.find_by_id(new_json['data'])
      self.assertEqual(wl.name, "test")
      self.assertEqual(wl.user_id, 1)

      resp = self.app.post("/wishlists", content_type="multipart/form-data")
      self.assertEqual(resp.status_code, 415)

      new_wl = {"user_id": 1}
      resp = self.app.post("/wishlists", json=new_wl, content_type="application/json")
      self.assertEqual(resp.status_code, 400)

      new_wl = {"name": "test", "user_id": 1}
      resp = self.app.get("/wishlists", json=new_wl, content_type="application/json")
      self.assertEqual(resp.status_code,405)

    def test_list_wishlists_by_userid(self):
        t1 = {"name": "test 1", "user_id": 1}
        t2 = {"name": "test 2", "user_id": 1}
        wishlist1 = Wishlist()
        wishlist1.deserialize(t1)
        wishlist1.create()
        wishlist2 = Wishlist()
        wishlist2.deserialize(t2)
        wishlist2.create()

        resp = self.app.get("/wishlists/user/1")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        d = resp.get_json()["data"]
        self.assertEqual(len(d), 2)
        self.assertEqual(d, Wishlist.find_all_by_user_id(1))
        resp = self.app.get("/wishlists/user/2")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        d = resp.get_json()
        self.assertEqual(d["message"],"404 Not Found: wishlists with user_id '2' not found!")
        resp = self.app.post("/wishlists/user/1")
        self.assertEqual(resp.status_code,405)

    def test_delete_wishlist(self):
      """ Delete a Wishlist """
      w = WishlistFactory()
      w.create()
      resp = self.app.delete("{0}/{1}".format(BASE_URL, w.id), content_type="application/json")
      self.assertEqual(resp.status_code, status.HTTP_200_OK)
      self.assertEqual(resp.get_json()['message'],"Wishlist Deleted!")
      # make sure they are deleted
      resp = Wishlist.find_by_id(w.id)
      self.assertEqual(resp, None)

      resp = self.app.delete("{0}/{1}".format(BASE_URL, 20000), content_type="application/json")
      self.assertEqual(resp.status_code,404)

      resp = self.app.get("{0}/{1}".format(BASE_URL, 1), content_type="application/json")
      self.assertEqual(resp.status_code, 405)
    
    def test_delete_items_from_wishlist(self):
      """delete items from wishlist"""
      p_instance_1 = Product(name="book",price=12.5,status=Availability.Available,pic_url="www.google.com",short_desc="this is a test book")
      p_instance_1.create()
      p_instance_2 = Product(name="toy",price=121.5,status=Availability.Available,pic_url="www.google.com",short_desc="this is a test toy")
      p_instance_2.create()
      p_instance_3 = Product(name="TV",price=1210.5,status=Availability.Available,pic_url="www.tv.com",short_desc="this is a test tv")
      p_instance_3.create()
      w_instance_1 = WishlistFactory()
      w_instance_1.create()
      w_instance_2 = WishlistFactory()
      w_instance_2.create()
      WishlistProduct(wishlist_id = w_instance_1.id, product_id = p_instance_1.id).create()
      WishlistProduct(wishlist_id = w_instance_1.id, product_id = p_instance_2.id).create()
      WishlistProduct(wishlist_id = w_instance_1.id, product_id = p_instance_3.id).create()
      WishlistProduct(wishlist_id = w_instance_2.id, product_id = p_instance_3.id).create()
      resp_body = {"id":[1,3]}
      resp = self.app.delete("/wishlists/1/delete-items",json=resp_body,content_type="application/json")
      self.assertEqual(resp.status_code,200)
      wps = WishlistProduct.find_all()
      self.assertEqual(len(wps),2)

      resp = self.app.delete("/wishlists/1/delete-items",json=resp_body,content_type="multipart/form-data")
      self.assertEqual(resp.status_code,415)

      resp = self.app.delete("/wishlists/1/delete-items",json=resp_body,content_type="application/json")
      self.assertEqual(resp.status_code,206)

      resp = self.app.get("/wishlists/1/delete-items",json=resp_body,content_type="application/json")
      self.assertEqual(resp.status_code,405)