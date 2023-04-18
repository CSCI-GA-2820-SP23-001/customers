"""
Customer Steps
Steps file for Customer.feature
For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given
from compare import expect


@given('the following customers')
def step_impl(context):
    """ Delete all customers and load new ones """
    # List all of the customers and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/customers"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for customer in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{pet['id']}")
        expect(context.resp.status_code).to_equal(204)

    # load the database with new customers
    for row in context.table:
        payload = {
            "id": row['id'],
            "first_name": row['first name'],
            "last_name": row['last name'],
            "email": row['email'],
            "password": row['password']
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        expect(context.resp.status_code).to_equal(201)