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
from service.models.wishlist import Wishlist
from service.models.product import Product
from service.models.wishlist_product import WishlistProduct

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        jsonify(
            name="Wishlists REST API Service",
            version="1.0",
            paths=url_for("wishlists_index", _external=True),
        ),
        status.HTTP_200_OK,
    )

## Define functional routes below
@app.route("/wishlists", methods=["GET"])
def wishlists_index():
  return (
        jsonify(
            {"message": "Nothing here yet!" }
        ),
        status.HTTP_200_OK,
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
        WishlistProduct.delete_all_by_wishlist_id(wishlist_id)

    return make_response("", status.HTTP_204_NO_CONTENT)





######################################################################
# ADD A NEW PRODUCT IN A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/products", methods=["POST"])
def create_products():
    """
    Creates a product
    This endpoint will create a product based the data in the body that is posted
    """
    app.logger.info("Request to create a product")
    check_content_type("application/json")
    product = Product()
    product.deserialize(request.get_json())
    product.create()
    message = product.serialize()

    dic = {'product_id': product.id, 'wishlist_id': wishlist_id}
    wishlistproduct = WishlistProduct()
    wishlistproduct.deserialize(dic)
    wishlistproduct.create()

    location_url = url_for("get_products", product_id=product.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )
