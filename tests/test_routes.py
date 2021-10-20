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
from service.routes import app, init_db
from .factories import ProductFactory, WishlistFactory

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/wishlists"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestWishlistsServer(unittest.TestCase):
    """ Wishlists Server Tests """

    # @classmethod
    # def setUpClass(cls):
    #     """ Run once before all tests """
    #     app.config["TESTING"] = True
    #     app.config["DEBUG"] = False
    #     app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    #     app.logger.setLevel(logging.CRITICAL)
    #     init_db()

    # @classmethod
    # def tearDownClass(cls):
    #     pass

    # def setUp(self):
    #     """ Runs before each test """
    #     db.drop_all()  # clean up the last tests
    #     db.create_all()  # create new tables
    #     self.app = app.test_client()

    # def tearDown(self):
    #     db.session.remove()
    #     db.drop_all()
    def _create_products(self, count):
      """ Factory method to create pets in bulk """
      products = []
      for _ in range(count):
        test_product = ProductFactory()
        resp = self.app.post(
          BASE_URL, json=test_product.serialize(), content_type="application/json"
        )
        self.assertEqual(
          resp.status_code, status.HTTP_201_CREATED, "Could not create test product"
        )
        new_product = resp.get_json()
        test_product.id = new_product["id"]
        products.append(test_product)
      return products


    def test_create_product(self):
      """ Create a new Product """
      test_product = ProductFactory()
      logging.debug(test_product)
      resp = self.app.post(
        BASE_URL, json=test_product.serialize(), content_type="application/json"
      )
      self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
      # Make sure location header is set
      location = resp.headers.get("Location", None)
      self.assertIsNotNone(location)
      # Check the data is correct
      new_product = resp.get_json()
      self.assertEqual(new_product["name"], test_product.name, "Names do not match")
      self.assertEqual(
        new_product["price"], test_product.price, "Prices do not match"
      )
      self.assertEqual(
        new_product["status"], test_product.status, "Status does not match"
      )
      self.assertEqual(
        new_product["pic_url"], test_product.pic_url, "Pic_url does not match"
      )
      self.assertEqual(
        new_product["short_desc"], test_product.short_desc, "Short_desc does not match"
      )

      # Check that the location header was correct
      resp = self.app.get(location, content_type="application/json")
      self.assertEqual(resp.status_code, status.HTTP_200_OK)
      new_product = resp.get_json()
      self.assertEqual(new_product["name"], test_product.name, "Names do not match")
      self.assertEqual(
        new_product["price"], test_product.price, "Prices do not match"
      )
      self.assertEqual(
        new_product["status"], test_product.status, "Status does not match"
      )
      self.assertEqual(
        new_product["pic_url"], test_product.pic_url, "Pic_url does not match"
      )
      self.assertEqual(
        new_product["short_desc"], test_product.short_desc, "Short_desc does not match"
      )


    def test_create_product_no_data(self):
      """ Create a Product with missing data """
      resp = self.app.post(
        BASE_URL, json={}, content_type="application/json"
      )
      self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_product_bad_name(self):
      """ Create a Product with bad name data """
      test_product = ProductFactory()
      logging.debug(test_product)
      # change available to a string
      test_product.name = "hello"
      resp = self.app.post(
        BASE_URL, json=test_product.serialize(), content_type="application/json"
      )
      self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_product_bad_price(self):
      """ Create a Product with bad price data """
      product = ProductFactory()
      logging.debug(product)
      # change gender to a bad string
      test_product = product.serialize()
      test_product["price"] = 1000  # wrong case
      resp = self.app.post(
        BASE_URL, json=test_product, content_type="application/json"
      )
      self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_product_bad_pic_url(self):
      """ Create a Product with bad pic_url data """
      product = ProductFactory()
      logging.debug(product)
      # change gender to a bad string
      test_product = product.serialize()
      test_product["pic_url"] = "www.123.com"  # wrong case
      resp = self.app.post(
        BASE_URL, json=test_product, content_type="application/json"
      )
      self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_bad_short_desc(self):
      """ Create a Product with bad short_desc data """
      product = ProductFactory()
      logging.debug(product)
      # change gender to a bad string
      test_product = product.serialize()
      test_product["short_desc"] = "this is nothing"  # wrong case
      resp = self.app.post(
        BASE_URL, json=test_product, content_type="application/json"
      )
      self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_no_content_type(self):
      """ Create a Product with no content type """
      resp = self.app.post(BASE_URL)
      self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)



    def test_delete_wishlist(self):
      """ Delete a Wishlist """
      test_wishlist = self._create_wishlists(1)[0]
      resp = self.app.delete(
        "{0}/{1}".format(BASE_URL, test_wishlist.id), content_type="application/json"
      )
      self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
      self.assertEqual(len(resp.data), 0)
      # make sure they are deleted
      resp = self.app.get(
        "{}/{}".format(BASE_URL, test_wishlist.id), content_type="application/json"
      )
      self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
