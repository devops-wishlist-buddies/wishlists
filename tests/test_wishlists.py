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
from werkzeug.exceptions import NotFound
from service.models.wishlist import Wishlist
from service import app
from .factories import WishlistFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  W I S H L I S T   M O D E L   T E S T   C A S E S
######################################################################
class TestWishlistModel(unittest.TestCase):
    """ Test Cases for Wishlist Model """

    # @classmethod
    # def setUpClass(cls):
    #     """ This runs once before the entire test suite """
    #     app.config["TESTING"] = True
    #     app.config["DEBUG"] = False
    #     app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    #     app.logger.setLevel(logging.CRITICAL)
    #     Pet.init_db(app)

    # @classmethod
    # def tearDownClass(cls):
    #     """ This runs once after the entire test suite """
    #     pass

    # def setUp(self):
    #     """ This runs before each test """
    #     db.drop_all()  # clean up the last tests
    #     db.create_all()  # make our sqlalchemy tables

    # def tearDown(self):
    #     """ This runs after each test """
    #     db.session.remove()
    #     db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    
