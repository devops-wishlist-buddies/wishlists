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
from flask import jsonify, request, make_response, abort

from . import app
from . import status  # HTTP Status Codes

# Import Flask application
from service.models.wishlist import Wishlist, WishlistVo
from service.models.product import Product
from service.models.model_utils import Availability, get_non_null_product_fields

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
    return abort(
      status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, \
      "Unsupported media type : application/json expected"
    )

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
# List WISHLISTS
######################################################################
@app.route("/wishlists", methods=["GET"])
def list_all_wishlists():
  """
  Lists wishlists
  This endpoint will return all wishlists in the database
  or wishlists with a specific user_id.
  """
  user_id = request.args.get('user_id')
  if not user_id:
    app.logger.info("Request for all wishlists")
    query_res = Wishlist.find_all()
    res = [r.read() for r in query_res]

    if not res:
      msg = "No wishlists found!"
    else:
      msg = "All the wishlists."

    return make_response(
      jsonify(data = res, message = msg),
      status.HTTP_200_OK
    )

  user_id = int(user_id)
  app.logger.info("Request for wishlists with user_id: %s", user_id)
  res = Wishlist.find_all_by_user_id(user_id)
  if not res:
    msg = "No wishlists found for user_id '%s'." % user_id
  else:
    msg = "Wishlists for user_id '%s'." % user_id

  return make_response(
    jsonify(data = res, message = msg),
    status.HTTP_200_OK
  )

######################################################################
# DELETE A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlists(wishlist_id):
  """
  Delete a wishlist
  This endpoint will delete a wishlist based the id specified in the URL
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
  return make_response(
    jsonify(
      data = [],
      message = "Wishlist {} not found".format(wishlist_id)
    ),
    status.HTTP_200_OK
  )

######################################################################
# Delete products from a wishlist
######################################################################
@app.route("/wishlists/<int:wishlist_id>/products", methods=["DELETE"])
def delete_products_from_wishlist(wishlist_id):
  """
  Delete products from wishlist
  This endpoint will delete products from the wishlist with id specified in the URL.
  The endpoint will remove products that are provided in the body as a list of product ids.
  """
  if request.headers.get("Content-Type") != "application/json":
    return abort(
      status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Unsupported media type : application/json expected"
    )
  data = request.get_json()
  product_ids_list = data['product_ids_list']
  app.logger.info("Request to delete products with id %s from wishlist %s"\
    % (product_ids_list,wishlist_id))
  wishlist = Wishlist.find_by_id(wishlist_id)

  if not wishlist:
    return make_response(
      jsonify(
        data = [],
        message = "Wishlist {} not found".format(wishlist_id)
      ),
      status.HTTP_404_NOT_FOUND
    )
  cnt = wishlist.delete_products(product_ids_list)

  if cnt == len(product_ids_list):
    return make_response(
      jsonify(
        data = [],
        message = "All products are deleted"
      ),
      status.HTTP_200_OK
    )

  return make_response(
    jsonify(
      data = [],
      message = "{} products are deleted".format(cnt)
    ),
    status.HTTP_206_PARTIAL_CONTENT
  )

######################################################################
# LIST PRODUCTS IN A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["GET"])
def list_products_in_wishlist(wishlist_id):
  """
  List all products in a wishlist based on a wishlist_id
  """
  app.logger.info("Request to list products in a wishlist")
  wishlist_products = Product.find_all_by_wishlist_id(wishlist_id)
  res = []
  for product in wishlist_products:
    if not product:
      return make_response(
        jsonify(
          data = [],
          message = "Product {} with id {} was not found".format(product.name, product.id)
        ),
        status.HTTP_404_NOT_FOUND
      )
    res.append(product.serialize())

  wishlist = Wishlist.find_by_id(wishlist_id)
  if not wishlist:
    return make_response(
      jsonify(
        data = [],
        message = "Wishlist with id {} was not found".format(wishlist_id)
      ),
      status.HTTP_404_NOT_FOUND
    )

  return make_response(
    jsonify(
      wishlist_id = wishlist.id,
      wishlist_user_id = wishlist.user_id,
      wishlist_name = wishlist.name,
      product_list = res,
      message = "Getting Products from wishlists with id {} success".format(wishlist_id)
    ),
    status.HTTP_200_OK
  )

######################################################################
# GET A PRODUCT IN A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/products/<int:product_id>", methods=["GET"])
def get_a_product_in_a_wishlist(wishlist_id, product_id):
  """
  Get a product in a wishlist based on a wishlist_id
  This endpoint will firstly look for a wishlist based on a wishlist_id
  Then look for a product based on a product_id
  """
  app.logger.info("Request to get a specific product in a wishlist")
  wishlist_product= Product.find_by_wishlist_id_and_product_id(wishlist_id, product_id)

  if not wishlist_product:
    return(
      jsonify(
        data = [],
        message = f"Wishlist with id {wishlist_id} and Product with" \
          f"id {product_id} was not found in Wishlist_Product db"
      ),
      status.HTTP_404_NOT_FOUND
    )

  product = Product.find_by_id(product_id)
  if not product:
    return(
      jsonify(
        data = [],
        message = f"Product with id {product_id} was not found in Product db"
      ),
      status.HTTP_404_NOT_FOUND
    )

  return make_response(
    jsonify(
      data = product.serialize(),
      message = "Successfully get Product with id {product_id} in wishlist with id {wishlist_id}"
    ),
    status.HTTP_200_OK
  )

######################################################################
# CREATE A NEW PRODUCT IN A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/products", methods=["POST"])
def create_product_in_wishlist(wishlist_id):
  """
  Creates a product
  This endpoint will create a product based the data in the body that is posted
  """
  app.logger.info("Request to create a product")
  data = {}
  non_null_fields = get_non_null_product_fields()

  if request.headers.get("Content-Type") == "application/x-www-form-urlencoded":
    app.logger.info("Processing FORM data")
    data = {
      "name": request.args.get("name"),
      "price": request.args.get("price"),
      "status": Availability.AVAILABLE \
        if request.args.get("status") == '1' else Availability.UNAVAILABLE,
      "pic_url": request.args.get("pic_url"),
      "short_desc": request.args.get("short_desc"),
      "wishlist_id": wishlist_id,
      "inventory_product_id": request.args.get("inventory_product_id"),
    }
  else:
    app.logger.info("Processing JSON data")
    data = request.get_json()

    request_data = request.get_json()
    if not isinstance(request_data, dict):
      return make_response(
        jsonify(
          data = [],
          message = "Expected a json request body"
        ),
        status.HTTP_400_BAD_REQUEST
      )

    for key in request_data:
      if key == 'status' and request_data[key]:
        data[key] = getattr(Availability, request_data[key])
      else:
        data[key] = request_data[key]

    data["wishlist_id"] = wishlist_id

  new_body_keys = data.keys()
  for key in non_null_fields:
    if key not in new_body_keys or data[key] is None:
      return make_response(
        jsonify(
          data = [],
          message = "%s cannot be null" % key
        ),
        status.HTTP_400_BAD_REQUEST
      )

  product = Product()
  product.deserialize(data)
  product.create()

  return make_response(
    jsonify(
      data = product.id,
      message = "Product Created"
    ),
    status.HTTP_201_CREATED
  )

######################################################################
# UPDATE A PRODUCT IN A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/products/<int:product_id>", methods=["PUT"])
def update_product_in_wishlist(wishlist_id, product_id):
  """
  Updates a product
  This endpoint will modify an existing product in a wishlist
  """
  app.logger.info("Request to update a product")
  product = Product.find_by_wishlist_id_and_product_id(wishlist_id, product_id)
  request_data = request.get_json()
  non_null_fields = get_non_null_product_fields()
  if not isinstance(request_data, dict):
    return make_response(
      jsonify(
        data = [],
        message = "Expected a json request body"
      ),
      status.HTTP_400_BAD_REQUEST
    )

  product_fields = product.serialize()
  product_fields.update(request_data)
  for key in product_fields:
    if product_fields[key] is None and key in non_null_fields:
      return make_response(
        jsonify(
          data = [],
          message = "%s cannot be null" % key
        ),
        status.HTTP_400_BAD_REQUEST
      )

  product.deserialize(product_fields)
  product.update()

  return make_response(
    jsonify(
      data = product.id,
      message = "Product Updated"
    ),
    status.HTTP_200_OK
  )

def init_db(app):
  """Initlaize the model"""
  app.app_context().push()

  Product.init_db(app)
  Wishlist.init_db(app)

  # logging.info('Creating dummy data')

  # w_1 = Wishlist(name = "User 1 first wishlist", user_id = 1)
  # w_1.create()
  # w_2 = Wishlist(name = "User 1 second wishlist", user_id = 1)
  # w_2.create()
  # w_3 = Wishlist(name = "User 2 first wishlist", user_id = 2)
  # w_3.create()

  # p_1 = Product(wishlist_id=w_1.id,name = "toy",price=11.5,status=Availability.AVAILABLE, \
  #   pic_url="www.toy.com/1.png",short_desc="this is a toy",inventory_product_id=3)
  # p_2 = Product(wishlist_id=w_1.id,name = "book",price=20.5,status=Availability.AVAILABLE, \
  #   pic_url="www.book.com/1.png",short_desc="this is a book",inventory_product_id=4)
  # p_3 = Product(wishlist_id=w_1.id,name = "tv",price=1001.5,status=Availability.AVAILABLE,\
  #   pic_url="www.tv.com/1.png",short_desc="this is a tv",inventory_product_id=15)
  # p_4 = Product(wishlist_id=w_1.id,name = "pepsi",price=7.5,status=Availability.AVAILABLE,\
  #   pic_url="www.drinks.com/pepsi.png",short_desc="this is pepsi coke",inventory_product_id=1)
  # p_5 = Product(wishlist_id=w_1.id,name = "bread",price=3.5,status=Availability.AVAILABLE,\
  #   pic_url="www.bakery.com/1.png",short_desc="this is a bread",inventory_product_id=20)
  # p_6 = Product(wishlist_id=w_1.id,name = "soccer",price=23.5,status=Availability.AVAILABLE,\
  #   pic_url="www.soccer.com/1.png",short_desc="this is a soccer",inventory_product_id=5)
  # p_7 = Product(wishlist_id=w_2.id,name = "bread",price=3.5,status=Availability.AVAILABLE,\
  #   pic_url="www.bakery.com/1.png",short_desc="this is a bread",inventory_product_id=20)
  # p_8 = Product(wishlist_id=w_2.id,name = "soccer",price=23.5,status=Availability.AVAILABLE,\
  #   pic_url="www.soccer.com/1.png",short_desc="this is a soccer",inventory_product_id=5)
  # p_9 = Product(wishlist_id=w_2.id,name = "toy",price=11.5,status=Availability.AVAILABLE, \
  #   pic_url="www.toy.com/1.png",short_desc="this is a toy",inventory_product_id=3)

  # products = [p_1,p_2,p_3,p_4,p_5,p_6,p_7,p_8,p_9]
  # for product in products:
  #   product.create()
