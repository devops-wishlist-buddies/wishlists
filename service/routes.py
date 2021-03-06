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

GET /wishlists -- List on Wishlists
POST /wishlists -- Create on Wishlists
GET /wishlists/{wishlist_id} -- Read on Wishlists
DELETE /wishlists/{wishlist_id} -- Delete on Wishlists
PUT /wishlists/{wishlist_id} -- Update on Wishlists
DELETE /wishlists/{wishlist_id}/products -- Action "Delete All" on Products
POST /wishlists/{wishlist_id}/products -- Create on products
GET /wishlists/{wishlist_id}/products/{product_id} -- Read on Products
DELETE /wishlists/{wishlist_id}/products/{product_id} -- Delete on Products
PUT /wishlists/{wishlist_id}/products/{product_id} -- Update on Products
PUT /wishlists/{wishlist_id}/products/{product_id}/add-to-cart -- Action "Move" on Products

"""

from flask import jsonify, request, abort
from flask_restx import Api, Resource, fields, reqparse

from . import app
from . import status  # HTTP Status Codes

# Import Flask application
from service.models.wishlist import Wishlist, WishlistVo
from service.models.product import Product
from service.models.model_utils import db, DataValidationError, InCartStatus, Availability

######################################################################
# GET INDEX
######################################################################
@app.route("/", strict_slashes=False)
def index():
  """ Serve static home page"""
  return app.send_static_file("index.html")

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
# Configure Swagger before initializing it
######################################################################
api = Api(app,
  version='1.0.0',
  title='Wishlists Service REST API',
  description='This is an API for Wishlists Service, NYU DevOps 2021.',
  default='wishlists',
  default_label='Wishlists CRUD operations',
  doc='/apidocs/', # default also could use doc='/apidocs/'
)

# Define the model so that the docs reflect what can be sent
create_wishlist_model = api.model('Create_Wishlist_Model', {
  'name': fields.String(required=True,
    description='The name of the wishlist.'),
  'user_id': fields.Integer(required=True,
    description='User ID who the wishlist belongs to.'),
})
rename_wishlist_model = api.model('Rename_Wishlist_Model', {
  'name': fields.String(required=True,
    description='The name of the wishlist.')
})

full_wishlist_model = api.inherit(
  'Read_Wishlist_Model',
  create_wishlist_model,
  {
    'id': fields.Integer(readOnly=True,
      description='The unique id assigned internally by service'),
  }
)

wishlist_args = reqparse.RequestParser()
wishlist_args.add_argument('user_id', type=int, required=False, help='List Wishlists by user id.')

create_product_model = api.model('Create_Product_Model', {
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

update_product_model = api.model('Update_Product_Model', {
  'name': fields.String(required=False,
    description='The name of the product'),
  'price': fields.Float(required=False,
    description='Price of the product.'),
  'status': fields.String(required=False,
    description='Availability status.',
    enum=Availability._member_names_),
  'pic_url': fields.String(required=False,
    description='URL for a picture of the product.'),
  'short_desc': fields.String(required=False,
    description='Short description of the product.'),
  'inventory_product_id': fields.Integer(required=False,
    description='ID of the product in inventory.'),
  'wishlist_id': fields.Integer(required=False,
    description='Wishlist ID that this product belongs to.'),
})

full_product_model = api.inherit(
  'Read_Product_Model',
  create_product_model,
  {
    'id': fields.String(readOnly=True,
      description='The unique id assigned internally by service'),
  }
)

wishlist_vo = api.inherit(
  'List_Wishlist/Product_Model',
  full_wishlist_model,
  {
    'products': fields.List(fields.Nested(full_product_model))
  }
)

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
  # ------------------------------------------------------------------
  # RETRIEVE A Wishlist
  # ------------------------------------------------------------------
  @api.doc('get_wishlists')
  @api.response(400, 'Integer value expected for field: Wishlist ID')
  @api.response(404, 'Wishlist not found')
  @api.marshal_with(wishlist_vo)
  def get(self, wishlist_id):
    """
    Read on Wishlists
    This endpoint will list all products in a wishlist based on a wishlist_id.
    """
    if not wishlist_id.isdigit():
      abort(status.HTTP_400_BAD_REQUEST, "Integer value expected for field: Wishlist ID")
    app.logger.info("Request to list products in a wishlist")
    wishlist = Wishlist.find_by_id(wishlist_id)
    if not wishlist:
      abort(status.HTTP_404_NOT_FOUND, "Wishlist with id {} was not found".format(wishlist_id))

    wishlist_products = Product.find_all_by_wishlist_id(wishlist_id)
    return WishlistVo(wishlist, wishlist_products).serialize(), status.HTTP_200_OK

  #------------------------------------------------------------------
  # RENAME A WISHLIST
  #------------------------------------------------------------------
  @api.doc('rename_wishlists')
  @api.response(400, 'The posted Wishlist data was not valid')
  @api.response(404, 'Wishlist not found')
  @api.response(415, 'Unsupported media type : application/json expected')
  @api.expect(rename_wishlist_model)
  @api.marshal_with(full_wishlist_model, code = 200)
  def put(self, wishlist_id):
    """
    Update on Wishlists
    This endpoint will rename an existing wishlist.
    """
    app.logger.info("Request to rename a wishlist")
    if request.headers.get("Content-Type") != "application/json":
      return abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, \
        "Unsupported media type : application/json expected"
      )

    if not wishlist_id.isdigit():
      abort(status.HTTP_400_BAD_REQUEST, "Integer value expected for field: Wishlist ID")

    wishlist = Wishlist.find_by_id(wishlist_id)
    if not wishlist:
      abort(status.HTTP_404_NOT_FOUND, "Wishlist with id '{}' was not found.".format(wishlist_id))

    app.logger.info('Payload = %s', api.payload)
    data = api.payload

    if "name" not in data or not isinstance(data["name"], str):
      abort(status.HTTP_400_BAD_REQUEST, "name field is wrong")

    query_res = Wishlist.find_all_by_user_id(wishlist.user_id)
    res = []
    for i in query_res:
      res.append(i['name'])

    num = 0
    wishlist_fields = wishlist.serialize()

    while 1:
      if num == 0:
        if data['name'] in res:
          num += 1
        else:
          break
      else:
        if data['name'] + ' {0}'.format(num) in res:
          num += 1
        else:
          data['name'] = data['name'] + ' {0}'.format(num)
          break

    wishlist_fields.update(data)
    wishlist.deserialize(wishlist_fields)
    wishlist.update()

    return wishlist.serialize(), status.HTTP_200_OK

  #------------------------------------------------------------------
  # DELETE A Wishlist
  #------------------------------------------------------------------
  @api.doc('delete_wishlists')
  @api.response(204, 'Wishlist deleted')
  @api.response(400, 'Integer value expected for field: Wishlist ID')
  def delete(self, wishlist_id):
    """
    Delete on Wishlists
    This endpoint will delete a wishlist based the id specified in the URL.
    """
    app.logger.info("Request to delete wishlist with id: %s", wishlist_id)
    if not wishlist_id.isdigit():
      abort(status.HTTP_400_BAD_REQUEST, "Integer value expected for field: Wishlist ID")

    wishlist = Wishlist.find_by_id(wishlist_id)
    if wishlist:
      wishlist.delete()
      app.logger.info("Wishlist deleted")
    return "", status.HTTP_204_NO_CONTENT

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
  #------------------------------------------------------------------
  # LIST WISHLISTS
  #------------------------------------------------------------------
  @api.doc('list_wishlists')
  @api.expect(wishlist_args, validate=True)
  @api.marshal_list_with(wishlist_vo)
  def get(self):
    """
    List on Wishlists
    This endpoint will return all wishlists in the database or wishlists with a specific user_id.
    """
    args = wishlist_args.parse_args()
    user_id = args['user_id']

    if not user_id:
      app.logger.info("Request for all wishlists")
      query_res = Wishlist.find_all()
      res = [r.read() for r in query_res]
      app.logger.info(res)

      if not res:
        msg = "No wishlists found!"
      else:
        msg = "All the wishlists."

      app.logger.info(msg)
      return res, status.HTTP_200_OK

    user_id = int(user_id)
    app.logger.info("Request for wishlists with user_id: %s", user_id)
    res = Wishlist.find_all_by_user_id(user_id)

    if not res:
      app.logger.info("No wishlists found for user_id '%s'." % user_id)

    return res, status.HTTP_200_OK

  #------------------------------------------------------------------
  # CREATE A NEW WISHLIST
  #------------------------------------------------------------------
  @api.doc('create_wishlist')
  @api.response(415, 'Unsupported media type : application/json expected')
  @api.response(400, 'The posted data was not valid')
  @api.expect(create_wishlist_model)
  @api.marshal_with(full_wishlist_model, code=201)
  def post(self):
    """
    Create on Wishlists
    This endpoint will create a wishlist based the data in the body.
    """
    app.logger.info("Request to create a wishlist")
    # Check for form submission data
    if request.headers.get("Content-Type") != "application/json":
      abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, \
        "Unsupported media type : application/json expected"
      )

    app.logger.info('Payload = %s', api.payload)
    data = api.payload

    if not isinstance(data, dict):
      abort(status.HTTP_400_BAD_REQUEST, "Expected a json request body")

    wishlist = Wishlist()
    wishlist.deserialize(data)
    wishlist.create()
    data = wishlist.serialize()

    location_url = api.url_for(WishlistResource, wishlist_id=wishlist.id, _external=True)
    return data, status.HTTP_201_CREATED, {'Location': location_url}

######################################################################
#  PATH: /wishlists/{wishlist_id}/products
######################################################################
@api.route('/wishlists/<wishlist_id>/products')
@api.param('wishlist_id', 'The Wishlist identifier')
class ProductCollectionResource(Resource):
  """
  ProductCollectionResource class

  Allows the manipulation on a collection of Products in a Wishlist
  POST - Create a product in a wishlist
  DELETE - Delete all products in a wishlist
  """
  @api.doc('create_a_product')
  @api.response(400,"Expected a json request body")
  @api.response(415,"Unsupported media type : application/json expected")
  @api.expect(create_product_model)
  @api.marshal_with(full_product_model,201)
  def post(self,wishlist_id):
    """
    Create on Products
    This endpoint will add a new product to a wishlist.
    """
    app.logger.info("Request to create a product")
    if request.headers.get("Content-Type") != "application/json":
      abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, \
        "Unsupported media type : application/json expected"
      )

    app.logger.info('Payload = %s', api.payload)
    data = api.payload

    if not isinstance(data, dict):
      abort(status.HTTP_400_BAD_REQUEST, "Expected a json request body")

    if not wishlist_id.isdigit():
      abort(status.HTTP_400_BAD_REQUEST, "Integer value expected for field: Wishlist ID")

    data['wishlist_id'] = wishlist_id

    product = Product()
    product.deserialize(data)
    product.create()

    location_url = api.url_for(
      ProductResource,
      wishlist_id=wishlist_id,
      product_id = product.id,
      _external=True
    )

    return product.serialize(), status.HTTP_201_CREATED, {'Location':location_url}

  @api.doc('delete_all_products_from_a_wishlist')
  @api.response(204, "Products deleted")
  @api.response(400, 'Integer value expected for field: Wishlist ID')
  def delete(self, wishlist_id):
    """
    Action "Delete All" on Products
    This endpoint will delete all products in a wishlist.
    """
    if not wishlist_id.isdigit():
      abort(status.HTTP_400_BAD_REQUEST, "Integer value expected for field: Wishlist ID")

    wishlist = Wishlist.find_by_id(wishlist_id)

    if wishlist:
      product_list = wishlist.read()['products']
      product_ids_list = [p["id"] for p in product_list]
      app.logger.info(f"Request to delete all the products from wishlist {wishlist_id}")

      wishlist.delete_products(product_ids_list)

    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /wishlists/{wishlist_id}/products/{product_id}
######################################################################
@api.route('/wishlists/<wishlist_id>/products/<product_id>')
@api.param('wishlist_id', 'The Wishlist identifier')
@api.param('product_id', 'The Product identifier')
class ProductResource(Resource):
  """
  ProductResource class

  Allows the manipulation on a single Product in a Wishlist
  GET - Returns a product in a wishlist
  DELETE - Delete a product from a wishlist
  PUT - Update a product in a wishlist
  """
  @api.doc('return_one_product')
  @api.response(400, 'Integer value expected for fields: Wishlist ID and Product ID')
  @api.response(404, 'Product with id not found in wishlist with id')
  @api.marshal_with(full_product_model)
  def get(self,wishlist_id,product_id):
    """
    Read on Products
    This endpoint will firstly look for a wishlist based on a wishlist_id
    Then look for a product based on a product_id.
    """
    app.logger.info("Request to get a specific product in a wishlist")
    if not wishlist_id.isdigit() or not product_id.isdigit():
      abort(
        status.HTTP_400_BAD_REQUEST,
        'Integer field expected for fields: Wishlist ID and Product ID'
      )

    product = Product.find_by_wishlist_id_and_product_id(wishlist_id, product_id)

    if not product:
      abort(status.HTTP_404_NOT_FOUND, f"Product with wishlist_id {wishlist_id} and " \
          f"id {product_id} was not found in Product db"
      )

    return product.serialize(), status.HTTP_200_OK

  @api.doc('delete_a_product')
  @api.response(204, "Product deleted")
  @api.response(400, 'Integer value expected for fields: Wishlist ID and Product ID')
  def delete(self, wishlist_id, product_id):
    """
    Delete on Products
    This endpoint will delete an existing product in a wishlist.
    """
    app.logger.info(f"Request to delete products with id {product_id} from wishlist {wishlist_id}")
    if not wishlist_id.isdigit() or not product_id.isdigit():
      abort(
        status.HTTP_400_BAD_REQUEST,
        'Integer field expected for fields: Wishlist ID and Product ID'
      )

    wishlist = Wishlist.find_by_id(wishlist_id)
    if wishlist:
      wishlist.delete_products([product_id])

    return "", status.HTTP_204_NO_CONTENT

  @api.doc('update_a_product')
  @api.response(400, "Expected a json request body")
  @api.response(404, "Product not found")
  @api.response(415, "Unsupported media type : application/json expected")
  @api.expect(update_product_model)
  @api.marshal_with(full_product_model)
  def put(self, wishlist_id, product_id):
    """
    Update on Products
    This endpoint will modify an existing product in a wishlist.
    """
    app.logger.info("Request to update a product")
    if not wishlist_id.isdigit() or not product_id.isdigit():
      abort(
        status.HTTP_400_BAD_REQUEST,
        'Integer field expected for fields: Wishlist ID and Product ID'
      )

    product = Product.find_by_wishlist_id_and_product_id(wishlist_id, product_id)
    if request.headers.get("Content-Type") != "application/json":
      abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, \
        "Unsupported media type : application/json expected"
      )

    if not product:
      abort(status.HTTP_404_NOT_FOUND, f"Product with id {product_id} not found")

    app.logger.info('Payload = %s', api.payload)
    data = api.payload
    if not isinstance(data, dict):
      abort( status.HTTP_400_BAD_REQUEST, "Expected a json request body")

    product_fields = product.serialize()
    product_fields.update(api.payload)
    product.deserialize(product_fields)
    product.update()

    return product.serialize(), status.HTTP_200_OK

@api.route('/wishlists/<wishlist_id>/products/<product_id>/add-to-cart')
@api.param('wishlist_id', 'The Wishlist identifier')
@api.param('product_id', 'The Product identifier')
class AddToCartResource(Resource):
  """
  AddToCartResource class

  Allows to place a product in a wishlist in the cart
  PUT - place the product in the wishlist in the cart
  """

  @api.doc('place_a_product_to_shopping_cart')
  @api.response(400, "Integer value expected for fields: Wishlist ID and Product ID")
  @api.response(404, "Product not found in the wishlist")
  @api.marshal_with(full_product_model)
  def put(self, wishlist_id, product_id):
    """
    Action "Move" on Products
    This endpoint will move an existing product in a wishlist to a shopping cart.
    """
    app.logger.info("Request to place a product in wishlist to cart")
    if not wishlist_id.isdigit() or not product_id.isdigit():
      abort(
        status.HTTP_400_BAD_REQUEST,
        'Integer field expected for fields: Wishlist ID and Product ID'
      )

    product = Product.find_by_wishlist_id_and_product_id(wishlist_id, product_id)

    if not product:
      abort(
        status.HTTP_404_NOT_FOUND,
        f"Product with id {product_id} was not found in wishlist with id {wishlist_id}"
      )

    product.in_cart_status = InCartStatus.IN_CART
    product.update()

    return product.serialize(),status.HTTP_200_OK


@api.errorhandler(DataValidationError)
def handle_data_validation_error(error):
  return {"message":error.args[0]}, status.HTTP_400_BAD_REQUEST

@api.errorhandler(TypeError)
def handle_type_error(error):
  return {"message":error.args[0]}, status.HTTP_400_BAD_REQUEST

######################################################################
# INITIALIZE DATABASE
######################################################################
def init_db(app):
  """Initlaize the model"""
  db.init_app(app)
  app.app_context().push()
  db.create_all()
