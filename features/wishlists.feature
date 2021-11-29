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
        |name          |inventory_product_id|price|status|
        |IPhone 20      |33                  |1200 |1|
        |Board game     |23                  | 30  |1|
        |Nintendo Switch|21                  |300  |1|

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlists interface" in the title
    And I should not see "404 Not Found"

Scenario: Create a wishlist
    When I visit the "Home Page"
    And I set the "wishlist-name" to "Jan Wishlist"
    And I set the "wishlist-user-id" to "1"
    And I press the "create-wishlist" button
    Then I should see the message "Wishlist Created!"
    When I copy the "wishlist-id" field
    And I press the "wishlists-clear" button
    Then the "Wishlist-Id" field should be empty
    And the "Wishlist-Name" field should be empty
    And the "Wishlist-User-Id" field should be empty
    When I paste the "Wishlist-Id" field
    And I press the "search-Wishlist" button
    Then I should see "Jan Wishlist" in the results
    And I should see "1" in the results

Scenario: List all wishlists
    When I visit the "Home Page"
    And I press the "Search-wishlist" button
    Then I should see "My wishlist" in the results
    And I should see "My greatest wishlist" in the results

Scenario: Rename a wishlist
    When I visit the "Home Page"
    And I press the "Search-wishlist" button
    Then I should see the message "Success"
    And I should see "My wishlist" in the results
    When I copy the first cell with class "results-table__wishlist-id"
    And I press the "Wishlists-clear" button
    And I paste the "Wishlist-Id" field
    And I set the "Wishlist-Name" to "New Name"
    And I press the "rename-wishlist" button
    Then I should see the message "Success"
    When I press the "Wishlists-clear" button
    And I press the "Search-wishlist" button
    Then I should see "New Name" in the results
    Then I should not see "My wishlist" in the results

Scenario: Read a wishlist
    When I visit the "Home Page"
    And I press the "Search-wishlist" button
    Then I should see "My wishlist" in the results
    When I press the "Wishlists-clear" button
    And I copy the first cell with class "results-table__wishlist-id"
    And I paste the "wishlist-id" field
    And I press the "search-wishlist" button
    Then I should see "My wishlist" in the results
    And I should not see "My greatest wishlist" in the results

Scenario: List wishlists by user(Query)
    When I visit the "Home Page"
    And I set the "wishlist-user-id" to "1"
    And I press the "search-wishlist" button
    Then I should see "My greatest wishlist" in the results
    And I should not see "My wishlist" in the results

Scenario: Delete a wishlist
    When I visit the "Home Page"
    And I press the "Search-wishlist" button
    Then I should see "My wishlist" in the results
    When I copy the first cell with class "results-table__wishlist-id"
    And I press the "Wishlists-clear" button
    And I paste the "Wishlist-Id" field
    And I press the "Delete-wishlist" button
    Then I should see the message "Wishlist Deleted!"
    When I press the "search-wishlist" button
    Then I should not see "My wishlist" in the results
    Then I should see "My greatest wishlist" in the results

Scenario: Add a product to wishlist
    When I visit the "Home Page"
    And I press the "search-wishlist" button
    Then I should see "My wishlist" in the results
    When I copy a random cell with class "results-table__wishlist-id"
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
    Then I should see "Golden Snitch" in the results
