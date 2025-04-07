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