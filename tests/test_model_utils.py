"""Test for utility functions used by models"""
from decimal import Decimal
import unittest

from service.models.model_utils import Availability, JsonEncoder

class TestModelUtils(unittest.TestCase):
  """Test for utility functions used by models"""
  def test_json_serialize(self):
    """Test for custom json serializer"""
    encoder = JsonEncoder()
    self.assertEqual(encoder.default(Availability.AVAILABLE),Availability.AVAILABLE.name)
    dec = Decimal(200.2)
    self.assertEqual(encoder.default(dec),200.2)
