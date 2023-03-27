"""
Customer Database Service

Paths:
------
GET /customers - Returns a list all of the Customers
GET /customers/{id} - Returns the Customer with a given id number
POST /customers - creates a new Customer record in the database
PUT /customers/{id} - updates a Customer record in the database
DELETE /customers/{id} - deletes a Customer record in the database
"""

from flask import jsonify, request, url_for, abort
from service.common import constants, status, strings
from service.models import Customer

# Import Flask application
from . import app


######################################################################
# GET HEALTH CHECK
######################################################################


@app.route("/healthcheck")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """ Root URL response """
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name=strings.ROOT_URL_NAME,
            version=constants.ROUTES_VERSION
        ),
        status.HTTP_200_OK,
    )

######################################################################
# GET A LIST OF CUSTOMERS
######################################################################


@app.route("/customers", methods=["GET"])
def list_customers():
    """Returns all of the Customers"""
    app.logger.info("Request for customer list")
    customers = []
    email = request.args.get("email")
    if email:
        customers = Customer.find_by_email(email)
    else:
        customers = Customer.all()
    results = [customer.serialize() for customer in customers]
    app.logger.info("Returning %d customers", len(results))
    return jsonify(results), status.HTTP_200_OK

######################################################################
# GET A CUSTOMER
######################################################################


@app.route("/customers/<int:customer_id>", methods=["GET"])
def get_customers(customer_id):
    """
    Retrieve a single customer
    This endpoint will return a Customer based on it's id
    """
    app.logger.info("Request for customer with id: %s", customer_id)
    customer = Customer.find(customer_id)
    if not customer:
        abort(status.HTTP_404_NOT_FOUND, f"Customer with id '{customer_id}' was not found.")

    app.logger.info("Returning customer: %s", customer.first_name)
    return jsonify(customer.serialize()), status.HTTP_200_OK

######################################################################
# ADD A NEW CUSTOMER
######################################################################


@app.route("/customers", methods=["POST"])
def create_customers():
    """
    Creates a Customer
    This endpoint will create a Customer based the data in the body that is posted
    """
    app.logger.info("Request to create a customer")
    check_content_type("application/json")

    # initialize an empty Customer record
    customer = Customer()

    # deserialize the request JSON into the newly created record
    customer.deserialize(request.get_json())

    try:
        # add the customer record to the database
        customer.create()
    except Exception:
        abort(
            status.HTTP_400_BAD_REQUEST,
            'Failed to create customer'
        )

    message = customer.serialize()

    location_url = url_for("get_customers", customer_id=customer.id, _external=True)

    app.logger.info("Customer with ID [%s] created.", customer.id)
    return (
        jsonify(message),
        status.HTTP_201_CREATED,
        {"location": location_url}
    )

######################################################################
# UPDATE A CUSTOMER
######################################################################


@app.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    """
    Update a Customer
    This endpoint will update a customer identified by customer_id with the data
    in the request body

    Args:
        customer_id (int): Customer ID

    Returns:
        Customer: JSON Serialized updated customer record
    """

    app.logger.info("Request to update Customer with id: %s", customer_id)
    check_content_type('application/json')

    customer = Customer.find(customer_id)
    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f'Customer with id {customer_id} does not exist'
        )

    customer.deserialize(request.get_json())

    customer.id = customer_id

    app.logger.info(f'Customer with id {customer_id} updated')
    return (
        jsonify(customer.serialize()),
        status.HTTP_200_OK
    )

######################################################################
# DELETE A CUSTOMER
######################################################################


@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customers(customer_id):
    """
    Delete a Customer
    This endpoint will delete a Customer based on the id specified in the path
    """
    customer = Customer()
    app.logger.info("Request to delete Customer with id: %s", customer_id)
    customer = customer.find(customer_id)
    if customer:
        customer.delete()

    app.logger.info("Customer with ID [%s] delete complete.", customer_id)
    return "", status.HTTP_204_NO_CONTENT

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
