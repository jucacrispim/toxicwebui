# -*- coding: utf-8 -*-

import time
from selenium.webdriver.common.by import By
from behave import when, then, given
from tests.behave import take_screenshot
from tests.behave.steps.base_steps import (  # noqa f811
    given_logged_in_webui, then_sees_message)


@when('he clicks in the waterfall button')
@take_screenshot
def clicks_waterfall_button(context):
    browser = context.browser

    def fn():
        try:
            btn = browser.find_elements(By.CLASS_NAME, 'badge')[1]
            btn = btn if btn.is_displayed() else None
        except Exception:
            btn = None

        return btn

    btn = browser.wait_element_become_present(fn)
    browser.click(btn)
    time.sleep(0.2)


@then('he sees a list of builds in the waterfall')  # noqa f401
@take_screenshot
def sees_waterfall_builds_list(context):
    browser = context.browser
    elements = browser.find_elements(By.CLASS_NAME,
                                     'waterfall-buildset-info-container')
    timeout = 5
    c = 0
    while not bool(elements) and c < timeout:
        time.sleep(1)
        elements = browser.find_elements(By.CLASS_NAME, 'step-running')
        c += 1

    assert bool(elements)


@given('the user is already in the waterfall')  # noqa f401
def step_impl(context):
    pass


@when('he clicks in the reschedule buildset button')  # noqa f401
@take_screenshot
def clicks_reschedule_buildset_button(context):
    browser = context.browser

    def fn():
        try:
            btn = browser.find_elements(By.CLASS_NAME, 'fa-redo')[2]
            btn = btn if btn.is_displayed() else None
        except IndexError:
            btn = None

        return btn

    btn = browser.wait_element_become_present(fn)
    btn.click()


@given('already rescheduled a buildset')
@take_screenshot
def reschedule_buildset(context):
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


@when('The builds start running')
@take_screenshot
def builds_start_running(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_elements(By.CLASS_NAME, 'build-running')[0]
        except IndexError:
            el = None

        return el

    el = browser.wait_element_become_present(fn)
    assert el


@then('he waits for the builds complete')
@take_screenshot
def wait_builds_complete(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_elements(By.CLASS_NAME, 'build-running')[0]
        except IndexError:
            el = None

        return el

    el = browser.wait_element_be_removed(fn)
    assert not el


@when('he clicks in the branch select filter')
def click_branch_select(context):
    browser = context.browser

    el = browser.wait_element_become_present(
        lambda: browser.find_elements(By.CLASS_NAME, 'navbar-select')[1])
    el.click()


@when('clicks in the master branch')
def click_master_branch(context):
    browser = context.browser

    def fn():
        return browser.find_elements(By.CLASS_NAME, 'option')[1]

    el = browser.wait_element_become_present(fn, check_display=False)
    assert el
    el.click()
