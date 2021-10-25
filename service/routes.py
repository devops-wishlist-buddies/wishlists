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
Wishlists Service

Paths:
------
TBD
"""

import os
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort

from service.models.model_utils import Availability, DataValidationError
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy

# Import Flask application
from . import app

from service.models.wishlist import Wishlist, WishlistVo
from service.models.product import Product
from service.models.wishlist_product import WishlistProduct
from service.models.model_utils import db

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
# GET INDEX
######################################################################
@app.route("/",methods=["GET"])
def index():
    """ Root URL response """
    return (
        jsonify(
            name="Wishlists REST API Service",
            version="1.0",
        ),
        status.HTTP_200_OK,
    )

######################################################################
# CREATE A NEW WISHLIST
######################################################################
@app.route("/wishlists", methods=["POST"])
def create_wishlists():
    """
    Creates a wishlist
    This endpoint will create a wishlist based the data in the body that is posted
    or data that is sent via an html form post.
    """
    app.logger.info("Request to create a wishlist")
    data = {}
    # Check for form submission data
    if request.headers.get("Content-Type") != "application/json":
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Unsupported media type : application/json expected"   
        )
    else:
        app.logger.info("Processing JSON data")
        data = request.get_json()
    wishlist = Wishlist()
    wishlist.deserialize(data)
    wishlist.create()
    return make_response(
        jsonify(
            data = wishlist.id,
            message = "Wishlist Created!"
        ),
        status.HTTP_201_CREATED
    )
######################################################################
# List ALL WISHLISTS
######################################################################
@app.route("/wishlists", methods=["GET"])
def list_all_wishlists():
    app.logger.info("Request for all wishlists")
    query_res = Wishlist.find_all()

    wishlists = [r for r in query_res]
    res = []
    for w in wishlists:
        wishlist_products = WishlistProduct.find_all_by_wishlist_id(w.id)
        products = []
        if len(wishlist_products) != 0:
          products = Product.find_all_by_id([wp.product_id for wp in wishlist_products])
        res.append(WishlistVo(w,products))
      
    r = [vo.serialize() for vo in res]

    if not r:
        abort(
            status.HTTP_404_NOT_FOUND, "No wishlists found!"
        )
    return make_response(
        jsonify(data = r, message = "All the wishlists."),
        status.HTTP_200_OK
    )

######################################################################
# List ALL WISHLISTS FOR A USER
######################################################################
@app.route("/wishlists/user/<int:user_id>", methods=["GET"])
def list_wishlists_by_userid(user_id):
    app.logger.info("Request for wishlists with user_id: %s", user_id)
    res = Wishlist.find_all_by_user_id(user_id)
    if not res:
        abort(
            status.HTTP_404_NOT_FOUND, "wishlists with user_id '{}' not found!".format(user_id)
        )
    return make_response(
        jsonify(data = res, message = "wishlists for user_id '{}'.".format(user_id)),
        status.HTTP_200_OK
    )

######################################################################
# DELETE A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlists(wishlist_id):
    """
    Delete a wishlist
    This endpoint will delete a wishlist based the id specified in the path
    """
    app.logger.info("Request to delete wishlist with id: %s", wishlist_id)
    wishlist = Wishlist.find_by_id(wishlist_id)

    if wishlist:
        wishlist.delete()
        return make_response(
            jsonify(
                data = [],
                message = "Wishlist Deleted!"
                ), 
                status.HTTP_200_OK
            )
    else:
        return make_response(
            jsonify(
                data = [],
                message = "Wishlist {} not found".format(wishlist_id)
                ), 
                status.HTTP_200_OK
            )

######################################################################
# Delete items from a wishlist
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items", methods=["DELETE"])
def delete_items_from_wishlist(wishlist_id):
    """
    Delete items from wishlist
    This endpoint will delete items from a wishlist based on the ids 
    """
    if request.headers.get("Content-Type") != "application/json":
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Unsupported media type : application/json expected"   
        )
    else:   
        data = request.get_json()
        product_id = data['product_id']
        app.logger.info("Request to delete items with id %s from wishlist %s" % (product_id,wishlist_id))
        w = Wishlist.find_by_id(wishlist_id)

        if not w:
            return make_response(
                    jsonify(
                            data = [],
                            message = "Wishlist {} not found".format(wishlist_id)
                        ),
                        status.HTTP_200_OK
                    )
        else:
            cnt = w.delete_items(product_id)
            if(cnt == len(product_id)):
                return make_response(
                    jsonify(
                            data = [],
                            message = "All items are deleted"
                        ),
                        status.HTTP_200_OK
                    )
            else:
                return make_response(
                    jsonify(
                        data = [],
                        message = "{} items are deleted".format(cnt)
                    ),
                    status.HTTP_206_PARTIAL_CONTENT
                )

######################################################################
# Add items to a wishlist
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items", methods=["PUT"])
def add_items_to_wishlist(wishlist_id):
    """
    Add items to wishlist
    This endpoint will add items to a wishlist based on the ids 
    """
    if request.headers.get("Content-Type") != "application/json":
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Unsupported media type : application/json expected"   
        )
    else:   
        data = request.get_json()
        product_id = data['product_id']
        app.logger.info("Request to add items with id %s to wishlist %s" % (product_id,wishlist_id))
        w = Wishlist.find_by_id(wishlist_id)

        if not w:
            abort(
            status.HTTP_404_NOT_FOUND, "Wishlist with id %s not found!".format(wishlist_id)   
        )
        else:
            cnt = w.add_items(product_id)
            if(cnt == len(product_id)):
                return make_response(
                    jsonify(
                            data = [],
                            message = "All items are added"
                        ),
                        status.HTTP_200_OK
                    )
            else:
                return make_response(
                    jsonify(
                        data = [],
                        message = "{} items are added".format(cnt)
                    ),
                    status.HTTP_206_PARTIAL_CONTENT
                )

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """Initlaize the model"""
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.logger.setLevel(logging.CRITICAL)
    Product.init_db(app)
    Wishlist.init_db(app)
    WishlistProduct.init_db(app)

    w_1 = Wishlist(name = "User 1 first wishlist", user_id = 1)
    w_1.create()
    w_2 = Wishlist(name = "User 1 second wishlist", user_id = 1)
    w_2.create()
    w_3 = Wishlist(name = "User 2 first wishlist", user_id = 2)
    w_3.create()

    p_1 = Product(name = "toy",price=11.5,status=Availability.Available,pic_url="www.toy.com/1.png",short_desc="this is a toy")    
    p_2 = Product(name = "book",price=20.5,status=Availability.Available,pic_url="www.book.com/1.png",short_desc="this is a book")
    p_3 = Product(name = "tv",price=1001.5,status=Availability.Available,pic_url="www.tv.com/1.png",short_desc="this is a tv")
    p_4 = Product(name = "pepsi",price=7.5,status=Availability.Available,pic_url="www.drinks.com/pepsi.png",short_desc="this is pepsi coke")
    p_5 = Product(name = "bread",price=3.5,status=Availability.Available,pic_url="www.bakery.com/1.png",short_desc="this is a bread")
    p_6 = Product(name = "soccer",price=23.5,status=Availability.Available,pic_url="www.soccer.com/1.png",short_desc="this is a soccer")

    p = [p_1,p_2,p_3,p_4,p_5,p_6]
    for i in range(0, len(p)):
        p[i].create()
    
    w_1.add_items([1,2,3,4,5,6])
    w_2.add_items([1,5,6])