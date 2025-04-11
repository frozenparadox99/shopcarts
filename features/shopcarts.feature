Feature: The shopcart service back-end
    As an E-commerce Platform Owner
    I need a RESTful shopcart service
    So that I can keep track of all my customers' shopping carts

Background:
    Given the following shopcart items
        | user_id | item_id | description      | price | quantity |
        | 1       | 101     | Deluxe Widget    | 19.99 | 2        |
        | 1       | 102     | Premium Gadget   | 29.99 | 1        |
        | 2       | 201     | Basic Tool       | 9.99  | 3        |
        | 3       | 301     | Fancy Accessory  | 39.99 | 1        |
        | 3       | 302     | Standard Supply  | 14.99 | 5        |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcart RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: API health check shows online
    When I visit the "Home Page"
    Then the API health status should be "✓ API Online"

Scenario: Add an item to a user's cart via the UI
    When I visit the "Home Page"
    And I set the "User ID" to "4"
    And I set the "Item ID" to "999"
    And I set the "Item Description" to "Test Product"
    And I set the "Item Price" to "49.99"
    And I set the "Item Quantity" to "2"
    And I press the "Create" button
    Then I should see the message "Item successfully added to cart!"
    When I press the "Search" button
    Then I should see the message "Search results found!"
    And I should see "Test Product" in the results
    And I should see "4" in the results
    And I should see "999" in the results

Scenario: Adding to cart fails when quantity is 0
    When I visit the "Home Page"
    And I set the "User ID" to "6"
    And I set the "Item ID" to "1001"
    And I set the "Item Description" to "Zero Item"
    And I set the "Item Price" to "12.99"
    And I set the "Item Quantity" to "0"
    And I press the "Create" button
    Then I should see the message "Quantity must be greater than 0."

Scenario: Add an item product to a user's cart via the UI
    When I visit the "Home Page"
    And I set the "User ID" to "5"
    And I set the "Item ID" to "888"
    And I set the "Item Description" to "Item Widget"
    And I set the "Item Price" to "29.99"
    And I set the "Item Quantity" to "3"
    And I set the "Item Stock" to "100"
    And I set the "Item Purchase Limit" to "5"
    And I press the "Create Item" button
    Then I should see the message "Product added from items!"
    When I press the "Search" button
    Then I should see "Item Widget" in the results

Scenario: Add an item product fails due to exceeding purchase limit
    When I visit the "Home Page"
    And I set the "User ID" to "5"
    And I set the "Item ID" to "888"
    And I set the "Item Description" to "Item Widget"
    And I set the "Item Price" to "29.99"
    And I set the "Item Quantity" to "3"
    And I set the "Item Stock" to "100"
    And I set the "Item Purchase Limit" to "2"
    And I press the "Create Item" button
    Then I should see the message "Cannot exceed purchase limit of 2"

Scenario: List all shopcarts from the UI
    When I visit the "Home Page"
    And I press the "List" button
    Then I should see "Deluxe Widget" in the results
    And I should see "Premium Gadget" in the results
    And I should see "Basic Tool" in the results
    And I should see "Fancy Accessory" in the results
    And I should see "Standard Supply" in the results

Scenario: List all shopcarts from the UI (using Search Button - equivalent to List All when no arguments provided)
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "Deluxe Widget" in the results
    And I should see "Premium Gadget" in the results
    And I should see "Basic Tool" in the results
    And I should see "Fancy Accessory" in the results
    And I should see "Standard Supply" in the results

<<<<<<< HEAD
Scenario: Checkout a user’s cart via the UI
    When I visit the "Home Page"
    And I set the "User ID" to "1"
    And I press the "Checkout" button
    Then I should see the message "Cart 1 checked out successfully"
    And the flashed message should be "Total: $69.97"
    When I press the "Clear" button
    And I set the "User ID" to "1"
    And I press the "Search" button
    Then I should see the message "No items found matching the search criteria."

Scenario: Checkout fails when cart is empty
    When I visit the "Home Page"
    And I set the "User ID" to "999"
    And I press the "Checkout" button
    Then I should see the message "No cart found for user 999"
=======
Scenario: Delete a shopcart from the UI
    When I visit the "Home Page"
    And I set the "User ID" to "3"
    And I press the "Delete" button
    Then I should see the message "Shopcart has been deleted!"
    When I press the "Retrieve" button
    Then I should see the message "Shopcart not found for this user."

Scenario: Delete an item from a user's cart via the UI
    When I visit the "Home Page"
    And I set the "User ID" to "1"
    And I set the "Item ID" to "101"
    And I press the "Delete Item" button
    Then I should see the message "Item has been deleted from the cart!"
    When I set the "User ID" to "1"
    And I press the "Retrieve" button
    Then I should see "Premium Gadget" in the results
    And I should not see "Deluxe Widget" in the results

Scenario: Cannot delete an item without providing a User ID
    When I visit the "Home Page" 
    And I set the "Item ID" to "101"
    And I press the "Delete Item" button
    Then I should see the message "User ID is required to delete an item."

Scenario: Cannot delete an item without providing an Item ID
    When I visit the "Home Page"
    And I set the "User ID" to "1"
    And I press the "Delete Item" button
    Then I should see the message "Item ID is required to delete an item."
>>>>>>> origin/master
