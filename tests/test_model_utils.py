from decimal import Decimal
import logging
import unittest

from service.models.model_utils import Availability, JsonEncoder
from service.models.wishlist import Wishlist

class testModulUtils(unittest.TestCase):
    
    def test_json_serialize(self):
        encoder = JsonEncoder()
        self.assertEqual(encoder.default(Availability.Available),Availability.Available.name)
        dec = Decimal(200.2)
        self.assertEqual(encoder.default(dec),200.2)