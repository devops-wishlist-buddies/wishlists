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