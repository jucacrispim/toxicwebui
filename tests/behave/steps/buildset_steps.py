# -*- coding: utf-8 -*-

from selenium.webdriver.common.by import By
from behave import when, then, given
from selenium.common.exceptions import StaleElementReferenceException
from tests.behave import take_screenshot
from tests.behave.steps.base_steps import (  # noqa f811
    given_logged_in_webui, then_sees_message)


@when('he clicks in the summary link')
@take_screenshot
def click_summary_link(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_elements(By.XPATH, '//a[@title="Summary"]')[1]
            el = el if el.is_displayed() else None
        except Exception:
            el = None

        return el

    browser.refresh()
    el = browser.click_and_retry_on_stale(fn)
    assert el


@then('he sees the buildset list page')
@take_screenshot
def see_buildset_list_page(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_elements(By.CLASS_NAME, 'buildset-info')[1]
            el = el if el.is_displayed() else None
        except Exception:
            el = None

        return el

    el = browser.wait_element_become_present(fn)
    assert el


@given('the user is in the buildset list page')
@take_screenshot
def is_in_buildset_list_page(context):
    browser = context.browser
    browser.get(browser.current_url)


@when('he clicks in the reschedule button')
@take_screenshot
def click_reschedule_button(context):
    browser = context.browser
    browser.refresh()

    def fn():
        try:
            el = browser.find_elements(By.CLASS_NAME, 'fa-redo')[1]
            el = el if el.is_displayed() else None
        except Exception:
            el = None

        return el

    el = browser.wait_element_become_present(fn)
    try:
        browser.wait_element_become_visible(el)
    except StaleElementReferenceException:
        el = browser.wait_element_become_present(fn)
        browser.wait_element_become_visible(el)

    browser.wait_element_become_visible(el)
    el.click()


@then('he sees the buildset running')
@take_screenshot
def see_buildset_running(context):
    browser = context.browser

    browser.wait_element_become_present(
        lambda: browser.find_elements(By.CLASS_NAME, 'badge-primary')[0])


@given('the user already rescheduled a buildset')
@take_screenshot
def already_rescheduled_buildset(context):
    browser = context.browser
    browser.refresh()
    el = browser.find_elements(By.CLASS_NAME, 'badge-primary')[0]
    browser.wait_element_become_visible(el)


@when('he clicks in the buildset details link')
@take_screenshot
def click_in_buildset_details_link(context):
    browser = context.browser
    el = browser.find_elements(By.CLASS_NAME, 'buildset-details-link')[3]
    try:
        browser.wait_element_become_visible(el)
    except StaleElementReferenceException:
        el = browser.find_elements(By.CLASS_NAME, 'buildset-details-link')[3]
        browser.wait_element_become_visible(el)

    el.click()


@then('he sees the buildset details page')
@take_screenshot
def see_buildset_details(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_elements(By.CLASS_NAME,
                                       'buildset-details-header')[1]
        except IndexError:
            el = None

        return el

    el = browser.wait_element_become_present(fn)
    assert el


@given('the user is in the buildset details page')
def is_in_buildset_details_page(context):
    pass


@when('the builds start')
@take_screenshot
def builds_start(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_elements(By.CLASS_NAME, 'badge-primary')[0]
        except IndexError:
            el = None

        return el

    el = browser.wait_element_become_present(fn)
    assert el


@then('he waits for the builds to complete')
@take_screenshot
def wait_builds_to_complete(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_elements(By.CLASS_NAME, 'badge-primary')[0]
        except IndexError:
            el = None

        return el

    el = browser.wait_element_be_removed(fn)
    assert not el
