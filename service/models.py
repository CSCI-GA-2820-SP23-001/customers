"""
Models for Customer

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound
from sqlalchemy.types import Enum
from service.common import constants, enums

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """ Initializes the SQLAlchemy app """
    Customer.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class Customer(db.Model):
    """
    Class that represents a Customer
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(constants.FIRST_NAME_MAX_LEN), nullable=False)
    last_name = db.Column(db.String(constants.LAST_NAME_MAX_LEN), nullable=False)
    email = db.Column(db.String(constants.EMAIL_MAX_LEN), unique=True, nullable=False)
    password = db.Column(db.String(constants.PASSWORD_MAX_LEN), nullable=False)
    status = db.Column(
        Enum(enums.CustomerStatus, name='customer_status', values_callable=lambda obj: [e.value for e in obj]),
        default=enums.CustomerStatus.ACTIVE,
        nullable=False)

    def __repr__(self):
        return f"<Customer {self.email} id=[{self.id}]>"

    def create(self):
        """
        Creates a Customer to the database
        """
        logger.info("Creating Customer: %s", self.email)
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Customer to the database
        """
        logger.info("Saving Customer: %s", self.email)
        db.session.commit()

    def delete(self):
        """ Removes a Customer from the data store """
        logger.info("Deleting Customer: %s", self.email)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Customer into a dictionary """
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password": self.password,
            "status": str(self.status)
        }

    def deserialize(self, data):
        """
        Deserializes a Customer from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = data["id"]
            self.first_name = data["first_name"]
            self.last_name = data["last_name"]
            self.email = data["email"]
            self.password = data["password"]
            self.status = enums.CustomerStatus.from_string(data["status"])

        except KeyError as error:
            raise DataValidationError(
                "Invalid Customer: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Customer: body of request contained bad or no data - "
                "Error message: " + error
            ) from error
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Customers in the database """
        logger.info("Processing all Customers")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Customer by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, by_id: int):
        """Finds a Customer by it's id
        :return: an instance with the by_id, or 404_NOT_FOUND if not found
        """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

    @classmethod
    def find_by_email(cls, email):
        """Returns all Customers with the given name

        Args:
            name (string): the name of the Customers you want to match
        """
        logger.info("Processing email query for %s ...", email)
        return cls.query.filter(cls.email == email).all()

    @classmethod
    def set_status(cls, customer_id: int, status: enums.CustomerStatus) -> "Customer":
        """Sets the status of a customer
        :param customer_id: id of the customer
        :param status: status to give to customer
        :return: customer object with new status
        """
        customer = cls.find(customer_id)

        if not customer:
            raise NoResultFound(f"Customer with id '{customer_id}' was not found.")

        customer.status = status
        customer.update()
        return customer

    @classmethod
    def suspend(cls, customer_id: int) -> "Customer":
        """Suspends a customer
        :param customer_id: id of the customer
        :return: customer object with suspended status
        """
        return cls.set_status(customer_id, enums.CustomerStatus.SUSPENDED)

    @classmethod
    def activate(cls, customer_id: int) -> "Customer":
        """Activates a customer
        :param customer_id: id of the customer
        :return: customer object with active status
        """
        return cls.set_status(customer_id, enums.CustomerStatus.ACTIVE)

    @classmethod
    def find_by_first_name(cls, first_name):
        """Returns all Customers with the given first name
        Args:
            name (string): the name of the Customers you want to match
        """
        logger.info("Processing first name query for %s ...", first_name)
        return cls.query.filter(cls.first_name == first_name).all()
