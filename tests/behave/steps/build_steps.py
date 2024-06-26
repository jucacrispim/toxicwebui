# -*- coding: utf-8 -*-

import time
from selenium.webdriver.common.by import By
from behave import given, when, then
from selenium.common.exceptions import StaleElementReferenceException

from toxicwebui import settings

from tests.behave import take_screenshot
from tests.behave.steps.base_steps import (  # noqa f811
    given_logged_in_webui, then_sees_message)


@given('is in the waterfall')
def is_in_waterfall(context):
    browser = context.browser
    base_url = 'http://{}:{}/'.format(settings.TEST_WEB_HOST,
                                      settings.TORNADO_PORT)

    waterfall_url = '{}someguy/repo-bla/waterfall'.format(base_url)
    browser.get(waterfall_url)
    time.sleep(0.5)


@when('he clicks in the reschedule buildset button in the waterfall')
def click_reschedule(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_elements(By.CLASS_NAME, 'fa-redo')[2]
            el = el if el.is_displayed() else None
        except IndexError:
            el = None

        return el

    el = browser.click_and_retry_on_stale(fn)
    assert el


@given('the user already rescheduled a buildset in the waterfall')
@take_screenshot
def buildset_already_rescheduled(context):
    browser = context.browser

    def fn():
        classes = ['build-preparing', 'build-pending']
        for cls in classes:
            try:
                el = browser.find_elements(By.CLASS_NAME, cls)[0]
            except IndexError:
                el = None

            if el:
                break

        return el

    el = browser.wait_element_become_present(fn)
    assert el


@when('the user clicks in the build details button')
def click_buildetails_button(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_elements(By.CLASS_NAME, 'build-details-link')[1]
        except IndexError:
            el = None

        return el

    el = browser.wait_element_become_present(fn)
    el.click()


@then('he sees the build details page')
def see_build_details(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_elements(By.CLASS_NAME,
                                       'build-details-container')[0]
        except IndexError:
            el = None

        return el

    el = browser.wait_element_become_present(fn)
    assert el


@given('the user is in the build details page')
def is_in_build_details_page(context):
    pass


@then('he waits for the build to finish')
def wait_build_finish(context):
    browser = context.browser

    def fn():
        el = browser.find_elements(By.CLASS_NAME, 'build-total-time')[0]
        try:
            if el.text:
                r = el
            else:
                r = None
        except StaleElementReferenceException:
            r = None

        return r

    el = browser.wait_element_become_present(fn)
    assert el
