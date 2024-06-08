# -*- coding: utf-8 -*-

import time
from selenium.webdriver.common.by import By
from behave import when, then, given
from toxicwebui import settings
from tests.behave.steps.base_steps import (  # noqa f811
    given_logged_in_webui, user_sees_main_main_page_login)


# Scenario: Someone try to access a page without being logged.

@when('someone tries to access a waterfall url without being logged')
def try_get_waterfall(context):
    browser = context.browser
    base_url = 'http://{}:{}/'.format(settings.TEST_WEB_HOST,
                                      settings.TORNADO_PORT)

    url = base_url + 'waterfall/some-repo'

    browser.get(url)


@then('he sees the login page')  # noqa f401
def sees_login_page(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_element(By.ID, 'inputUsername')
        except Exception:
            el = None

        return el

    el = browser.wait_element_become_present(fn)

    assert el


# Scenario: Do login

@given('the user is in the login page')  # noqa f401
def user_is_in_login_page(context):
    browser = context.browser
    base_url = 'http://{}:{}/'.format(settings.TEST_WEB_HOST,
                                      settings.TORNADO_PORT)

    url = base_url + 'login'
    browser.get(url)


@when('he inserts "{user_name}" as user name')
def user_inserts_username_login(context, user_name):
    browser = context.browser
    username_input = browser.find_element(By.ID, 'inputUsername')
    username_input.send_keys(user_name)


@when('inserts "{passwd}" as password')
def user_inserts_password_login(context, passwd):
    browser = context.browser
    passwd_input = browser.find_element(By.ID, 'inputPassword')
    passwd_input.send_keys(passwd)


@when('clicks in the login button')
def user_clicks_login_button(context):
    browser = context.browser
    btn = browser.find_element(By.ID, 'btn-login')
    btn.click()


@then('he sees the red warning in the password field')
def user_sees_missing_required_field_warning(context):
    browser = context.browser
    el = browser.find_element(By.CLASS_NAME, 'form-control-error')
    assert el


@then('he sees the invalid credentials message')
def user_sees_invalid_credentials_message(context):
    browser = context.browser
    el = browser.find_element(By.ID, 'login-error-msg-container')
    color = el.value_of_css_property('color')
    time.sleep(0.5)
    assert color != 'rgb(255, 255, 255)'


# Scenario: Do logout

@when('he clicks in the logout link')  # noqa f401
def step_impl(context):
    browser = context.browser
    el = browser.find_element(By.CLASS_NAME, 'nav-link')
    browser.click(el)
    el = browser.find_elements(By.CLASS_NAME, 'dropdown-item-logout')[-1]
    browser.click(el)
