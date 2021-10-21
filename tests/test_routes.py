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
import decimal
from flask.json import JSONEncoder
from urllib.parse import quote_plus
from service import status  # HTTP Status Codes
from service.models.model_utils import db, Availability
from service.models.product import Product
from service.models.wishlist import Wishlist
from service.models.wishlist_product import WishlistProduct
from service.routes import app, init_db
from .factories import WishlistFactory, ProductFactory

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)
CONTENT_TYPE_JSON = "application/json"
BASE_URL = "/wishlists"

class JsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, Availability):
            return obj.name
        return JSONEncoder.default(self, obj)


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
        app.json_encoder = JsonEncoder
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
#  H E L P E R   M E T H O D S
######################################################################

    def _create_products(self, count):
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            resp = self.app.post( 
                "/products", 
                json = test_product.serialize(),
                content_type = CONTENT_TYPE_JSON )
            self.assertEqual( resp.status_code, status.HTTP_201_CREATED, "Could not create test product" )
            new_product = resp.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    def _create_wishlists(self, count):
        wishlists = []
        for _ in range(count):
            test_wishlist = WishlistFactory()
            resp = self.app.post( 
                "/wishlists", 
                json = test_wishlist.serialize(),
                content_type = CONTENT_TYPE_JSON )
            self.assertEqual( resp.status_code, status.HTTP_201_CREATED, "Could not create test wishlist" )
            new_wishlist = resp.get_json()
            test_wishlist.id = new_wishlist["data"]
            wishlists.append(test_wishlist)
        return wishlists


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

    def test_get_wishlists(self):
        """Get a single Wishlist"""
        test_wishlist = self._create_wishlists(1)[0]
        resp = self.app.get("/wishlists/{}".format(test_wishlist.id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], test_wishlist.id)

    def test_create_product(self):
        """Create a product"""
        new_product = ProductFactory()
        resp = self.app.post("/products", json=new_product.serialize(), content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        product = resp.get_json()
        self.assertEqual(product["name"], new_product.name)
        self.assertEqual(product["price"], new_product.price)
        self.assertEqual(product["status"], new_product.status.name)
        self.assertEqual(product["pic_url"], new_product.pic_url)
        self.assertEqual(product["short_desc"], new_product.short_desc)

    def test_get_product(self):
        """Get a single product"""
        test_product = self._create_products(1)[0]
        resp = self.app.get("/products/{}".format(test_product.id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], test_product.id) 

    def test_add_product_into_wishlist(self):
        """Add a product into a wishlist"""
        wishlist = self._create_wishlists(1)[0]
        new_product = self._create_products(1)[0]
        data_posted = { "id": new_product.id }
        resp = self.app.post(
            "/wishlists/{}/products".format(wishlist.id),
            json = data_posted,
            content_type = "application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        wishlistproduct = resp.get_json()
        logging.debug(wishlistproduct)
        self.assertEqual(wishlistproduct["product_id"], new_product.id)
        self.assertEqual(wishlistproduct["wishlist_id"], wishlist.id)

    def test_list_products_in_wishlist(self):
        """List products in a wishlist"""
        test_wishlist = self._create_wishlists(1)[0]
        products = self._create_products(2)
        
        resp = self.app.post(
            "/wishlists/{}/products".format(test_wishlist.id),
            json = products[0].serialize(),
            content_type = "application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.app.post(
            "/wishlists/{}/products".format(test_wishlist.id),
            json = products[1].serialize(),
            content_type = "application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.app.get(
            "/wishlists/{}/products".format(test_wishlist.id),
            content_type = "applicationn/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

