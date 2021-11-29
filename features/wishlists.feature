Feature: The Wishlist service back-end
    As a user
    I need a frontend layer of the application
    So that I can easily manipulate my wishlists via a user interface instead of urls

Background:
    Given the following wishlists
        |name                  |user_id |
        |My wishlist           |6       |
        |My greatest wishlist  |1       |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlists interface" in the title
    And I should not see "404 Not Found"

Scenario: Create a wishlist
    When I visit the "Home Page"
    And I set the "Wishlist-Name" to "Jan Wishlist"
    And I set the "Wishlist-User_Id" to "1"
    And I press the "create-wishlist" button
    Then I should see the message "Wishlist Created!"
    When I copy the "Wishlist-Id" field
    And I press the "Wishlists-clear" button
    Then the "Wishlist-Id" field should be empty
    And the "Wishlist-Name" field should be empty
    And the "Wishlist-User_Id" field should be empty
    When I paste the "Wishlist-Id" field
    And I press the "retrieve-Wishlist" button
    Then I should see "Jan Wishlist" in the "Wishlist-Name" field
    And I should see "1" in the "Wishlist-User_Id" field

Scenario: List all wishlists
    When I visit the "Home Page"
    And I press the "Search-wishlist" button
    Then I should see "My wishlist" in the results
    And I should see "My greatest wishlist" in the results

Scenario: Rename a wishlist
    When I visit the "Home Page"
    And I press the "Search-wishlist" button
    Then I should see "My wishlist" in the results
    When I copy the "Wishlist-Id" field
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
    When I copy the "Wishlist-Id" field
    And I press the "Wishlists-clear" button
    And I paste the "Wishlist-Id" field
    And I press the "retrieve-wishlist" button
    Then I should see "My wishlist" in the results

Scenario: List wishlists by user(Query)
    When I visit the "Home Page"
    And I set the "wishlist-user_id" to "1"
    And I press the "search-wishlist" button
    Then I should see "My greatest wishlist" in the results
    And I should not see "My wishlist" in the results

Scenario: Delete a wishlist
    When I visit the "Home Page"
    And I press the "Search-wishlist" button
    Then I should see "My wishlist" in the results
    When I copy the "Wishlist-Id" field
    And I press the "Wishlists-clear" button
    And I paste the "Wishlist-Id" field
    And I press the "Delete-wishlist" button
    Then I should see the message "Wishlist Deleted!"
    When I press the "search-wishlist" button
    Then I should not see "My wishlist" in the results
    Then I should see "My greatest wishlist" in the results