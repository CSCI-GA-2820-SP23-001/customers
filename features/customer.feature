Feature: The customer service back-end
    As a vendor
    I need a RESTful customer service
    So that I can keep track of all my customers

Background:
    Given the following customers
        | first_name     | last_name      | email                     | password   | status    |
        | abraham        | abrahamson     | aabrahamson@honest.com    | th3honest1 | ACTIVE    |
        | john           | jacob          | jjingleheimer@schmidt.com | myName2    | ACTIVE    |
        | sally          | ride           | sride@nasa.gov            | blastOff   | ACTIVE    |
        | daisy          | duck           | dduck@looney.com          | qqquack    | SUSPENDED |
        | john           | smith          | jsmith@gmail.com          | whiteBread | SUSPENDED |

Scenario: The server is running
    When I visit the "home page"
    Then I should see "Customers Admin Portal" in the title
    And I should not see "404 Not Found"

Scenario: Create a Customer
     When I visit the "home page"
     And I set the "First Name" to "abraham"
     And I set the "Last Name" to "abrahamson"
     And I set the "Email" to "aabrahamson@dishonest.com"
     And I set the "Password" to "th3honest1"
     And I select "Active" in the "Status" dropdown
     And I press the "Create" button
     Then I should see the message "Success"
     When I copy the "First Name" field
     And I press the "Clear" button
     Then the "First Name" field should be empty
     And the "Last name" field should be empty
     And the "Email" field should be empty
     When I paste the "First Name" field
     And I press the "Search" button
     Then I should see the message "Success"
     And I should see "abrahamson" in the results
     And I should see "aabrahamson@dishonest.com" in the results
     And I should see "th3honest1" in the results
     And I should see "ACTIVE" in the results

Scenario: Search for john
    When I visit the "home page"
    And I set the "first_name" to "john"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "john" in the results
    And I should see "jacob" in the results
    And I should see "john" in the results
    And I should see "smith" in the results
    But I should not see "abraham" in the results
    And I should not see "sally" in the results
    And I should not see "daisy" in the results

Scenario: Deleting a customer
    When I visit the "home page"
    And I set the "first_name" to "sally"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "sally" in the "first_name" field
    When I press the "Delete" button
    Then I should see the message "Customer has been Deleted!"
    And the "id" field should be empty
    And the "first_name" field should be empty
    And the "last_name" field should be empty
    And the "email" field should be empty
    And the "password" field should be empty
    And I should see "Active" in the "status" dropdown
    When I visit the "home page"
    And I set the "first_name" to "sally"
    And I press the "search" button
    Then I should see the message "Success"
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should not see "sally" in the results

 Scenario: Update a Customer
    When I visit the "home page"
    And I set the "first_name" to "sally"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "sally" in the "first_name" field
    And I should see "ride" in the "last_name" field
    When I change "first_name" to "toke"
    And I change "last_name" to "abi"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "toke" in the "first_name" field
    And I should see "abi" in the "last_name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "toke" in the results
    And I should not see "sally" in the results

Scenario: Retrieve a Customer
    When I visit the "home page"
    And I press the "Search" button
    When the "id" field is not empty
    And I copy the customer in the form
    And I press the "Clear" button
    Then the "id" field should be empty
    And the "first_name" field should be empty
    When I paste the customer "id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And the "first_name" should equal the copied customer
    And the "last_name" should equal the copied customer
    And the "email" should equal the copied customer
