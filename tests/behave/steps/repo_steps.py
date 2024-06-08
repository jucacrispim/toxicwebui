# -*- coding: utf-8 -*-

import time
from selenium.webdriver.common.by import By
from behave import when, then, given
from tests.behave.steps.base_steps import (  # noqa f811
    given_logged_in_webui, then_sees_message, when_navigate2settings,
    click_add_button)
from tests.functional import REPO_DIR


@when('he clicks in the add repository link')
def click_add_repo_btn(context):
    browser = context.browser
    btn = browser.find_element(By.XPATH, '//a[@href="/repository/add"]')
    browser.wait_element_become_visible(btn)
    browser.click(btn)


@then('he sees the add repository page')
def sees_add_repo_page(context):
    browser = context.browser
    browser.wait_text_become_present('Add repository')


@given('the user is in the add repo page')
def is_in_the_add_repo_page(context):
    browser = context.browser
    is_present = browser.wait_text_become_present('Add repository')
    assert is_present
    time.sleep(0.5)


@when('he fills the name with a repo name')
def fill_repo_name(context):
    browser = context.browser
    name_input = browser.find_elements(By.CLASS_NAME, 'repo-details-name')[1]
    name_input.send_keys('MyNewRepo')


@when('fills the url field with a repo url')
def fill_repo_url(context):
    browser = context.browser
    url_input = browser.find_elements(By.CLASS_NAME, 'repo-details-url')[1]
    url_input.send_keys(REPO_DIR)


@when('he fills the parallel builds with 2')
def fill_parallel_builds(context):
    browser = context.browser
    el_input = browser.find_elements(By.CLASS_NAME,
                                     'repo-parallel-builds')[1]
    el_input.send_keys(2)


@when('he clicks in the environment variables button')
def click_envvars_button(context):
    browser = context.browser
    btn = browser.find_elements(By.CLASS_NAME, 'envvars-badge')[1]
    btn.click()


@when('he clicks in the secrets button')
def click_secrets_button(context):
    browser = context.browser
    btn = browser.find_elements(By.CLASS_NAME, 'secrets-badge')[1]
    btn.click()


@when('fills the key and value fiels')
def fill_envvar(context):
    browser = context.browser
    key = browser.wait_element_become_present(
        lambda: browser.find_elements(By.CLASS_NAME, 'envvars-key')[0])

    val = browser.wait_element_become_present(
        lambda: browser.find_elements(By.CLASS_NAME, 'envvars-value')[0])
    key.send_keys('the-key')
    val.send_keys('the-value')


@when('fills the secrets key and value fiels')
def fill_secret(context):
    browser = context.browser
    key = browser.wait_element_become_present(
        lambda: browser.find_elements(By.CLASS_NAME, 'secrets-key')[0])

    val = browser.wait_element_become_present(
        lambda: browser.find_elements(By.CLASS_NAME, 'secrets-value')[0])
    key.send_keys('the-key')
    val.send_keys('the-value')


@when('clicks in the save environment variables button')
def click_save_envvars(context):
    browser = context.browser
    btn = browser.find_element(By.ID, 'btn-update-envvars')
    btn.click()


@when('clicks in the save secrets button')
def click_save_secrets(context):
    browser = context.browser
    btn = browser.find_element(By.ID, 'btn-update-secrets')
    btn.click()


@given('the user is in the repository settings page')
def is_in_repo_settings_page(context):
    browser = context.browser
    el = browser.wait_element_become_present(
        lambda: browser.find_element(By.CLASS_NAME, 'fa-list'))
    assert el


@when('he clicks in the Advanced element')
def click_advanced_config(context):
    browser = context.browser
    el = browser.wait_element_become_present(
        lambda: browser.find_elements(By.CLASS_NAME,
                                      'repo-config-advanced-span')[1])
    browser.click(el)


@given('he sees the advanced options')
@then('he sees the advanced options')
def see_advanced_options(context):
    browser = context.browser
    el = browser.find_elements(By.CLASS_NAME, 'repo-branches-ul')[1]
    browser.wait_element_become_visible(el)


@then('sees the advanced help in the side bar')
def see_advanced_help(context):
    browser = context.browser
    sidebar_help = browser.find_element(By.ID, 'parallel-builds-config-p')
    browser.wait_element_become_visible(sidebar_help)


@when('he clicks in the add branch button')
def clicks_branch_button(context):
    browser = context.browser
    btn = browser.find_elements(By.CLASS_NAME, 'add-branch-btn')[1]
    browser.click(btn)
    el = browser.find_element(By.ID, 'addBranchModal')
    browser.wait_element_become_visible(el)


@when('fills the branch name')
def fill_branch_name(context):
    browser = context.browser
    el = browser.find_element(By.ID, 'repo-branch-name')
    el.send_keys('master')
    time.sleep(0.5)


@when('clicks in the add branch button')
def click_add_branch_button(context):
    browser = context.browser
    el = browser.find_element(By.ID, 'btn-add-branch')
    browser.click(el)
    time.sleep(0.5)


@then('he sees the new branch config in the list')
def see_new_branch(context):
    browser = context.browser

    el = browser.wait_element_become_present(
        lambda: browser.find_elements(By.CLASS_NAME, 'repo-branches-li')[2])
    assert el


@given('the user already added a branch config')
def already_added_branch(context):
    pass


@when('he clicks in the remove branch config button')
def click_remove_branch_btn(context):
    browser = context.browser
    btn = browser.find_elements(By.CLASS_NAME, 'remove-branch-btn')[2]
    browser.click(btn)


@then('he sees the no branch config info in the list')
def see_no_branch_config_info(context):
    browser = context.browser
    el = browser.find_elements(By.CLASS_NAME, 'no-item-placeholder')[1]
    browser.wait_element_become_visible(el)


@when('he clicks in the slave enabled check button')
def click_slave_enabled_check(context):
    browser = context.browser
    xpath = '//li[@class="repo-slaves-li box-shadow-light box-white"]'
    xpath += '/div/div/label[@class="btn btn-success toggle-on"]'

    el = browser.find_element(By.XPATH, xpath)
    browser.wait_element_become_visible(el)
    browser.click(el)


@then('he sees the slave disabled check button')
def see_slave_disabled_check(context):
    browser = context.browser
    xpath = '//li[@class="repo-slaves-li box-shadow-light box-white"]'
    xpath += '/div/div/label[@class="btn btn-secondary active toggle-off"]'

    el = browser.find_element(By.XPATH, xpath)
    browser.wait_element_become_visible(el)


@when('he clicks in the slave disabled check button')
def clicks_slave_disabled_btn(context):
    browser = context.browser
    xpath = '//li[@class="repo-slaves-li box-shadow-light box-white"]'
    xpath += '/div/div/label[@class="btn btn-secondary active toggle-off"]'

    el = browser.find_element(By.XPATH, xpath)
    browser.wait_element_become_visible(el)
    browser.click(el)


@then('he sees the slave enabled check button')
def see_slave_enabled_check(context):
    browser = context.browser
    xpath = '//li[@class="repo-slaves-li box-shadow-light box-white"]'
    xpath += '/div/div/label[@class="btn btn-success toggle-on"]'

    el = browser.find_element(By.XPATH, xpath)
    browser.wait_element_become_visible(el)


@when('he clicks in the repo enabled check button')
def click_repo_enabled_check(context):
    browser = context.browser
    xpath = '//div[@class="repo-info-container {}"]'.format(
        'repository-info-enabled-container repo-enabled')
    xpath += '/div/div/label[@class="btn btn-success toggle-on"]'

    el = browser.find_element(By.XPATH, xpath)
    browser.wait_element_become_visible(el)
    browser.click(el)


@then('he sees the repo disabled check button')
def see_repo_disabled_check(context):
    browser = context.browser
    xpath = '//div[@class="repo-info-container {}"]'.format(
        'repository-info-enabled-container repo-enabled')
    xpath += '/div/div/label[@class="btn btn-secondary active toggle-off"]'

    el = browser.find_element(By.XPATH, xpath)
    browser.wait_element_become_visible(el)


@when('he clicks in the close button')
def click_close_btn(context):
    browser = context.browser
    btn = browser.find_element(By.CLASS_NAME, 'close-btn')
    browser.click(btn)
    el = browser.find_element(By.ID, 'no-repos-message')
    browser.wait_element_become_visible(el)


@when('clicks in the manage repositories link')
def click_manage_repos_link(context):
    browser = context.browser
    browser.click_link('manage')
    browser.wait_text_become_present('Manage repositories')
    el = browser.find_element(By.CLASS_NAME, 'fa-plus')
    browser.wait_element_become_visible(el)


@then('he sees a list of repositories')
def see_repo_list(context):
    browser = context.browser
    el = browser.find_elements(By.CLASS_NAME, 'repository-info')[1]
    browser.wait_element_become_visible(el)


@given('the user is in the repository management page')
def is_in_repo_management_page(context):
    pass


@when('he clicks in the repo disabled ckeck button')
def click_repo_disabled_button(context):
    browser = context.browser

    xpath = '//div[@class="repo-info-container {}"]'.format(
        'repository-info-enabled-container repo-disabled')
    xpath += '/div/div/label[@class="btn btn-secondary active toggle-off"]'

    el = browser.find_element(By.XPATH, xpath)
    browser.wait_element_become_visible(el)
    browser.click(el)


@then('he sees the repo enabled check button')
def see_repo_enabled_check(context):
    browser = context.browser

    xpath = '//div[@class="repo-info-container {}"]'.format(
        'repository-info-enabled-container')
    xpath += '/div/div/label[@class="btn btn-success toggle-on"]'

    el = browser.find_element(By.XPATH, xpath)
    browser.wait_element_become_visible(el)


@when('he clicks in the toxicbuild logo')
def clicks_toxicbuild_logo(context):
    browser = context.browser

    el = browser.find_elements(By.CLASS_NAME, 'navbar-brand')[0]
    browser.click(el)
    browser.wait_text_become_present('Your Repositories')
    el = browser.find_elements(By.CLASS_NAME, 'fa-wrench')[0]
    browser.wait_element_become_visible(el)


@when('clicks in the repo menu')
def click_repo_menu(context):
    browser = context.browser

    el = browser.wait_element_become_present(
        lambda: browser.find_elements(By.CLASS_NAME, 'fa-ellipsis-h')[1])
    browser.click(el)

    el = browser.wait_element_become_present(
        lambda: browser.find_elements(By.CLASS_NAME, 'dropdown-menu-right')[1])
    assert el


@when('clicks in the repo settings link')
def click_settings_link(context):
    browser = context.browser
    browser.click_link('Settings')
    browser.wait_text_become_present('General configurations')


@then('he sees the repository settings page')
def see_repo_settings_page(context):
    browser = context.browser

    def fn():
        try:
            el = browser.find_element(By.CLASS_NAME, 'fa-list')
            el = el if el.is_displayed() else None
        except IndexError:
            el = None

        return el

    el = browser.wait_element_become_present(fn)
    assert el


@when('clicks in the delete repo button')
def click_delete_button(context):
    browser = context.browser
    el = browser.find_elements(By.CLASS_NAME, 'btn-delete-repo')[1]
    browser.wait_element_become_visible(el)
    el.click()

    el = browser.find_element(By.ID, 'removeRepoModal')
    browser.wait_element_become_visible(el)


@when('clicks in the delete repo button in the modal')
def click_delete_button_modal(context):
    browser = context.browser
    el = browser.find_element(By.ID, 'btn-remove-obj')
    el.click()
