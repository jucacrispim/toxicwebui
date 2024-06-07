# -*- coding: utf-8 -*-

import os
import socket
import sys
import time
import tornado
from unittest import TestCase

import bcrypt
from pyrocumulus.auth import AccessToken

from toxiccore import BaseToxicClient
from toxiccore.utils import bcrypt_string, log
from toxicmaster import create_settings_and_connect
from toxicslave import create_settings
from toxicpoller import create_settings as create_settings_poller
from toxicwebui import create_settings as create_settings_ui

from tests import TEST_DATA_DIR

from toxicnotifications import (
    create_settings_and_connect as create_settings_notif)


SOURCE_DIR = os.path.join(TEST_DATA_DIR, '..')
REPO_DIR = os.path.join(TEST_DATA_DIR, 'repo')
SLAVE_ROOT_DIR = TEST_DATA_DIR
MASTER_ROOT_DIR = TEST_DATA_DIR
POLLER_ROOT_DIR = TEST_DATA_DIR
NOTIFICATIONS_ROOT_DIR = TEST_DATA_DIR
SECRETS_ROOT_DIR = TEST_DATA_DIR
PYVERSION = ''.join([str(n) for n in sys.version_info[:2]])

toxicmaster_conf = os.environ.get('TOXICMASTER_SETTINGS')
if not toxicmaster_conf:
    toxicmaster_conf = os.path.join(MASTER_ROOT_DIR, 'toxicmaster.conf')
    os.environ['TOXICMASTER_SETTINGS'] = toxicmaster_conf

toxicpoller_conf = os.environ.get('TOXICPOLLER_SETTINGS')
if not toxicpoller_conf:
    toxicpoller_conf = os.path.join(POLLER_ROOT_DIR, 'toxicpoller.conf')
    os.environ['TOXICPOLLER_SETTINGS'] = toxicpoller_conf

toxicslave_conf = os.environ.get('TOXICSLAVE_SETTINGS')
if not toxicslave_conf:
    toxicslave_conf = os.path.join(SLAVE_ROOT_DIR, 'toxicslave.conf')
    os.environ['TOXICSLAVE_SETTINGS'] = toxicslave_conf


toxicnotifications_conf = os.environ.get('TOXICNOTIFICATIONS_SETTINGS')
if not toxicnotifications_conf:
    toxicnotifications_conf = os.path.join(
        NOTIFICATIONS_ROOT_DIR, 'toxicnotifications.conf')
    os.environ['TOXICNOTIFICATIONS_SETTINGS'] = toxicnotifications_conf


toxicwebui_conf = os.environ.get('TOXICWEBUI_SETTINGS')
if not toxicwebui_conf:
    toxicwebui_conf = os.path.join(
        TEST_DATA_DIR, 'toxicwebui.conf')
    os.environ['TOXICWEBUI_SETTINGS'] = toxicwebui_conf


create_settings()
create_settings_and_connect()
create_settings_notif()
create_settings_poller()
create_settings_ui()


def start_slave(sleep=0.5):
    """Starts an slave server in a new process for tests"""

    toxicslave_conf = os.environ.get('TOXICSLAVE_SETTINGS')
    pidfile = 'toxicslave{}.pid'.format(PYVERSION)
    toxicslave_cmd = 'toxicslave'
    cmd = ['export', 'PYTHONPATH="{}"'.format(SOURCE_DIR), '&&',
           toxicslave_cmd, 'start', SLAVE_ROOT_DIR, '--daemonize',
           '--pidfile', pidfile, '--loglevel', 'debug']

    if toxicslave_conf:
        cmd += ['-c', toxicslave_conf]

    os.system(' '.join(cmd))


def stop_slave():
    """Stops the test slave"""

    toxicslave_cmd = 'toxicslave'
    pidfile = 'toxicslave{}.pid'.format(PYVERSION)
    cmd = ['export', 'PYTHONPATH="{}"'.format(SOURCE_DIR), '&&',
           toxicslave_cmd, 'stop', SLAVE_ROOT_DIR,
           '--pidfile', pidfile, '--kill']

    os.system(' '.join(cmd))


def start_poller():

    toxicpoller_conf = os.environ.get('TOXICPOLLER_SETTINGS')
    pidfile = 'toxicpoller{}.pid'.format(PYVERSION)
    toxicpoller_cmd = 'toxicpoller'
    cmd = ['export', 'PYTHONPATH="{}"'.format(SOURCE_DIR), '&&',
           toxicpoller_cmd, 'start', POLLER_ROOT_DIR, '--daemonize',
           '--pidfile', pidfile, '--loglevel', 'debug']

    if toxicpoller_conf:
        cmd += ['-c', toxicpoller_conf]

    os.system(' '.join(cmd))


def stop_poller():

    toxicpoller_cmd = 'toxicpoller'
    pidfile = 'toxicpoller{}.pid'.format(PYVERSION)
    cmd = ['export', 'PYTHONPATH="{}"'.format(SOURCE_DIR), '&&',
           'python', toxicpoller_cmd, 'stop', POLLER_ROOT_DIR,
           '--pidfile', pidfile, '--kill']

    os.system(' '.join(cmd))


def wait_master_to_be_alive(root_dir):
    from toxicmaster import settings
    HOST = settings.HOLE_ADDR
    PORT = settings.HOLE_PORT
    alive = False
    limit = int(os.environ.get('FUNCTESTS_MASTER_START_TIMEOUT', 20))
    step = 0.5
    i = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        while not alive and i < limit:
            try:
                s.connect((HOST, PORT))
                s.close()
            except Exception:
                alive = False
            else:
                alive = True
                break

            time.sleep(step)
            i += step

    if not alive:
        log(f'Master did not start at {HOST}:{PORT} in {limit} seconds',
            level='error')
        logfile = os.path.join(root_dir, 'toxicmaster.log')
        os.system(f'tail --lines 100 {logfile}')


def start_master(sleep=0.5):
    """Starts a master server in a new process for tests"""

    toxicmaster_conf = os.environ.get('TOXICMASTER_SETTINGS')

    toxicmaster_cmd = 'toxicmaster'
    pidfile = 'toxicmaster{}.pid'.format(PYVERSION)
    cmd = ['export', 'PYTHONPATH="{}"'.format(SOURCE_DIR), '&&',
           toxicmaster_cmd, 'start', MASTER_ROOT_DIR, '--daemonize',
           '--pidfile', pidfile, '--loglevel', 'debug']

    if toxicmaster_conf:
        cmd += ['-c', toxicmaster_conf]

    os.system(' '.join(cmd))

    wait_master_to_be_alive(MASTER_ROOT_DIR)


def stop_master():
    """Stops the master test server"""

    toxicmaster_cmd = 'toxicmaster'
    pidfile = 'toxicmaster{}.pid'.format(PYVERSION)

    cmd = ['export', 'PYTHONPATH="{}"'.format(SOURCE_DIR), '&&',
           toxicmaster_cmd, 'stop', MASTER_ROOT_DIR,
           '--pidfile', pidfile, '--kill']

    os.system(' '.join(cmd))


def start_secrets(sleep=0.5):
    """Starts a secrets server in a new process for tests"""

    toxicsecrets_conf = os.environ.get('TOXICSECRETS_SETTINGS')

    toxicsecrets_cmd = 'toxicsecrets'
    pidfile = 'toxicsecrets{}.pid'.format(PYVERSION)
    cmd = ['export', 'PYTHONPATH="{}"'.format(SOURCE_DIR), '&&',
           toxicsecrets_cmd, 'start', SECRETS_ROOT_DIR, '--daemonize',
           '--pidfile', pidfile, '--loglevel', 'debug']

    if toxicsecrets_conf:
        cmd += ['-c', toxicsecrets_conf]

    os.system(' '.join(cmd))


def stop_secrets():
    """Stops the secrets test server"""

    toxicsecrets_cmd = 'toxicsecrets'
    pidfile = 'toxicsecrets{}.pid'.format(PYVERSION)

    cmd = ['export', 'PYTHONPATH="{}"'.format(SOURCE_DIR), '&&',
           toxicsecrets_cmd, 'stop', SECRETS_ROOT_DIR,
           '--pidfile', pidfile, '--kill']

    os.system(' '.join(cmd))


def start_notifications(sleep=0.5):
    """Starts a toxicnotifications instance in a new process for tests"""

    conf = os.path.join(NOTIFICATIONS_ROOT_DIR, 'toxicnotifications.conf')

    cmd = 'toxicnotifications'
    pidfile = 'toxicnotifications{}.pid'.format(PYVERSION)
    cmd = ['export', 'PYTHONPATH="{}"'.format(SOURCE_DIR), '&&', 'python',
           cmd, 'start', NOTIFICATIONS_ROOT_DIR, '--daemonize',
           '--pidfile', pidfile, '--loglevel', 'debug']

    if conf:
        cmd += ['-c', conf]

    os.system(' '.join(cmd))


def stop_notifications():
    """Stops the toxicnotifications test server"""

    cmd = 'toxicnotifications'
    pidfile = 'toxicnotifications{}.pid'.format(PYVERSION)

    cmd = ['export', 'PYTHONPATH="{}"'.format(SOURCE_DIR), '&&',
           'python', cmd, 'stop', NOTIFICATIONS_ROOT_DIR,
           '--pidfile', pidfile, '--kill']

    os.system(' '.join(cmd))


def start_webui(sleep=0.5):
    """Starts a toxicwebui instance in a new process for tests"""

    conf = os.path.join(TEST_DATA_DIR, 'toxicwebui.conf')

    cmd = os.path.join(SOURCE_DIR, 'toxicwebui', 'cmds.py')
    pidfile = 'toxicwebui{}.pid'.format(PYVERSION)
    cmd = ['export', 'PYTHONPATH="{}"'.format(SOURCE_DIR), '&&', 'python',
           cmd, 'start', TEST_DATA_DIR, '--daemonize',
           '--pidfile', pidfile, '--loglevel', 'debug']

    if conf:
        cmd += ['-c', conf]

    os.system(' '.join(cmd))


def stop_webui():
    """Stops a toxicwebui instance"""

    conf = os.path.join(TEST_DATA_DIR, 'toxicwebui.conf')

    cmd = os.path.join(SOURCE_DIR, 'toxicwebui', 'cmds.py')
    pidfile = 'toxicwebui{}.pid'.format(PYVERSION)
    cmd = ['export', 'PYTHONPATH="{}"'.format(SOURCE_DIR), '&&', 'python',
           cmd, 'stop', TEST_DATA_DIR,
           '--pidfile', pidfile]

    if conf:
        cmd += ['-c', conf]

    os.system(' '.join(cmd))


def start_customwebserver():
    """Start the custom web server for tests """

    custom_cmd = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'custom_webhook.py')
    pidfile = 'customwh{}.pid'.format(PYVERSION)
    cmd = ['export', 'PYTHONPATH="{}"'.format(SOURCE_DIR), '&&', 'python',
           custom_cmd, 'start', MASTER_ROOT_DIR, '--daemonize',
           '--pidfile', pidfile]

    os.system(' '.join(cmd))


def stop_customwebserver():
    """Stops the custom web server"""

    custom_cmd = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'custom_webhook.py')
    pidfile = 'customwh{}.pid'.format(PYVERSION)

    cmd = ['export', 'PYTHONPATH="{}"'.format(SOURCE_DIR), '&&',
           'python', custom_cmd, 'stop', MASTER_ROOT_DIR,
           '--pidfile', pidfile]

    os.system(' '.join(cmd))


def start_all():
    start_slave()
    start_poller()
    start_master()
    start_notifications()
    start_customwebserver()


def stop_all():
    stop_customwebserver()
    stop_poller()
    stop_master()
    stop_notifications()
    stop_slave()


class BaseFunctionalTest(TestCase):

    """An AsyncTestCase that starts a master and a slave process on
    setUpClass and stops it on tearDownClass"""

    @classmethod
    def start_slave(cls):
        start_slave()

    @classmethod
    def stop_slave(cls):
        stop_slave()

    @classmethod
    def start_master(cls):
        start_master()

    @classmethod
    def stop_master(cls):
        stop_master()

    @classmethod
    def start_custom(cls):
        start_customwebserver()

    @classmethod
    def stop_custom(cls):
        stop_customwebserver()

    @classmethod
    def start_poller(cls):
        start_poller()

    @classmethod
    def stop_poller(cls):
        stop_poller()

    @classmethod
    def start_notifications(cls):
        start_notifications()

    @classmethod
    def stop_notifications(cls):
        stop_notifications()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.start_slave()
        cls.start_poller()
        cls.start_master()
        cls.start_notifications()
        start_customwebserver()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        stop_customwebserver()
        cls.stop_poller()
        cls.stop_master()
        cls.stop_notifications()
        cls.stop_slave()

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()


STREAM_EVENT_TYPES = ['build_added', 'build_started', 'build_finished',
                      'step_started', 'step_finished', 'step_output_arrived',
                      'repo_added', 'buildset_started', 'buildset_finished']


class DummyMasterHoleClient(BaseToxicClient):

    def __init__(self, user, *args, **kwargs):
        kwargs['use_ssl'] = True
        kwargs['validate_cert'] = False
        super().__init__(*args, **kwargs)
        self.user = user

    async def request2server(self, action, body):

        data = {'action': action, 'body': body,
                'user_id': str(self.user.id),
                'token': '123'}
        await self.write(data)
        response = await self.get_response()
        return response['body'][action]

    async def create_slave(self, slave_port):
        action = 'slave-add'
        body = {'slave_name': 'test-slave',
                'slave_host': 'localhost',
                'slave_port': slave_port,
                'slave_token': '123',
                'owner_id': str(self.user.id),
                'use_ssl': True,
                'validate_cert': False}
        resp = await self.request2server(action, body)
        return resp

    async def create_repo(self):
        action = 'repo-add'
        body = {'repo_name': 'test-repo', 'repo_url': REPO_DIR,
                'vcs_type': 'git', 'update_seconds': 1,
                'slaves': ['test-slave'],
                'owner_id': str(self.user.id)}

        resp = await self.request2server(action, body)

        return resp

    async def wait_clone(self):
        await self.write({'action': 'stream', 'token': '123',
                          'body': {'event_types': STREAM_EVENT_TYPES},
                          'user_id': str(self.user.id)})
        while True:
            r = await self.get_response()
            body = r['body'] if r else {}
            try:
                event = body['event_type']
                if event == 'repo_status_changed':
                    break
            except KeyError:
                pass

    async def start_build(self, builder='builder-1'):

        action = 'repo-start-build'
        body = {'repo_name_or_id': 'toxic/test-repo',
                'branch': 'master'}
        if builder:
            body['builder_name_or_id'] = builder
        resp = await self.request2server(action, body)

        return resp

    async def wait_build_complete(self):
        await self.write({'action': 'stream', 'token': '123',
                          'body': {'event_types': STREAM_EVENT_TYPES},
                          'user_id': str(self.user.id)})

        # this ugly part here it to wait for the right message
        # If we don't use this we may read the wrong message and
        # the test will fail.
        while True:
            response = await self.get_response()
            body = response['body'] if response else {}
            if body.get('event_type') == 'build_finished':
                has_sleep = False
                for step in body['steps']:
                    if step['command'] == 'sleep 3':
                        has_sleep = True

                if not has_sleep:
                    break
        return response


async def create_output_access_token():
    from toxicwebui import settings

    real_token = bcrypt_string(settings.ACCESS_TOKEN_BASE, bcrypt.gensalt(8))
    token = AccessToken(token_id=settings.ACCESS_TOKEN_ID,
                        token=real_token)
    await token.save()
