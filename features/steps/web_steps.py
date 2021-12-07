"""
Web Steps
Steps file for web interactions with Silenium
For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import logging
import json
from random import choice
from behave import when, then
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions


@when('I visit the "home page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)

@then('I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.driver.page_source)
    ensure(message in context.resp.text, False, error_msg)

@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)

    logging.info('Set %s to %s', element_name, text_string)

@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    expect(element.get_attribute('value')).to_be(u'')

##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = element_name.lower()
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Clipboard contains: %s', context.clipboard)

@when('I copy the wishlist "{element}" value')
def step_impl(context, element):
  elements = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
    expected_conditions.presence_of_all_elements_located(
      (By.XPATH, '//div[@class="wishlist-block__'+element+'"]')
    )
  )
  id = elements[0].text
  context.clipboard = id
  logging.info('Clipboard contains %s', id)

@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = element_name.lower()
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)

    logging.info('Pasted %s in %s', context.clipboard, element_name)

@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower()
    element = context.driver.find_element_by_id(button_id)
    element.click()

@then('I should see "{name}" in the results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search-results'),
            name
        )
    )
    expect(found).to_be(True)

@then('I should see "{name}" in the results as wishlist "{element}"')
def step_impl(context, name, element):
  # find all elements with matching classname
  candidates = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
    expected_conditions.presence_of_all_elements_located(
      (By.XPATH, '//div[@class="wishlist-block__'+element+'"]')
    )
  )
  matching_element = ''
  for el in candidates:
    if el.text == name:
      matching_element = el

  # verify that it's in the results
  found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search-results'),
            matching_element.text
        )
    )

  expect(found).to_be(True)

@then('I should see "{name}" in the results as product "{element}"')
def step_impl(context, name, element):
  # find all elements with matching classname
  candidates = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
    expected_conditions.presence_of_all_elements_located(
      (By.XPATH, '//div[@class="products-item__'+element+'"]')
    )
  )
  matching_element = ''
  for el in candidates:
    if el.text == name:
      matching_element = el

  # verify that it's in the results
  found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search-results'),
            matching_element.text
        )
    )

  expect(found).to_be(True)

@then('I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('search-results')
    error_msg = "I should not see '%s' in '%s'" % (name, element.text)
    ensure(name in element.text, False, error_msg)

@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash-message'),
            message
        )
    )
    expect(found).to_be(True)

@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = element_name.lower()
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    expect(found).to_be(True)

@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = element_name.lower()
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)


# for testing simplicity we will assume that proucts have different names and
# do not repeat in different wishlists.
@when('I copy the product id of "{product_name}" from wishlist results')
def step_impl(context, product_name):
  elements = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
    expected_conditions.presence_of_all_elements_located(
      (By.CLASS_NAME, 'wishlist-block__products-item')
    )
  )
  matching_product_block = ''
  for elem in elements:
    if product_name in elem.text:
      matching_product_block = elem

  assert matching_product_block != ''

  product_id = matching_product_block.get_attribute('id')
  context.clipboard = product_id.split('-')[-1]
  logging.info('Clipboard contains: %s', context.clipboard)

@when('I copy the wishlist id of "{product_name}" from wishlist results')
def step_impl(context, product_name):
  elements = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
    expected_conditions.presence_of_all_elements_located(
      (By.CLASS_NAME, 'wishlist-block')
    )
  )
  matching_wishlist_block = ''
  for elem in elements:
    if product_name in elem.text:
      matching_wishlist_block = elem

  assert matching_wishlist_block != ''
  wishlist_id = matching_wishlist_block.get_attribute('id')
  context.clipboard = wishlist_id.split('-')[-1]
  logging.info('Clipboard contains: %s', context.clipboard)
