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
from flask_restx import Api, Resource, fields, reqparse, inputs

from . import app
from . import status  # HTTP Status Codes

# Import Flask application
from service.models.wishlist import Wishlist, WishlistVo
from service.models.product import Product
from service.models.model_utils import Availability, InCartStatus, get_non_null_product_fields, db

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
  version='1.0.0',
  title='Wishlists Service REST API',
  description='This is an API for Wishlists Service, NYU DevOps 2021.',
  default='wishlists',
  default_label='Wishlists CRUD operations',
  doc='/apidocs/', # default also could use doc='/apidocs/'
  prefix='/api'
)

# Define the model so that the docs reflect what can be sent
create_wishlist_model = api.model('Wishlist', {
  'name': fields.String(required=True,
    description='The name of the wishlist.'),
  'user_id': fields.Integer(required=True,
    description='User ID who the wishlist belongs to.'),
})

full_wishlist_model = api.inherit(
  'DBWishlistModel',
  create_wishlist_model,
  {
    'id': fields.Integer(readOnly=True,
      description='The unique id assigned internally by service'),
  }
)

wishlist_arg = reqparse.RequestParser()
wishlist_arg.add_argument('user_id', type=int, required=False, help='List Wishlists by user id.')

create_product_model = api.model('Product', {
  'name': fields.String(required=True,
    description='The name of the product'),
  'price': fields.Float(required=True,
    description='Price of the product.'),
  'status': fields.String(required=True,
    description='Availability status.',
    enum=Availability._member_names_),
  'pic_url': fields.String(required=False,
    description='URL for a picture of the product.'),
  'short_desc': fields.String(required=False,
    description='Short description of the product.'),
  'inventory_product_id': fields.Integer(required=True,
    description='ID of the product in inventory.'),
  'wishlist_id': fields.Integer(required=True,
    description='Wishlist ID that this product belongs to.'),
  'in_cart_status': fields.String(required=False,
    description='Flag indicating if this product has been placed in cart.' +
      'Can only be changed with the add-to-cart endpoint.  Not in cart by default.',
    enum=InCartStatus._member_names_),
})

full_product_model = api.inherit(
  'DBProductModel',
  create_product_model,
  {
    'id': fields.String(readOnly=True,
      description='The unique id assigned internally by service'),
  }
)

######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/info")
def info():
  """ API info"""
  return (
    jsonify(
      name="Wishlists REST API Service",
      version="1.0",
    ),
    status.HTTP_200_OK,
  )

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
  """ Serve static home page"""
  return app.send_static_file("index.html")

######################################################################
#  PATH: /wishlists/{id}
######################################################################
@api.route('/wishlists/<wishlist_id>')
@api.param('wishlist_id', 'The Wishlist identifier')
class WishlistResource(Resource):
  """
  WishlistResource class

  Allows the manipulation of a single Wishlist
  GET /{wishlist_id} - Returns a Wishlist with the id
  PUT /{wishlist_id} - Update a Wishlist with the id
  DELETE /{wishlist_id} -  Deletes a Wishlist with the id
  """

  def get(self):
    pass

  def post(self):
    pass

  def put(self):
    pass

  def delete(self):
    pass

######################################################################
#  PATH: /wishlists
######################################################################
@api.route('/wishlists', strict_slashes=False)
class WishlistCollection(Resource):
  """
  WishlistCollection class

  Allows the manipulation on a set of Wishlists
  GET / - Returns all wishlists in the database
  POST / - Create a Wishlist
  """
  def get(self):
    pass

  def post(self):
    pass

######################################################################
#  PATH: /wishlists/{wishlist_id}/products/{product_id}
######################################################################
@api.route('/wishlists/<wishlist_id>/products/<product_id>')
@api.param('wishlist_id', 'The Wishlist identifier')
@api.param('product_id', 'The Product identifier')
class ProductResource(Resource):
  """
  ProductResource class

  Allows the manipulation on a a single Product in a Wishlist
  GET - Returns the product in the wishlist
  POST - Create the product in the wishlist
  DELETE - Delete the product from the wishlist
  """

  def get(self):
    pass

  def post(self):
    pass

  def put(self):
    pass

  def delete(self):
    pass

######################################################################
#  PATH: /wishlists/{wishlist_id}/products
######################################################################
@api.route('/wishlists/<wishlist_id>/products', strict_slashes=False)
@api.param('wishlist_id', 'The Wishlist identifier')
class ProductCollection(Resource):
  """
  ProductCollection class

  Allows the manipulation on a set of Products in a Wishlist
  GET / - Returns all products in a wishlists in the database
  DELETE / - Delete all products in a wishlist
  """

  def get(self):
    pass

  def delete(self):
    pass

@api.route('/wishlists/<wishlist_id>/products/<product_id>/add-to-cart')
@api.param('wishlist_id', 'The Wishlist identifier')
@api.param('product_id', 'The Product identifier')
class AddToCartResource(Resource):
  """
  AddToCartResource class

  Allows to place a product in a wishlist in the cart
  PUT - place the product in the wishlist in the cart
  """
  def put(self):
    pass

###
# TODO: MOVE THE FUNCTIONS BELOW INTO THE CLASSES ABOVE
###

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
  data = wishlist.serialize()
  return make_response(
    jsonify(
      data = data,
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
# Delete all products from a wishlist
######################################################################
@app.route("/wishlists/<int:wishlist_id>/products", methods=["DELETE"])
def delete_products_from_wishlist(wishlist_id):
  """
  Delete all products from a wishlist
  """
  wishlist = Wishlist.find_by_id(wishlist_id)
  if not wishlist:
    return make_response(
      jsonify(
        data = [],
        message = "Wishlist {} not found".format(wishlist_id)
      ),
      status.HTTP_404_NOT_FOUND
    )

  product_list = wishlist.read()["products"]
  product_ids_list = [p["id"] for p in product_list]
  app.logger.info("Request to delete all the products from wishlist %s"\
    % (wishlist_id))

  cnt = wishlist.delete_products(product_ids_list)

  if cnt != 0:
    return make_response(
      jsonify(
        data = [],
        message = "All products are deleted."
      ),
      status.HTTP_200_OK
    )

  return make_response(
    jsonify(
      data = [],
      message = "There is no products in the wishlist, 0 products are deleted."
    ),
    status.HTTP_200_OK
  )
######################################################################
# Delete a product from a wishlist
######################################################################
@app.route("/wishlists/<int:wishlist_id>/products/<int:product_id>", methods=["DELETE"])
def delete_a_product_from_wishlist(wishlist_id, product_id):
  """
  Delete a product from a wishlist
  This endpoint will delete a product from a wishlist based the wishlist_id
  and the product_id specified in the URL
  """
  app.logger.info("Request to delete products with id %s from wishlist %s"\
    % (product_id,wishlist_id))

  wishlist = Wishlist.find_by_id(wishlist_id)
  if not wishlist:
    return make_response(
      jsonify(
        data = [],
        message = "Wishlist {} not found".format(wishlist_id)
      ),
      status.HTTP_404_NOT_FOUND
    )
  cnt = wishlist.delete_products([product_id])

  if cnt == 0:
    return make_response(
      jsonify(
        data = [],
        message = "Product with id {} is not in this wishlist.".format(product_id)
      ),
      status.HTTP_200_OK
  )
  return make_response(
    jsonify(
      data = [],
      message = "Product with id {} is deleted.".format(product_id)
    ),
    status.HTTP_200_OK
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
    res.append(product)

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
      data = WishlistVo(wishlist,res).serialize(),
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
      message = f"Successfully get Product with id {product_id} in wishlist with id {wishlist_id}"
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
      data[key] = request_data[key]

    data["wishlist_id"] = wishlist_id

  product = Product()
  product.deserialize(data)
  product.create()

  return make_response(
    jsonify(
      data = product.id,
      message = "Product Created!"
    ),
    status.HTTP_201_CREATED
  )

######################################################################
# RENAME A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["PUT"])
def rename_a_wishlist(wishlist_id):
  """
  Renames a wishlist
  This endpoint will rename an existing wishlist
  """
  app.logger.info("Request to rename a wishlist")
  wishlist = Wishlist.find_by_id(wishlist_id)
  if not wishlist:
    return make_response(
      jsonify(
        data=[],
        message="Wishlist with id {} not found".format(wishlist_id)
      ),
      status.HTTP_404_NOT_FOUND
    )

  request_data = request.get_json()
  if not request_data['name']:
    return make_response(
      jsonify(
        data=[],
        message = "Field name cannot be null"
      ),
      status.HTTP_400_BAD_REQUEST
    )

  query_res = Wishlist.find_all_by_user_id(wishlist.user_id)
  res = []
  for i in query_res:
    res.append(i['name'])

  num=0
  wishlist_fields = wishlist.serialize()

  while 1:
    if num==0:
      if request_data['name'] in res:
        num=num+1
      else:
        wishlist_fields.update(request_data)
        break
    else:
      if request_data['name']+' {0}'.format(num) in res:
        num=num+1
      else:
        request_data['name'] = request_data['name'] + ' {0}'.format(num)
        wishlist_fields.update(request_data)
        break

  wishlist.deserialize(wishlist_fields)
  wishlist.update()

  return make_response(
    jsonify(
      data = wishlist.serialize(),
      message = "Wishlist with id {} is renamed.".format(wishlist_id)
    ),
    status.HTTP_200_OK
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
  product.deserialize(product_fields)
  product.update()

  return make_response(
    jsonify(
      data = product.id,
      message = "Product Updated"
    ),
    status.HTTP_200_OK
  )

######################################################################
# ADD A PRODUCT IN A WISHLIST TO CART
######################################################################
@app.route("/wishlists/<int:wishlist_id>/products/<int:product_id>/add-to-cart", methods=["PUT"])
def add_product_to_cart(wishlist_id, product_id):
  """
  Updates a product in_cart_status to indicate placing an item in a shopcart
  This endpoint will modify an existing product in a wishlist
  """

  app.logger.info("Request to place a product in wishlist to cart")
  product = Product.find_by_wishlist_id_and_product_id(wishlist_id, product_id)
  if not product:
    return(
      jsonify(
        data = [],
        message = f"Product with id {product_id} was not found in wishlist with id {wishlist_id}"
      ),
      status.HTTP_404_NOT_FOUND
    )

  # Call to Shopcarts API here with this product's inventory_product_id. Assuming success:
  product.in_cart_status = InCartStatus.IN_CART
  product.update()

  return make_response(
    jsonify(
      data = product.id,
      message = "Product placed in shopping cart."
    ),
    status.HTTP_200_OK
  )


######################################################################
# INITIALIZE DATABASE
######################################################################
def init_db(app):
  """Initlaize the model"""
  db.init_app(app)
  app.app_context().push()
  db.create_all()
