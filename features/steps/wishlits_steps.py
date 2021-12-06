######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
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
######################################################################

"""
Wishlist Steps

Steps file for wishlists.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import json
import requests
import random
from behave import given
from compare import expect

@given('the following wishlists')
def step_impl(context):
    """ Delete all Wishlists and load new ones """
    headers = {'Content-Type': 'application/json'}
    # list all of the wishlists and delete them one by one
    context.resp = requests.get(context.base_url + '/wishlists')
    expect(context.resp.status_code).to_equal(200)
    for wishlist in context.resp.json():
        context.resp = requests.delete(context.base_url + '/wishlists/' + str(wishlist["id"]), headers=headers)
        expect(context.resp.status_code).to_equal(200)

    # load the database with new wishlists
    create_url = context.base_url + '/wishlists'
    context.wishlist_ids = []
    for row in context.table:
        data = {
            "name" : row['name'],
            "user_id" : int(row['user_id'])
            }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)
        parsed_response = context.resp.json()
        context.wishlist_ids.append(parsed_response.get('id'))


@given('the following products')
def step_impl(context):
    """ Add products to the newly created empty wishlists """
    headers = {'Content-Type': 'application/json'}
    for row in context.table:
        data = {
            "name": row.get('name'),
            "price": int(row.get('price')),
            "status":  int(row.get('status')),
            "pic_url": row.get('pic_url'),
            "short_desc": row.get('short_desc'),
            "inventory_product_id": row.get('inventory_product_id'),
        }
        trimmed_data = {k: v for k, v in data.items() if v}
        payload = json.dumps(trimmed_data)
        wishlist_id = str(random.choice(context.wishlist_ids))
        add_url = context.base_url + '/wishlists/' + wishlist_id + '/products'
        context.resp = requests.post(add_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)
