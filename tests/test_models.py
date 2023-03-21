"""
Test cases for Customer Model

"""
import unittest
from tests.factories import CustomerFactory
from service.models import Customer, db

######################################################################
#  C U S T O M E R   M O D E L   T E S T   C A S E S
######################################################################


class TestCustomer(unittest.TestCase):
    """ Test Cases for Customer Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """

        # Drop existing tables from previous tests
        db.drop_all()

        # Close session from previous tests
        db.session.close()

        # Create all the ORM-mapped database tables
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """

        # disconnect from the database
        db.session.close()

    def setUp(self):
        """ This runs before each test """

        # delete all customers from the database from last tests
        db.session.query(Customer).delete()
        # commit the transaction
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """

        # close session
        db.session.remove()

    def create_customer(self) -> Customer:
        """ Convenience method to create customer record """
        customer = CustomerFactory()
        customer.create()
        return customer

    ######################################################################
    #  H A P P Y  T E S T   C A S E S
    ######################################################################

    def test_create_customer(self) -> None:
        """ Test creating customer record """
        customer: Customer = self.create_customer()

        customer_fetched: Customer = Customer.find(customer.id)
        self.assertEqual(customer.id, customer_fetched.id)

    def test_update_customer(self) -> None:
        """ Test updating customer record """

        # create customer
        customer: Customer = self.create_customer()

        customer: Customer = Customer.find(customer.id)

        new_name: str = "Abraham"
        customer.first_name = new_name
        customer.update()

        customer: Customer = Customer.find(customer.id)
        self.assertEqual(customer.first_name, new_name)

    def test_delete_customer(self) -> None:
        """It should delete a customer record"""

        # create customer
        customer: Customer = self.create_customer()

        # get customer id
        customer_id: db.Integer = customer.id

        # fetch customer from db
        customer: Customer = Customer.find(customer.id)

        # assert customer exists
        self.assertTrue(customer)

        # delete customer record
        Customer.query.filter(Customer.id == customer_id).delete()
        db.session.commit()

        # search for customer by id
        empty_customer: Customer = Customer.find(customer_id)
        self.assertIsNone(empty_customer)

    ######################################################################
    #  S A D  T E S T   C A S E S
    ######################################################################

    def test_typeerror_deserialize(self):
        """It should fail to deserialize with a TypeError"""

        bad_obj = {
            'id': 'John Smith',
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'johnsmith@johnsmith.com',
            'password': 'johnsmith123'
        }

        customer = self.create_customer()

        self.assertRaises(TypeError, customer.deserialize(bad_obj))
