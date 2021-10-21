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
from service.models.model_utils import db
from service.models.product import Product
from service.models.wishlist import Wishlist
from service.models.wishlist_product import WishlistProduct
from service.routes import app, init_db
from .factories import WishlistFactory, ProductFactory

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


######################################################################
# #  T E S T   C A S E S
######################################################################
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

    def test_create_product(self):
      new_wl = {"name": "test", "user_id": 1}
      resp = self.app.post("/wishlists", json=new_wl, content_type="application/json")

      new=resp.get_json()

      new_product = ProductFactory()

      # new_product = Product.serialize(new_product)

      new_product = {"name": "hello", "price": 1, "pic-url": "www.google.com", "short_desc" : "hello"}



      resp = self.app.post("{0}/{1}/{0}".format(BASE_URL, new['data'], "products"), json=new_product, content_type="application/json")
      self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


      new_json = resp.get_json()
      product = Product.find_by_id(new_json['data'])
      self.assertEqual(product.short_desc, new_product.short_desc)
      self.assertEqual(product.pic_url, new_product.pic_url)
      self.assertEqual(product.status, new_product.status)
      self.assertEqual(product.price, new_product.price)
      self.assertEqual(product.name, new_product.name)



    def test_delete_wishlist(self):
      """ Delete a Wishlist """
      new_wl = WishlistFactory()
      resp = self.app.post("/wishlists", json=new_wl.serialize(), content_type="application/json")
      new_json = resp.get_json()
      resp = self.app.delete("{0}/{1}".format(BASE_URL, new_json['data']), content_type="application/json")
      self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
      self.assertEqual(len(resp.data), 0)
      # make sure they are deleted
      resp = Wishlist.find_by_id(new_json['data'])
      self.assertEqual(resp, None)
