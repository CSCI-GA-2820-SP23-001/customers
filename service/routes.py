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

from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import constants, status, strings
from service.models import Customer

# Import Flask application
from . import app

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
            version=constants.ROUTES_VERSION,
            # paths=url_for("list_customers", _external=True), # TODO: we need path for list customers first
        ),
        status.HTTP_200_OK,
    )

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
    except:
        abort(
            status.HTTP_400_BAD_REQUEST,
            'Failed to create customer'
        )

    message = customer.serialize()

    # TODO: this cannot be implemented until we have a functioning GET endpoint
    # location_url = url_for("get_customers", customer_id=customer.id, _external=True)

    # app.logger.info("Customer with ID [%s] created.", customer.id)
    # return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}

    return (
        jsonify(
            data=[
                message
            ]
        ),
        status.HTTP_201_CREATED
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
