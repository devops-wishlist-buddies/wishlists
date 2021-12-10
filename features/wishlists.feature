Feature: The Wishlist service back-end
    As a user
    I need a frontend layer of the application
    So that I can easily manipulate my wishlists via a user interface instead of urls

Background:
    Given the following wishlists
        |name                  |user_id |
        |My wishlist           |6       |
        |My greatest wishlist  |1       |
    And the following products
        |name           |inventory_product_id|price|status|short_desc|pic_url|
        |IPhone 20      |33                  |1200 |1|Future is here|https://via.placeholder.com/150|
        |Board game     |23                  | 30  |1|Best time killer you've ever seen!||
        |Nintendo Switch|21                  |400  |1|New pokemon game available||
        |Pen            |57                  |7    |1|||

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlists interface" in the title
    And I should not see "404 Not Found"

Scenario: Create a wishlist
    When I visit the "Home Page"
    And I press the "create-wishlist" button
    Then I should see the message "User ID and name should be defined."

    When I set the "wishlist-user-id" to "me"
    And I set the "wishlist-name" to "Mine"
    And I press the "create-wishlist" button
    Then I should see the message "User ID should be an integer."

    When I press the "wishlists-clear" button
    And I set the "wishlist-name" to "Jan Wishlist"
    And I set the "wishlist-user-id" to "9"
    And I press the "create-wishlist" button
    Then I should see the message "Wishlist Created!"
    When I copy the wishlist "id" value
    And I press the "wishlists-clear" button
    Then the "Wishlist-Id" field should be empty
    And the "Wishlist-Name" field should be empty
    And the "Wishlist-User-Id" field should be empty
    When I paste the "Wishlist-Id" field
    And I press the "search-Wishlist" button
    Then I should see value "Jan Wishlist" in the wishlist results as wishlist "name"
    And I should see value "9" in the wishlist results as wishlist "user-id"

Scenario: List all wishlists
    When I visit the "Home Page"
    And I set the "wishlist-id" to "some string"
    And I press the "search-wishlist" button
    Then I should see the message "Wishlist ID should be defined as an integer."

    When I press the "wishlists-clear" button
    And I press the "Search-wishlist" button
    Then I should see "My wishlist" in the results
    And I should see "My greatest wishlist" in the results

Scenario: Rename a wishlist
    When I visit the "Home Page"
    And I set the "wishlist-id" to "some string"
    And I press the "rename-wishlist" button
    Then I should see the message "Wishlist ID should be defined as an integer."

    When I set the "wishlist-id" to "1"
    And I press the "rename-wishlist" button
    Then I should see the message "Wishlist name cannot be empty."

    When I press the "wishlists-clear" button
    And I press the "Search-wishlist" button
    Then I should see the message "Success"
    And I should see value "My wishlist" in the wishlist results as wishlist "name"
    When I copy the wishlist "id" value
    And I press the "Wishlists-clear" button
    And I paste the "Wishlist-Id" field
    And I set the "Wishlist-Name" to "New Name"
    And I press the "rename-wishlist" button
    Then I should see the message "Success"
    When I press the "Wishlists-clear" button
    And I press the "Search-wishlist" button
    Then I should see value "New Name" in the wishlist results as wishlist "name"
    And I should not see "My wishlist" in the results
    And I should not see "My wishlist" in the wishlist results as wishlist "name"

Scenario: Read a wishlist
    When I visit the "Home Page"
    And I set the "wishlist-id" to "some string"
    And I press the "search-wishlist" button
    Then I should see the message "Wishlist ID should be defined as an integer."

    When I press the "wishlists-clear" button
    And I press the "Search-wishlist" button
    Then I should see "My wishlist" in the results
    When I press the "Wishlists-clear" button
    And I copy the wishlist "id" value
    And I paste the "wishlist-id" field
    And I press the "search-wishlist" button
    Then I should see value "My wishlist" in the wishlist results as wishlist "name"
    And I should not see "My greatest wishlist" in the results

Scenario: List wishlists by user(Query)
    When I visit the "Home Page"
    And I set the "wishlist-user-id" to "me"
    And I press the "search-wishlist" button
    Then I should see the message "User ID should be an integer."

    When I set the "wishlist-user-id" to "1"
    And I press the "search-wishlist" button
    Then I should see "My greatest wishlist" in the results
    And I should not see "My wishlist" in the results

Scenario: Delete a wishlist
    When I visit the "Home Page"
    And I set the "wishlist-id" to "some string"
    And I press the "Delete-wishlist" button
    Then I should see the message "Wishlist ID should be defined as an integer."

    When I press the "wishlists-clear" button
    And I press the "Search-wishlist" button
    Then I should see "My wishlist" in the results
    When I copy the wishlist "id" value
    And I paste the "Wishlist-Id" field
    And I press the "Delete-wishlist" button
    Then I should see the message "Wishlist Deleted!"
    When I press the "Wishlists-clear" button
    And I press the "search-wishlist" button
    Then I should not see "My wishlist" in the results
    Then I should see value "My greatest wishlist" in the wishlist results as wishlist "name"

Scenario: Add a product to wishlist
    When I visit the "Home Page"
    And I press the "wishlists-clear" button
    And I press the "search-wishlist" button
    Then I should see "My wishlist" in the results
    When I copy the wishlist "id" value
    And I press the "wishlists-clear" button
    And I paste the "wishlist-id" field
    And I set the "wishlist-inventory-product-id" to "50"
    And I set the "wishlist-product-name" to "Golden Snitch"
    And I set the "wishlist-product-price" to "350"
    And I set the "wishlist-product-pic" to "https://via.placeholder.com/150/FFFF00"
    And I set the "wishlist-product-description" to "Very rare ball, easy to lose, but can keep your cat busy."
    And I press the "add-product" button
    Then I should see the message "Product was added to wishlist."
    When I press the "wishlists-clear" button
    Then the "wishlist-inventory-product-id" field should be empty
    And the "wishlist-product-name" field should be empty
    And the "wishlist-product-price" field should be empty
    And the "wishlist-product-pic" field should be empty
    And the "wishlist-product-description" field should be empty
    When I paste the "wishlist-id" field
    And I press the "search-wishlist" button
    Then I should see value "My wishlist" in the wishlist results as wishlist "name"
    And I should see value "Golden Snitch" in the wishlist results as product "name"
    And I should see value "350" in the wishlist results as product "price"
    And I should not see "My greatest wishlist" in the results

    When I press the "wishlists-clear" button
    And I set the "wishlist-id" to "blahblah"
    And I press the "add-product" button
    Then I should see the message "Inventory ID, product name, product price and wishlist ID should be defined."

    When I press the "wishlists-clear" button
    And I press the "search-wishlist" button
    Then I should see "My wishlist" in the results
    When I copy the wishlist "id" value
    And I press the "wishlists-clear" button
    And I paste the "wishlist-id" field
    And I set the "wishlist-inventory-product-id" to "hello"
    And I set the "wishlist-product-name" to "New product"
    And I set the "wishlist-product-price" to "350thousand"
    And I press the "add-product" button
    Then I should see the message "Inventory ID, product price and wishlist ID should be integers."

    When I press the "wishlists-clear" button
    And I press the "search-wishlist" button
    Then I should see "My wishlist" in the results
    When I copy the wishlist "id" value
    And I press the "wishlists-clear" button
    And I paste the "wishlist-id" field
    And I set the "wishlist-product-name" to "New product"
    And I press the "add-product" button
    Then I should see the message "Inventory ID, product name, product price and wishlist ID should be defined."

Scenario: Read a product in a wishlist
    When I visit the "Home Page"
    When I set the "wishlist-id" to "some string"
    And I set the "wishlist-product-id" to "16.5asd"
    And I press the "search-product" button
    Then I should see the message "Product ID and Wishlist ID should be defined as integers."

    When I press the "wishlists-clear" button
    And I press the "search-wishlist" button
    Then I should see "Board game" in the results
    When I copy the product id of "Board game" from wishlist results
    And I paste the "wishlist-product-id" field
    And I copy the wishlist id of "Board game" from wishlist results
    And I paste the "wishlist-id" field
    And I press the "search-product" button
    Then I should see "Best time killer you've ever seen!" in the results
    And I should not see value "IPhone" in the product results as product "name"
    And I should not see value "Pen" in the product results as product "name"
    And I should not see "My wishlist" in the results

Scenario: Delete a product from a wishlist
    When I visit the "Home Page"
    And I set the "wishlist-id" to "some string"
    And I set the "wishlist-product-id" to "16.5asd"
    And I press the "delete-product" button
    Then I should see the message "Product ID and Wishlist ID should be defined as integers."

    When I press the "wishlists-clear" button
    And I press the "search-wishlist" button
    Then I should see "Board game" in the results
    When I copy the product id of "Board game" from wishlist results
    And I paste the "wishlist-product-id" field
    And I copy the wishlist id of "Board game" from wishlist results
    And I paste the "wishlist-id" field
    And I press the "delete-product" button
    Then I should see the message "Success"
    When I press the "search-wishlist" button
    Then I should not see value "Board game" in the wishlist results as product "name"

Scenario: Edit a product in a wishlist
    When I visit the "Home Page"
    And I set the "wishlist-id" to "some string"
    And I set the "wishlist-product-id" to "16.5asd"
    And I press the "update-product" button
    Then I should see the message "Product ID and Wishlist ID should be defined as integers."

    When I press the "wishlists-clear" button
    And I press the "search-wishlist" button
    Then I should see "Board game" in the results
    When I copy the product id of "Board game" from wishlist results
    And I paste the "wishlist-product-id" field
    And I copy the wishlist id of "Board game" from wishlist results
    And I paste the "wishlist-id" field
    And I set the "wishlist-product-name" to "New Board game"
    And I set the "wishlist-product-price" to "6666"
    And I press the "update-product" button
    Then I should see the message "Updated Success!"
    When I paste the "wishlist-id" field
    And I press the "search-wishlist" button
    Then I should see value "New Board game" in the wishlist results as product "name"
    And I should see value "6666" in the wishlist results as product "price"
    And I should not see value "30" in the wishlist results as product "price"

    When I press the "wishlists-clear" button
    And I press the "search-wishlist" button
    Then I should see "Pen" in the results
    When I copy the product id of "Pen" from wishlist results
    And I paste the "wishlist-product-id" field
    And I copy the wishlist id of "Pen" from wishlist results
    And I paste the "wishlist-id" field
    And I set the "wishlist-product-price" to "fifty"
    And I set the "wishlist-inventory-product-id" to "five"
    And I press the "update-product" button
    Then I should see the message "Inventory ID and Price should be defined as Integer and Float respectively."

Scenario: Place a product from a wishlist in a shopcart
    When I visit the "Home Page"
    And I set the "wishlist-id" to "some string"
    And I set the "wishlist-product-id" to "16.5asd"
    And I press the "order-product" button
    Then I should see the message "Product ID and Wishlist ID should be defined as integers."

    When I press the "wishlists-clear" button
    And I press the "search-wishlist" button
    Then I should see "Pen" in the results
    When I copy the product id of "Pen" from wishlist results
    And I paste the "wishlist-product-id" field
    And I copy the wishlist id of "Pen" from wishlist results
    And I paste the "wishlist-id" field
    And I press the "order-product" button
    Then I should see the message "Success"
    When I press the "search-wishlist" button
    Then I should see "This product is in the shopping cart" in the results
