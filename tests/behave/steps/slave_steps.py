# -*- coding: utf-8 -*-

import time
from selenium.webdriver.common.by import By
from behave import when, then, given
from tests.behave.steps.base_steps import (  # noqa f811
    given_logged_in_webui)


@when('he clicks in the settings button')
def click_settings_button(context):
    browser = context.browser
    browser.click_link('manage')

    # wait for the settings page
    browser.wait_text_become_present('Manage slaves')


@when('clicks in the Manage slaves menu')
def click_manage_slave_menu(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_element(By.ID, 'manage-slaves-link')
        except Exception:
            el = None

        el = el if el.is_displayed() else None
        return el

    el = browser.wait_element_become_present(fn)

    el.click()

    # here I wait for the slave list page to appear looking for the
    # help text
    browser.wait_text_become_present('Slaves are the ones')


@when('clicks in the add slave button')
def click_add_slave_button(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_elements(By.CLASS_NAME, 'fa-plus')[0]
        except IndexError:
            el = None

        return el

    el = browser.wait_element_become_present(fn)
    el.click()


@then('he sees the add slave page')
def see_add_slave_page(context):
    browser = context.browser
    browser.wait_text_become_present('Add slave')


@given('the user is in the add slave page')
def is_in_add_slave_page(self):
    pass


@when('he fills the slave name field')
def fill_slave_name(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_elements(By.CLASS_NAME, 'slave-details-name')[1]
        except IndexError:
            el = None

        return el

    el = browser.wait_element_become_present(fn)
    el.send_keys('some-name')


@when('fills the host field')
def fill_slave_host(context):
    browser = context.browser
    el = browser.find_elements(By.CLASS_NAME, 'slave-details-host')[1]
    el.send_keys('some.host')


@when('fills the port field')
def fill_slave_port(context):
    browser = context.browser
    el = browser.find_elements(By.CLASS_NAME, 'slave-details-port')[1]
    el.send_keys(1234)


@when('fills the token field')
def fill_token_field(context):
    browser = context.browser
    el = browser.find_elements(By.CLASS_NAME, 'slave-details-token')[1]
    el.send_keys('some-token')


@when('clicks in the save changes button')
@when('clicks in the add new slave button')
def click_add_new_slave_button(context):
    browser = context.browser
    el = browser.find_element(By.ID, 'btn-save-obj')
    time.sleep(0.5)
    el.click()


@given('the user is in the slave settings page')
def is_in_slave_settings_page(context):
    browser = context.browser
    browser.wait_text_become_present('General configurations')

    def fn():
        try:
            el = browser.find_elements(By.CLASS_NAME, 'btn-delete-slave')[1]
        except IndexError:
            el = None

        return el

    el = browser.wait_element_become_present(fn)
    browser.wait_element_become_visible(el)


@when('he clicks in the use ssl button')
def click_use_ssl(context):
    browser = context.browser
    el = browser.find_element(By.ID, 'slave-use-ssl')
    browser.click(el)


@when('he clicks in the close page button')
def click_close_btn(context):
    browser = context.browser

    def fn():
        el = browser.find_element(By.ID, 'btn-cancel-save')
        return el

    btn = browser.wait_element_become_present(fn)
    btn.click()
    browser.wait_text_become_present('Manage slaves')


@then('he sees the slaves list')
def see_slave_list(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_elements(By.CLASS_NAME, 'slave-info')[1]
        except IndexError:
            el = None

        return el

    el = browser.wait_element_become_present(fn)
    browser.wait_element_become_visible(el)


@given('the user is in the slaves list page')
def is_in_slaves_list_page(context):
    pass


@when('he navigates to the slave settings page')
def navigate_to_slave_settings_page(context):
    browser = context.browser

    el = browser.find_elements(By.CLASS_NAME, 'fa-ellipsis-h')[1]
    el.click()
    browser.click_link('Settings')
    browser.wait_text_become_present('General configurations')


@when('clicks in the delete slave button')
def click_delete_button(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_elements(By.CLASS_NAME, 'btn-delete-slave')[1]
        except IndexError:
            el = None

        return el

    el = browser.wait_element_become_present(fn)
    browser.wait_element_become_visible(el)

    browser.click(el)


@when('clicks in the delete slave button in the modal')
def click_delete_button_modal(context):
    browser = context.browser

    el = browser.find_element(By.ID, 'btn-remove-obj')
    browser.wait_element_become_visible(el)
    el.click()
