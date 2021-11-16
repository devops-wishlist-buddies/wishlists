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
import json
import logging
import unittest
from service import status  # HTTP Status Codes
from service.models.model_utils import db, Availability
from service.models.product import Product
from service.models.wishlist import Wishlist
from service.routes import app
from .factories import WishlistFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.environ['VCAP_SERVICES'])
    DATABASE_URI = vcap['user-provided'][0]['credentials']['url']

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
    with app.app_context():
      db.drop_all()
      db.create_all()

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
    """Create a wishlist"""
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
    resp = self.app.delete("/wishlists", json=new_wl, content_type="application/json")
    self.assertEqual(resp.status_code,405)

  def test_list_all_wishlists(self):
    """List all wishlists"""
    resp = self.app.get("/wishlists")
    self.assertEqual(resp.status_code, status.HTTP_200_OK)
    d = resp.get_json()
    self.assertEqual(d["message"],"No wishlists found!")

    t1 = {"name": "test 1", "user_id": 1}
    t2 = {"name": "test 2", "user_id": 1}
    wishlist1 = Wishlist()
    wishlist1.deserialize(t1)
    wishlist1.create()
    wishlist2 = Wishlist()
    wishlist2.deserialize(t2)
    wishlist2.create()
    resp = self.app.get("/wishlists")
    self.assertEqual(resp.status_code, status.HTTP_200_OK)
    d = resp.get_json()['data']
    self.assertEqual(len(d), 2)

  def test_list_wishlists_by_userid(self):
    """List wishlists by userid"""
    t1 = {"name": "test 1", "user_id": 1}
    t2 = {"name": "test 2", "user_id": 1}
    wishlist1 = Wishlist()
    wishlist1.deserialize(t1)
    wishlist1.create()
    wishlist2 = Wishlist()
    wishlist2.deserialize(t2)
    wishlist2.create()

    resp = self.app.get("/wishlists?user_id=1")
    self.assertEqual(resp.status_code, status.HTTP_200_OK)
    d = resp.get_json()["data"]
    self.assertEqual(len(d), 2)
    self.assertEqual(d, Wishlist.find_all_by_user_id(1))

    resp = self.app.get("/wishlists?user_id=2")
    self.assertEqual(resp.status_code, status.HTTP_200_OK)
    d = resp.get_json()
    self.assertEqual(d["message"],"No wishlists found for user_id '2'.")

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
    self.assertEqual(resp.status_code,200)

    resp = self.app.get("{0}/{1}".format(BASE_URL, 1), content_type="application/json")
    self.assertEqual(resp.status_code, 404)

  def test_delete_products_from_wishlist(self):
    """Delete products from wishlist"""
    w_instance_1 = WishlistFactory()
    w_instance_1.create()

    p_instance_1 = Product(wishlist_id = w_instance_1.id, inventory_product_id=1,name="book",price=12.5,\
      status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test book")
    p_instance_1.create()
    p_instance_2 = Product(wishlist_id = w_instance_1.id, inventory_product_id=2,name="toy",price=121.5,\
      status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test toy")
    p_instance_2.create()
    p_instance_3 = Product(wishlist_id = w_instance_1.id, inventory_product_id=3,name="TV",price=1210.5,\
      status=Availability.AVAILABLE,pic_url="www.tv.com",short_desc="this is a test tv")
    p_instance_3.create()

    wps = Product.find_all()
    self.assertEqual(len(wps), 3)

    resp = self.app.delete("/wishlists/16359/products")
    self.assertEqual(resp.status_code, 404)

    resp = self.app.delete("/wishlists/{}/products".format(w_instance_1.id))
    self.assertEqual(resp.status_code, 200)
    new_product_list = Product.find_all_by_wishlist_id(w_instance_1.id)
    self.assertEqual(len(new_product_list), 0)

    resp = self.app.delete("/wishlists/{}/products".format(w_instance_1.id))
    self.assertEqual(resp.get_json()['message'],\
       "There is no products in the wishlist, 0 products are deleted.")

    resp = self.app.get("/wishlists/1/products")
    self.assertEqual(resp.status_code, 405)

  def test_delete_a_product_from_wishlist(self):
    """Delete a product from a wishlist"""
    w_instance_1 = WishlistFactory()
    w_instance_1.create()
    w_instance_2 = WishlistFactory()
    w_instance_2.create()

    p_instance_1 = Product(wishlist_id = w_instance_1.id, inventory_product_id=1,name="book",price=12.5,\
      status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test book")
    p_instance_1.create()
    p_instance_2 = Product(wishlist_id = w_instance_1.id, inventory_product_id=2,name="toy",price=121.5,\
      status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a test toy")
    p_instance_2.create()
    p_instance_3 = Product(wishlist_id = w_instance_1.id, inventory_product_id=3,name="TV",price=1210.5,\
      status=Availability.AVAILABLE,pic_url="www.tv.com",short_desc="this is a test tv")
    p_instance_3.create()

    wps = Product.find_all()
    self.assertEqual(len(wps), 3)

    resp = self.app.delete("/wishlists/16359/products/1")
    self.assertEqual(resp.status_code, 404)

    resp = self.app.delete("/wishlists/{}/products/{}".format(w_instance_1.id, p_instance_1.id))
    self.assertEqual(resp.status_code, 200)
    new_product_list = Product.find_all_by_wishlist_id(w_instance_1.id)
    self.assertEqual(len(new_product_list), 2)

    resp = self.app.delete("/wishlists/{}/products/{}".format(w_instance_2.id, p_instance_2.id))
    self.assertEqual(resp.get_json()['message'], "Product with id {} is not in this wishlist."\
      .format(p_instance_2.id))
    new_product_list = Product.find_all_by_wishlist_id(w_instance_1.id)
    self.assertEqual(len(new_product_list), 2)

  def test_list_products_in_wishlist(self):
    """List all products in a wishlist"""
    w_instance_1 = WishlistFactory()
    w_instance_1.create()
    w_instance_2 = WishlistFactory()
    w_instance_2.create()

    p_instance_1 = Product(wishlist_id=w_instance_1.id,inventory_product_id=1, name="book",\
      price=12.5,status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a book")
    p_instance_1.create()
    p_instance_2 = Product(wishlist_id=w_instance_1.id,inventory_product_id=3, name="toy",\
      price=121.5,status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a toy")
    p_instance_2.create()
    p_instance_3 = Product(wishlist_id=w_instance_1.id,inventory_product_id=2,name="TV",\
      price=1210.5,status=Availability.AVAILABLE,pic_url="www.tv.com",short_desc="this is a tv")
    p_instance_3.create()

    wps = Product.find_all()
    self.assertEqual(len(wps),3)

    resp = self.app.get(
      "/wishlists/{0}".format(w_instance_1.id),
      content_type = "application/json"
    )
    self.assertEqual(resp.status_code, status.HTTP_200_OK)
    resp_body = resp.get_json()
    self.assertEqual(len(resp_body["data"]["products"]), 3)
    self.assertEqual(resp_body["data"]["id"], 1)

    resp = self.app.get(
      "/wishlists/{0}".format(w_instance_2.id),
      content_type = "application/json"
    )
    self.assertEqual(resp.status_code, status.HTTP_200_OK)
    resp_body = resp.get_json()
    self.assertEqual(len(resp_body["data"]["products"]), 0)

  def test_get_a_product_in_a_wishlist(self):
    """Get a product in a wishlist"""
    w_instance_1 = WishlistFactory()
    w_instance_1.create()
    w_instance_2 = WishlistFactory()
    w_instance_2.create()

    p_instance_1 = Product(wishlist_id=w_instance_1.id,inventory_product_id=1,name="book",\
      price=12.5, status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="best book")
    p_instance_1.create()
    p_instance_2 = Product(wishlist_id=w_instance_1.id,inventory_product_id=2,name="toy",\
      price=121.5,status=Availability.AVAILABLE,pic_url="www.google.com",short_desc="this is a toy")
    p_instance_2.create()
    p_instance_3 = Product(wishlist_id=w_instance_1.id,inventory_product_id=3,name="TV",\
      price=1210.5,status=Availability.AVAILABLE,pic_url="www.tv.com",short_desc="this is a tv")
    p_instance_3.create()
    p_instance_4 = Product(wishlist_id=w_instance_2.id,inventory_product_id=3,name="TV",\
      price=1210.5,status=Availability.AVAILABLE,pic_url="www.tv.com",short_desc="this is a tv")
    p_instance_4.create()

    wps = Product.find_all()
    self.assertEqual(len(wps),4)

    resp = resp = self.app.get(
          "/wishlists/{0}/products/{1}".format(w_instance_1.id, p_instance_2.id),
          content_type = "application/json"
      )
    self.assertEqual(resp.status_code, status.HTTP_200_OK)

    data = resp.get_json()["data"]
    self.assertEqual(data["name"], p_instance_2.name)
    self.assertEqual(data["price"], p_instance_2.price)
    self.assertEqual(data["status"], Availability.AVAILABLE.name)
    self.assertEqual(data["pic_url"], p_instance_2.pic_url)
    self.assertEqual(data["short_desc"], p_instance_2.short_desc)
    self.assertEqual(data["wishlist_id"], p_instance_2.wishlist_id)
    self.assertEqual(data["wishlist_id"], w_instance_1.id)

    resp = self.app.get(
          "/wishlists/1/products/4",
          content_type = "application/json"
      )
    self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

  def test_create_product(self):
    """Create product"""
    w_instance_1 = WishlistFactory()
    w_instance_1.create()

    p_instance_1 = {
      'name': "piggy",
      'price': 100.5,
      'status': Availability.UNAVAILABLE,
      'pic_url': "www.piggy.com/1.png",
      'short_desc': "this is a piggy",
      'inventory_product_id': 12,
    }
    # valid request
    resp = self.app.post("/wishlists/{0}/products".format(w_instance_1.id),\
      json=p_instance_1, content_type="application/json")
    self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    new_json = resp.get_json()
    product = Product.find_by_id(new_json['data'])
    self.assertEqual(product.name, "piggy")
    self.assertEqual(product.price, 100.5)
    self.assertEqual(product.status, Availability.UNAVAILABLE)
    self.assertEqual(product.pic_url, "www.piggy.com/1.png")
    self.assertEqual(product.short_desc, "this is a piggy")
    self.assertEqual(product.wishlist_id, w_instance_1.id)

    # wrong payload
    resp = self.app.post("/wishlists/{0}/products".format(w_instance_1.id),\
      json='im a string!', content_type="application/json")
    self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    w_instance_2 = WishlistFactory()
    w_instance_2.create()

    p_instance_2 = {
      'name': "piggy",
      'price': 100.5,
      'pic_url': "www.piggy.com/1.png",
      'short_desc': "this is a piggy",
    }
    # attempt to create with missing fields
    resp = self.app.post("/wishlists/{0}/products".format(w_instance_2.id), json=p_instance_2,\
      content_type="application/json")
    self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # valid request as url-encoded
    resp = self.app.post(\
      "/wishlists/{0}/products?name=mug&price=10&status=1&pic_url=www.piggy.com/1.png"\
      "&short_desc=\"the best mug in the world\"&inventory_product_id=30".format(w_instance_2.id),\
      content_type="application/x-www-form-urlencoded")
    self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    # invalid request as url-encoded (missing fields)
    resp = self.app.post(\
      "/wishlists/{0}/products?name=mug&price=10&status=1&pic_url=www.piggy.com/1.png"\
      "&short_desc=\"the best mug in the world\"".format(w_instance_2.id),\
      content_type="application/x-www-form-urlencoded")
    self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

  def test_update_product_in_wishlist(self):
    """Update product"""
    w_instance_1 = WishlistFactory()
    w_instance_1.create()

    p_instance_1 = {
      'name': "piggy",
      'price': 100.5,
      'status': Availability.UNAVAILABLE,
      'pic_url': "www.piggy.com/1.png",
      'short_desc': "this is a piggy",
      'inventory_product_id': 12,
    }
    resp = self.app.post("/wishlists/{0}/products".format(w_instance_1.id),\
      json=p_instance_1, content_type="application/json")
    self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    updated_fields = {
      'name': 'new and improved piggy',
      'status': Availability.AVAILABLE
    }
    product_id = resp.get_json()['data']
    resp = self.app.put("/wishlists/{0}/products/{1}".format(w_instance_1.id, product_id),\
      json=updated_fields, content_type="application/json")

    self.assertEqual(resp.status_code, status.HTTP_200_OK)
    altered_product = Product.find_by_id(product_id)
    self.assertEqual(altered_product.name, updated_fields['name'])
    self.assertEqual(altered_product.status, updated_fields['status'])
    self.assertEqual(altered_product.short_desc, p_instance_1['short_desc'])

    # test some invalid scenarios
    updated_fields = {
      'some_invalid_field': 'will it break?'
    }
    resp = self.app.put("/wishlists/{0}/products/{1}".format(w_instance_1.id, product_id),\
      json=updated_fields, content_type="application/json")

    self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    resp = self.app.put("/wishlists/{0}/products/{1}".format(w_instance_1.id, product_id),\
      json="not a dictionary", content_type="application/json")
    self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(resp.get_json()['message'], "Expected a json request body")

    resp = self.app.put("/wishlists/{0}/products/{1}".format(w_instance_1.id, product_id),\
      json={'name': None}, content_type="application/json")
    self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(resp.get_json()['message'], "Field name cannot be null")
