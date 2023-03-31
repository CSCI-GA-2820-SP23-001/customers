"""
Test file for common module code
"""


import unittest
from service.common.enums import CustomerStatus


class TestCommon(unittest.TestCase):
    """ Test cases for Common module """

    ######################################################################
    #  H A P P Y  T E S T   C A S E S
    ######################################################################

    def test_customer_status(self):
        """ Test for customer status """
        self.assertTrue(CustomerStatus.string_equals("ACTIVE", CustomerStatus.ACTIVE))
        self.assertTrue(CustomerStatus.string_equals("SUSPENDED", CustomerStatus.SUSPENDED))
        self.assertEqual(str(CustomerStatus.ACTIVE), "ACTIVE")
        self.assertEqual(str(CustomerStatus.SUSPENDED), "SUSPENDED")
        self.assertEqual(CustomerStatus.ACTIVE, CustomerStatus.from_string("ACTIVE"))
        self.assertEqual(CustomerStatus.SUSPENDED, CustomerStatus.from_string("SUSPENDED"))

    ######################################################################
    #  S A D  T E S T   C A S E S
    ######################################################################

    def test_customer_status_bad(self):
        """Sad tests for customer status"""

        self.assertFalse(CustomerStatus.string_equals("ACTIVE", CustomerStatus.SUSPENDED))
        self.assertFalse(CustomerStatus.string_equals("SUSPENDED", CustomerStatus.ACTIVE))
        self.assertRaises(ValueError, CustomerStatus.from_string, "BAD")
