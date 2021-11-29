Feature: The Wishlist service back-end
    As a user
    I need a frontend layer of the application
    So that I can easily manipulate my wishlists via a user interface instead of urls

Background:
    Given the following wishlists
        |name                  |user_id |
        |My wishilst           |6       |
        |My greatest wishilst  |1       |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishilsts interface" in the title
    And I should not see "404 Not Found"

Scenario: Create a wishlist
    When I visit the "Home Page"
    And I set the "Wishlist_Name" to "Jan Wishlist"
    And I set the "Wishlist_User_Id" to "1"
    And I press the "create-wishlist" button
    Then I should see the message "Wishlist Created!"
    When I copy the "Wishlist_Id" field
    And I press the "Wishlists_clear" button
    Then the "Wishlist_Id" field should be empty
    And the "Wishlist_Name" field should be empty
    And the "Wishlist_User_Id" field should be empty
    When I paste the "Wishlist_Id" field
    And I press the "Search-Wishlist" button
    Then I should see "Jan Wishlist" in the "Wishlist_Name" field
    And I should see "1" in the "Wishlist_User_Id" field
