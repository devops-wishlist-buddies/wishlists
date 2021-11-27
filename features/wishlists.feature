Feature: The Wishlist service back-end
    As a user
    I need a frontend layer of the application
    So that I can easily manipulate my wishlists via a user interface instead of urls

Background:
    Given the following wishlists
        |id |name                  |user_id |
        |1  |My wishilst           |6       |
        |4  |My greatest wishilst  |1       |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishilsts interface" in the title
    And I should not see "404 Not Found"