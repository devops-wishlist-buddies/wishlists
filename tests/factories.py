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
Test Factory to make fake objects for testing
"""
import factory
import random
from factory.fuzzy import FuzzyChoice, FuzzyInteger, FuzzyDecimal
from service.models.product import Product
from service.models.wishlist import Wishlist
from service.models.model_utils import Availability, InCartStatus
class ProductFactory(factory.Factory):
  """Helper class to create dummy Product data for tests"""
  class Meta:
    model = Product

  name = factory.Sequence(lambda n : "Product_%d"% n)
  price = FuzzyDecimal(10,3000)
  status = FuzzyChoice(choices=[Availability.AVAILABLE, Availability.UNAVAILABLE])
  pic_url = factory.LazyAttribute(lambda obj : 'www.%s.com/sth/1/png' % obj.name)
  short_desc = factory.lazy_attribute(lambda obj :\
    'this is a %s with price %s and status %s' % (obj.name , obj.price , obj.status))
  inventory_product_id = FuzzyInteger(1, 400)
  in_cart_status = InCartStatus.DEFAULT

class WishlistFactory(factory.Factory):
  """Helper class to create dummy Wishlist data for tests"""

  class Meta:
    model = Wishlist

  name = factory.Sequence(lambda n : "Wishlist_%d"% n)
  user_id = FuzzyInteger(0,100)
