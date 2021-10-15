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
from factory.fuzzy import FuzzyChoice
from service.models.product import Product
from service.models.wishlist import Wishlist
from service.models.model_utils import Availability
class ProductFactory(factory.Factory):
    class Meta:
        model = Product
    
    #id = factory.Sequence(lambda n:n)
    name = factory.Sequence(lambda n : "Product_%d"% n)
    price = random.random() * 100
    status = FuzzyChoice(choices=[Availability.Available, Availability.Unavailable])
    pic_url = factory.LazyAttribute(lambda obj : 'www.%s.com/sth/1/png' % obj.name)
    short_desc = factory.lazy_attribute(lambda obj : 'this is a %s with price %s and status %s' % (obj.name , obj.price , obj.status))

class WishlistFactory(factory.Factory):
    """ Creates fake wishlists for tests """

    class Meta:
        model = Wishlist
