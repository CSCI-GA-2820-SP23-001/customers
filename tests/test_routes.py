"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from typing import List
from unittest import TestCase
from service import app
from service.models import db, init_db, Customer
from service.common import constants, enums, status, strings
from tests.factories import CustomerFactory

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/customers"

######################################################################
#  T E S T   C A S E S
######################################################################


class TestCustomerServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    def _create_customers(self, count):
        """Factory method to create customers in bulk"""
        customers = []
        for _ in range(count):
            test_customer = CustomerFactory()
            response = self.client.post(BASE_URL, json=test_customer.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test customer"
            )
            new_customer = response.get_json()
            test_customer.id = new_customer["id"]
            customers.append(test_customer)
        return customers

    ######################################################################
    #  C U S T O M E R   H A P P Y   P A T H   T E S T   C A S E S
    ######################################################################

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/healthcheck")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

    def test_root_url(self):
        """It should get the root URL message"""
        response = self.client.get("/")

        # assert the response has the correct status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()

        # assert the root URL message has the correct name
        self.assertEqual(data['name'], strings.ROOT_URL_NAME)
        # assert the version matches the value stored in constants
        self.assertEqual(data['version'], constants.ROUTES_VERSION)

    def test_get_customer_list(self):
        """It should Get a list of Customers"""

        self._create_customers(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_get_customer_by_email(self):
        """It should Get a list of customers by email"""

        test_customers: List[Customer] = self._create_customers(5)

        search_email: str = 'search_email@findme.com'
        test_customers[0].email = search_email
        response = self.client.put(f"{BASE_URL}/{test_customers[0].id}", json=test_customers[0].serialize())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(BASE_URL, query_string={'email': search_email})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        get_customers = response.get_json()
        self.assertEqual(len(get_customers), 1)
        self.assertEqual(get_customers[0]['email'], search_email)

    def test_get_customer(self):
        """It should Get a single Customer"""
        # get the id of a customer
        test_customer = self._create_customers(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["first_name"], test_customer.first_name)

    def test_create_customer(self):
        """It should Create a new Customer"""

        # initialize a customer object for creation
        test_customer = CustomerFactory()

        # serialize customer object
        test_customer_serialized = test_customer.serialize()

        logging.info("Creating Customer: %s", test_customer_serialized)

        # issue post request to customer endpoint
        response = self.client.post(BASE_URL, json=test_customer_serialized)

        # assert the POST response has the correct status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # # Make sure location header is set
        location = response.headers.get("location", None)
        self.assertIsNotNone(location)

        # # Get the newly created customer from the POST response
        new_customer = response.get_json()

        # # Check the data is correct
        self.assertEqual(new_customer["first_name"], test_customer.first_name)
        self.assertEqual(new_customer["last_name"], test_customer.last_name)
        self.assertEqual(new_customer["email"], test_customer.email)
        self.assertEqual(new_customer["password"], test_customer.password)

        # fetch the new customer from the GET endpoint
        new_customer_id = new_customer['id']
        response = self.client.get(f"{BASE_URL}/{new_customer_id}")

        # assert the customer was fetched successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # assert that the data is correct
        new_customer = response.get_json()
        self.assertEqual(new_customer["first_name"], test_customer.first_name)
        self.assertEqual(new_customer["last_name"], test_customer.last_name)
        self.assertEqual(new_customer["email"], test_customer.email)
        self.assertEqual(new_customer["password"], test_customer.password)

    def test_update_customer(self):
        """It should update an existing Customer"""

        # Create 4 customers for testing various types of updates
        test_customers: List[Customer] = self._create_customers(4)

        update_dict = {
            'first_name': 'Abraham',
            'last_name': 'Abrahamson',
            'email': 'honestabe@roadrunner.com',
            'password': 'password123'
        }

        # iterate over the newly created customers with the fields to update
        for test_customer, update_field, update_value in zip(test_customers, update_dict.keys(), update_dict.values()):
            test_customer.__setattr__(update_field, update_value)
            response = self.client.put(f'{BASE_URL}/{test_customer.id}', json=test_customer.serialize())
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            updated_customer = response.get_json()
            self.assertEqual(updated_customer[update_field], update_value)

    def test_delete_customer(self):
        """It should Delete a Customer"""

        test_customer = self._create_customers(1)[0]
        response = self.client.get(f'{BASE_URL}/{test_customer.id}')

        # Make sure a customer was created
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        new_customer = response.get_json()
        self.assertTrue(new_customer)

        # delete the customer
        new_customer_id = new_customer['id']
        response = self.client.delete(f"{BASE_URL}/{new_customer_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # get the previously created customer
        response = self.client.get(f"{BASE_URL}/{new_customer_id}")

        # make sure they are deleted
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_suspend_customer(self):
        """It should Suspend a Customer"""

        # create a customer
        test_customer = self._create_customers(1)[0]

        # suspend the customer
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # get the customer
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # assert that the customer is suspended
        customer = response.get_json()
        self.assertEqual(enums.CustomerStatus.from_string(customer['status']), enums.CustomerStatus.SUSPENDED)

    def test_activate_customer(self):
        """It should Activate a Customer"""

        # create a customer
        test_customer = self._create_customers(1)[0]

        # suspend the customer
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # get the customer
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # assert that the customer is suspended
        customer = response.get_json()
        self.assertEqual(enums.CustomerStatus.from_string(customer['status']), enums.CustomerStatus.SUSPENDED)

        # activate the customer
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/activate")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # get the customer
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # assert that the customer is active
        customer = response.get_json()
        self.assertEqual(enums.CustomerStatus.from_string(customer['status']), enums.CustomerStatus.ACTIVE)

    ######################################################################
    #  T E S T   S A D   P A T H S
    ######################################################################

    def test_get_customer_not_found(self):
        """It should not Get a Customer thats not found"""

        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_create_customer_no_data(self):
        """It should not Create a Customer with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_no_content_type(self):
        """It should not Create a Customer with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_customer_wrong_content_type(self):
        """It should not Create a Customer with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_customer_bad_available(self):
        """It should not Create a Customer with bad available data"""
        test_customer = CustomerFactory()

        logging.info('Attempting to create Customer: %s', test_customer)

        # change first_name to an empty string
        test_customer.first_name = None

        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.get_json()
        self.assertIn('Failed to create customer'.lower(), data['message'].lower())

    def test_update_customer_id(self):
        """It should not update a Customer id"""

        # Create a customer
        test_customer: Customer = self._create_customers(1)[0]

        update_id = 123
        test_customer.id, initial_id = update_id, test_customer.id
        response = self.client.put(f'{BASE_URL}/{initial_id}', json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_customer = response.get_json()
        self.assertNotEqual(updated_customer['id'], update_id)

    def test_unsupported_method(self):
        """It should return a method not allowed error"""

        # Create a customer
        test_customer: Customer = self._create_customers(1)[0]

        patch_first_name: str = 'Bob'
        test_customer.first_name = patch_first_name

        response = self.client.patch(f'{BASE_URL}/{test_customer.id}', json=test_customer.serialize())

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unsupported_media_type(self):
        """It should return a mediatype not supported error"""

        # Create a customer
        test_customer: Customer = self._create_customers(1)[0]

        patch_first_name: str = 'Bob'
        test_customer.first_name = patch_first_name

        response = self.client.put(
            f'{BASE_URL}/{test_customer.id}',
            json=test_customer.serialize(),
            headers={'Content-Type': 'application/pdf'}
        )

        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_suspend_customer_not_found(self):
        """It should not Suspend a Customer that does not exist"""

        # suspend the customer
        response = self.client.put(f"{BASE_URL}/0/suspend")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_activate_customer_not_found(self):
        """It should not Activate a Customer that does not exist"""

        # activate the customer
        response = self.client.put(f"{BASE_URL}/0/activate")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_query_customer_list_by_name(self):
        """It should query customers by name"""
        customers = self._create_customers(10)
        test_name = customers[0].name
        name_customers = [customer for customer in customers if customer.name == test_name]
        response = self.client.get(
            BASE_URL,
            query_string=f"name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(name_customers))
        # check the data just to be sure
        for customer in data:
            self.assertEqual(customer["name"], test_name)
