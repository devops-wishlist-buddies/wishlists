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
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy

# Import Flask application
from . import app

from service.models.wishlist import Wishlist
from service.models.product import Product
from service.models.wishlist_product import WishlistProduct

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
    if request.headers.get("Content-Type") == "application/x-www-form-urlencoded":
        app.logger.info("Processing FORM data")
        data = {
            "name": request.form.get("name"),
            "user_id": request.form.get("user_id"),
        }
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
# RETRIEVE A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["GET"])
def get_wishlist(wishlist_id):
    """
    Retrieve a single wishlist
    This endpoint will return a wishlist based on it"s id
    """
    app.logger.info("Request for wishlist with id: %s", wishlist_id)
    wishlist = Wishlist.find_by_id(wishlist_id)
    if not wishlist:
        return(
            f"Wishlist with id {wishlist_id} was not found",
            status.HTTP_404_NOT_FOUND
        )
    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)


######################################################################
# ADD A PRODUCT IN A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/products", methods=["POST"])
def add_product_to_wishlist(wishlist_id):
    """
    This endpoint will add a product into wishlist
    """
    app.logger.info("Request to add a product")
    check_content_type("application/json")

    data = request.get_json()
    product_id = data["id"]
    product_exist_check = Product.find_by_id( product_id )
    if not product_exist_check:
        return(
            f"Product with id {product_id} was not found",
            status.HTTP_404_NOT_FOUND
        )
    
    wishlistproduct = WishlistProduct()
    wishlistproduct.product_id = product_id
    wishlistproduct.wishlist_id = wishlist_id
    if not Wishlist.find_by_id( wishlist_id ):
        return(
            f"Wishlist with id {wishlist_id} was not found",
            status.HTTP_404_NOT_FOUND
        )
    wishlistproduct.create()
    message = wishlistproduct.serialize()

    return make_response(jsonify(message), status.HTTP_201_CREATED)

######################################################################
# LIST PRODUCTS IN A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/products", methods=["GET"])
def list_products_in_wishlist(wishlist_id):
    """
    List all products in a wishlist based on a wishlist_id
    """
    app.logger.info("Request to list products in a wishlist")
    wishlist_products= WishlistProduct.find_all_by_wishlist_id(wishlist_id)
    products_id_list = [ wishlist_product.product_id for wishlist_product in wishlist_products ]
    res = []
    for product_id in products_id_list:
        product = Product.find_by_id( product_id )
        if not product:
            return(
                f"Product with id {product_id} was not found",
                status.HTTP_404_NOT_FOUND
            )
        res.append( product.serialize() )
    return make_response(jsonify(res), status.HTTP_200_OK)

######################################################################
# CREATE A NEW PRODUCT
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """
    Creates a product
    This endpoint will create a product based the data in the body that is posted
    """
    app.logger.info("Request to create a product")
    data = request.get_json()
    product= Product()
    if isinstance(data["status"], str):
        if not hasattr(Availability, data["status"]):
            return(
                f"product got wrong status",
                status.HTTP_400_BAD_REQUEST
            )
        data["status"] = getattr(Availability, data["status"])
    product.deserialize(data)
    product.create()
    return make_response(
        jsonify( product.serialize() ),
        status.HTTP_201_CREATED
    )

######################################################################
# RETRIEVE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """
    Retrieve a single product
    This endpoint will return a product based on it"s id
    """
    app.logger.info("Request for product with id: %s", product_id)
    product = Product.find_by_id(product_id)
    if not product:
        return(
            f"product with id {product_id} was not found",
            status.HTTP_404_NOT_FOUND
        )
    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)



######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """Initlaize the model"""
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.logger.setLevel(logging.CRITICAL)
    Wishlist.init_db(app)
    Product.init_db(app)
    WishlistProduct.init_db(app)

def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type),
    )