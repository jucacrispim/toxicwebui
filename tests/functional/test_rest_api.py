# -*- coding: utf-8 -*-
# Copyright 2018, 2024 Juca Crispim <juca@poraodojuca.net>

# This file is part of toxicbuild.

# toxicbuild is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# toxicbuild is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with toxicbuild. If not, see <http://www.gnu.org/licenses/>.

import json
from unittest import TestCase
import requests
from pyrocumulus.auth import AccessToken
from toxicmaster.repository import Repository as RepoDBModel
from toxicmaster.slave import Slave as SlaveDBModel
from toxicmaster.users import User as UserDBModel
from toxicnotifications.base import Notification
from toxicwebui import settings
from tests import async_test
from tests.functional import (
    start_master,
    stop_master,
    start_webui,
    stop_webui,
    start_notifications,
    stop_notifications,
    create_output_access_token,
    start_secrets,
    stop_secrets,
    start_slave,
    stop_slave,
)


def setUpModule():
    start_slave()
    start_secrets()
    start_master()
    start_webui()
    start_notifications()


def tearDownModule():
    stop_slave()
    stop_master()
    stop_secrets()
    stop_webui()
    stop_notifications()


def _do_login():
    session = requests.session()
    url = settings.LOGIN_URL
    session.post(url, data=json.dumps({
        'username_or_email': 'a@a.com',
        'password': '123'}))
    return session


class UserRestAPITest(TestCase):

    @async_test
    async def setUp(self):
        self.user = UserDBModel(email='a@a.com',
                                allowed_actions=['add_repo', 'add_slave'])
        self.user.set_password('123')
        await self.user.save()
        self.session = _do_login()

    @async_test
    async def tearDown(self):
        await UserDBModel.drop_collection()
        self.session.close()

    @async_test
    async def test_user_change_password(self):
        url = settings.USER_API_URL
        data = {'old_password': '123',
                'new_password': '456'}

        self.session.post(url + 'change-password', data=json.dumps(data))

        r = await type(self.user).authenticate('a@a.com', '456')
        self.assertTrue(r)


class RepositoryRestAPITest(TestCase):

    @async_test
    async def setUp(self):
        self.user = UserDBModel(email='a@a.com',
                                allowed_actions=['add_repo', 'add_slave'])
        self.user.set_password('123')
        await self.user.save()
        self.session = requests.session()
        self.slave = SlaveDBModel(name='someslave', host='localhost',
                                  port=1234, use_ssl=False,
                                  owner=self.user, token='some-token')
        await self.slave.save()
        self.session = _do_login()

    @async_test
    async def tearDown(self):
        await RepoDBModel.drop_collection()
        await UserDBModel.drop_collection()
        await SlaveDBModel.drop_collection()
        self.session.close()

    def test_repo_add(self):
        url = settings.REPO_API_URL
        data = {'name': 'somerepo', 'url': 'https://somebla.com',
                'vcs_type': 'git'}

        self.session.post(url, data=json.dumps(data))

        resp = self.session.get(url)
        repos = resp.json()
        self.assertEqual(len(repos['items']), 1)

    def test_repo_remove(self):
        url = settings.REPO_API_URL
        data = {'name': 'somerepo', 'url': 'https://somebla.com',
                'vcs_type': 'git'}
        self.session.post(url, data=json.dumps(data))
        self.session.delete(url + '?name=a/somerepo')
        resp = self.session.get(url)
        repos = resp.json()
        self.assertEqual(len(repos['items']), 0)

    def test_repo_add_slave(self):
        url = settings.REPO_API_URL
        data = {'name': 'somerepo', 'url': 'https://somebla.com',
                'vcs_type': 'git'}
        self.session.post(url, data=json.dumps(data))
        slave_data = {'name': 'a/someslave'}

        resp = self.session.post(url + 'add-slave?name=a/somerepo',
                                 data=json.dumps(slave_data))
        json_resp = resp.json()
        self.assertEqual(json_resp['repo-add-slave'], 'slave added')

    def test_repo_remove_slave(self):
        url = settings.REPO_API_URL
        data = {'name': 'somerepo', 'url': 'https://somebla.com',
                'vcs_type': 'git'}
        self.session.post(url, data=json.dumps(data))
        slave_data = {'name': 'a/someslave'}

        resp = self.session.post(url + 'add-slave?name=a/somerepo',
                                 data=json.dumps(slave_data))

        resp = self.session.post(url + 'remove-slave?name=a/somerepo',
                                 data=json.dumps(slave_data))

        json_resp = resp.json()
        self.assertEqual(json_resp['repo-remove-slave'], 'slave removed')

    def test_repo_add_branch(self):
        url = settings.REPO_API_URL
        data = {'name': 'somerepo', 'url': 'https://somebla.com',
                'vcs_type': 'git'}
        self.session.post(url, data=json.dumps(data))

        branch_data = {'add_branches': [{'branch_name': 'master',
                                         'notify_only_latest': True}]}
        resp = self.session.post(url + 'add-branch?name=a/somerepo',
                                 data=json.dumps(branch_data))
        self.assertEqual(resp.json()['repo-add-branch'], '1 branches added')

    def test_repo_remove_branch(self):
        url = settings.REPO_API_URL
        data = {'name': 'somerepo', 'url': 'https://somebla.com',
                'vcs_type': 'git'}
        self.session.post(url, data=json.dumps(data))

        branch_data = {'add_branches': [{'branch_name': 'master',
                                         'notify_only_latest': True}]}
        self.session.post(url + 'add-branch?name=a/somerepo',
                          data=json.dumps(branch_data))
        rm_data = {'remove_branches': ['master']}
        resp = self.session.post(url + 'remove-branch?name=a/somerepo',
                                 data=json.dumps(rm_data))

        self.assertEqual(
            resp.json()['repo-remove-branch'], '1 branches removed')

    def test_repo_add_secret(self):
        url = settings.REPO_API_URL
        data = {'name': 'somerepo', 'url': 'https://somebla.com',
                'vcs_type': 'git'}
        self.session.post(url, data=json.dumps(data))

        branch_data = {'add_branches': [{'branch_name': 'master',
                                         'notify_only_latest': True}]}
        self.session.post(url + 'add-branch?name=a/somerepo',
                          data=json.dumps(branch_data))

        url = settings.REPO_API_URL + 'add-secret?name=a/somerepo'
        data = {'key': 'the key', 'value': 'val'}
        self.session.post(url, data=json.dumps(data))
        url = settings.REPO_API_URL + 'get-secrets?name=a/somerepo'
        secrets = self.session.get(url)
        self.assertEqual(secrets.status_code, 200)
        self.assertEqual(secrets.json()['the key'], 'val')

    def test_repo_rm_secret(self):
        url = settings.REPO_API_URL
        data = {'name': 'somerepo', 'url': 'https://somebla.com',
                'vcs_type': 'git'}
        self.session.post(url, data=json.dumps(data))

        branch_data = {'add_branches': [{'branch_name': 'master',
                                         'notify_only_latest': True}]}
        self.session.post(url + 'add-branch?name=a/somerepo',
                          data=json.dumps(branch_data))

        url = settings.REPO_API_URL + 'add-secret?name=a/somerepo'
        data = {'key': 'the key', 'value': 'val'}
        self.session.post(url, data=json.dumps(data))
        url = settings.REPO_API_URL + 'rm-secret?name=a/somerepo'
        data = {'key': 'the key'}
        self.session.post(url, data=json.dumps(data))

        url = settings.REPO_API_URL + 'get-secrets?name=a/somerepo'
        secrets = self.session.get(url)
        self.assertEqual(secrets.status_code, 200)
        self.assertEqual(len(secrets.json().keys()), 0)

    def test_repo_replace_secrets(self):
        url = settings.REPO_API_URL
        data = {'name': 'somerepo', 'url': 'https://somebla.com',
                'vcs_type': 'git'}
        self.session.post(url, data=json.dumps(data))

        branch_data = {'add_branches': [{'branch_name': 'master',
                                         'notify_only_latest': True}]}
        self.session.post(url + 'add-branch?name=a/somerepo',
                          data=json.dumps(branch_data))

        url = settings.REPO_API_URL + 'add-secret?name=a/somerepo'
        data = {'key': 'the key', 'value': 'val'}
        self.session.post(url, data=json.dumps(data))
        url = settings.REPO_API_URL + 'replace-secrets?name=a/somerepo'
        data = {'the key': 'other val'}
        self.session.post(url, data=json.dumps(data))
        url = settings.REPO_API_URL + 'get-secrets?name=a/somerepo'
        secrets = self.session.get(url)
        self.assertEqual(secrets.status_code, 200)
        self.assertEqual(secrets.json()['the key'], 'other val')


class SlaveRestAPITest(TestCase):

    @async_test
    async def setUp(self):
        self.user = UserDBModel(email='a@a.com',
                                allowed_actions=['add_repo', 'add_slave'])
        self.user.set_password('123')
        await self.user.save()
        self.session = _do_login()

    @async_test
    async def tearDown(self):
        await UserDBModel.drop_collection()
        await SlaveDBModel.drop_collection()
        self.session.close()

    def test_slave_add(self):
        url = settings.SLAVE_API_URL
        data = {'name': 'someslave', 'token': 'asdf', 'host': 'localhost',
                'port': 1234, 'use_ssl': False}
        self.session.post(url, data=json.dumps(data))

        resp = self.session.get(url)
        repos = resp.json()
        self.assertEqual(len(repos['items']), 1)

    def test_repo_remove(self):
        url = settings.REPO_API_URL
        data = {'name': 'someslave', 'token': 'asdf', 'host': 'localhost',
                'port': 1234, 'use_ssl': False}
        self.session.post(url, data=json.dumps(data))
        self.session.delete(url + '?name=someslave')
        resp = self.session.get(url)
        repos = resp.json()
        self.assertEqual(len(repos['items']), 0)


class NotificationRestApiTest(TestCase):

    @async_test
    async def setUp(self):

        await create_output_access_token()
        # login
        self.user = UserDBModel(email='a@a.com',
                                allowed_actions=['add_repo', 'add_slave'])
        self.user.set_password('123')
        await self.user.save()

        self.session = _do_login()

    @async_test
    async def tearDown(self):
        await UserDBModel.drop_collection()
        await AccessToken.drop_collection()
        await Notification.drop_collection()

    def test_enable(self):
        url = settings.NOTIFICATION_API_URL + 'custom-webhook/some-id'
        data = {'webhook_url': 'http://bla.nada'}
        r = self.session.post(url, data=json.dumps(data))
        r.connection.close()
        self.assertTrue(r.status_code, 200)

    def test_disable(self):
        url = settings.NOTIFICATION_API_URL + 'custom-webhook/some-id'

        data = {'webhook_url': 'http://bla.nada'}
        r = self.session.post(url, data=json.dumps(data))
        r.connection.close()
        self.assertTrue(r.status_code, 200)

        r = self.session.delete(url)
        r.connection.close()
        self.assertTrue(r.status_code, 200)
