"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
from service.models import db, init_db, Customer
from service.common import constants, status, strings
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
        # assert the version matches the value stored in contstants
        self.assertEqual(data['version'], constants.ROUTES_VERSION)

    def test_get_customer_list(self):
        """It should Get a list of Customers"""
        customers = self._create_customers(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

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


        # TODO: This cannot be implemented until we have a functioning GET endpoint
        # # Make sure location header is set
        # location = response.headers.get("Location", None)
        # self.assertIsNotNone(location)

        # # Get the newly created customer from the POST response
        # new_customer = response.get_json()

        # # Check the data is correct
        # self.assertEqual(new_customer["first_name"], test_customer.first_name)
        # self.assertEqual(new_customer["last_name"], test_customer.last_name)
        # self.assertEqual(new_customer["email"], test_customer.email)
        # self.assertEqual(new_customer["password"], test_customer.password)


        # # fetch the new customer from the GET endpoint
        # response = self.client.get(new_customer)

        # # assert the customer was fetched successfully
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

        # # assert that the data is correct
        # new_customer = response.get_json()
        # self.assertEqual(new_customer["first_name"], test_customer.first_name)
        # self.assertEqual(new_customer["last_name"], test_customer.last_name)
        # self.assertEqual(new_customer["email"], test_customer.email)
        # self.assertEqual(new_customer["password"], test_customer.password)
        
    def test_delete_customer(self):
        """It should Delete a Customer"""
        
        test_customer = self._create_customers(1)[0]
        # TODO: once GET endpoint is completed, use it to find the customer
        # instead of find_by_email
        new_customers = Customer.find_by_email(test_customer.email)
        
        # Make sure a customer was created
        self.assertTrue(new_customers)
        # Make sure only 1 customer was returned
        self.assertEqual(len(new_customers), 1)

        new_customer = new_customers[0]

        # delete the customer
        response = self.client.delete(f"{BASE_URL}/{new_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # TODO: once GET endpoint is completed, use it to find the customer
        # instead of find_by_email
        # query the database for the previously created customer
        new_customers = Customer.find_by_email(test_customer.email)

        # make sure they are deleted
        self.assertFalse(new_customers)
        # response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        # self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
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
