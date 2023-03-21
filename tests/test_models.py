"""
Test cases for Customer Model

"""
import os
import logging
from tests.factories import CustomerFactory
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import unittest
from service import app, config
from service.models import Customer, DataValidationError, db

######################################################################
#  Customer   M O D E L   T E S T   C A S E S
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
        return
        

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        
        # disconnect from the database
        db.session.close()
        return

    def setUp(self):
        """ This runs before each test """

        # delete all customers from the database from last tests
        db.session.query(Customer).delete()
        # commit the transaction
        db.session.commit()
        return


    def tearDown(self):
        """ This runs after each test """
        
        # close session
        db.session.remove()
        return

    def create_customer(self) -> Customer:
        """ Convenience method to create customer record """
        customer = CustomerFactory()
        customer.create()
        return customer

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_customer(self) -> None:
        """ Test creating customer record """
        customer: Customer = self.create_customer()

        customer_fetched: Customer = Customer.find(customer.id)
        self.assertEqual(customer.id, customer_fetched.id)
        return

    def test_read_customer(self):
        """Test reading a customer record"""
        customer = CustomerFactory()
        logging.debug(customer)
        customer.id = None
        customer.create()
        self.assertIsNotNone(customer.id)
        # Fetch it back
        found_customer = Customer.find(customer.id)
        self.assertEqual(found_customer.id, customer.id)
        self.assertEqual(found_customer.first_name, customer.first_name)

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
        return

    def test_delete_customer(self) -> None:

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
        return
