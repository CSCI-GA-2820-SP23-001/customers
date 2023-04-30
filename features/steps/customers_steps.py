######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Customer Steps

Steps file for Customer.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import logging
import requests
from behave import given, then, when
from compare import expect
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

ID_PREFIX = 'customer_'


@given('the following customers')
def step_impl(context):
    """ Delete all Customers and load new ones """
    # List all of the customers and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/customers"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for customer in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{customer['id']}")
        expect(context.resp.status_code).to_equal(204)

    # load the database with new customers
    for row in context.table:
        payload = {
            "first_name": row['first_name'],
            "last_name": row['last_name'],
            "email": row['email'],
            "password": row['password'],
            "status": row['status'],
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        expect(context.resp.status_code).to_equal(201)


@when('I copy the customer in the form')
def step_impl(context):
    """Copy the entire customer object in the form component"""

    element_keys = [
        'id',
        'first_name',
        'last_name',
        'email',
        'password',
        'status'
    ]
    element_ids = [ID_PREFIX + el for el in element_keys]

    customer = {}
    for el_id, el_key in zip(element_ids, element_keys):
        element = context.driver.find_element(By.ID, el_id)
        customer[el_key] = element.get_attribute('value')

    context.clipboard = str(customer)
    logging.info('Clipboard contains: %s', context.clipboard)



@when('I paste the customer "{element_name}" field')
def step_impl(context, element_name):
    """Pastes the field element_name field into the corresponding form component"""

    element_key = element_name.lower().replace(' ', '_')
    element_id = ID_PREFIX + element_key
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )

    customer = eval(context.clipboard)
    value = customer.get(element_key, '')

    element.clear()
    element.send_keys(value)


@then('the "{element_name}" should equal the copied customer')
def step_impl(context, element_name):
    """Compares the form field element_name to the copied customer element_name field"""

    element_key = element_name.lower().replace(' ', '_')
    element_id = ID_PREFIX + element_key
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )

    form_value = element.get_attribute('value')
    copied_value = context.clipboard.get(element_key, '')

    expect(form_value).to_equal(copied_value)