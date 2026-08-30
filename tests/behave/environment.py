# -*- coding: utf-8 -*-

import asyncio
import os
from toxiccore.utils import log, bcrypt_string
from toxicwebui import create_settings as create_settings_ui
from tests.functional import (REPO_DIR,
                              SLAVE_ROOT_DIR, MASTER_ROOT_DIR,
                              TEST_DATA_DIR,
                              NOTIFICATIONS_ROOT_DIR,
                              create_output_access_token)

# settings needed to the test data. This needs to be before the
# import from ui.models

toxicmaster_conf = os.environ.get('TOXICMASTER_SETTINGS')
if not toxicmaster_conf:
    toxicmaster_conf = os.path.join(MASTER_ROOT_DIR, 'toxicmaster.conf')
    os.environ['TOXICMASTER_SETTINGS'] = toxicmaster_conf

toxicslave_conf = os.environ.get('TOXICSLAVE_SETTINGS')
if not toxicslave_conf:
    toxicslave_conf = os.path.join(SLAVE_ROOT_DIR, 'toxicslave.conf')
    os.environ['TOXICSLAVE_SETTINGS'] = toxicslave_conf

toxicweb_conf = os.environ.get('TOXICWEBUI_SETTINGS')
if not toxicweb_conf:
    toxicweb_conf = os.path.join(TEST_DATA_DIR, 'toxicwebui.conf')
    os.environ['TOXICWEBUI_SETTINGS'] = toxicweb_conf

create_settings_ui()

from pyrocumulus.auth import AccessToken  # noqa f402
from toxicwebui import settings  # noqa f402
from toxiccommon.interfaces import (  # noqa 402
    SlaveInterface, RepositoryInterface, BaseInterface)
from tests.functional import (start_slave, stop_slave,  # noqa 402
                              start_master, stop_master,
                              start_poller, stop_poller,
                              start_notifications, stop_notifications,
                              start_webui, stop_webui,
                              start_secrets, stop_secrets,
                              drop_test_data,
                              REPO_DIR)
from tests.behave import SeleniumBrowser  # noqa 402

# The async mongo client (and the whole suite) is bound to a single event
# loop created in tests/__init__.py. We reuse that same loop in all hooks,
# otherwise the mongomotor connection raises "Cannot use AsyncMongoClient in
# different event loop" and the after_feature cleanup never runs (leaving
# duplicated slaves/repos behind).
from tests import loop as _loop  # noqa 402
asyncio.set_event_loop(_loop)


BaseInterface.settings = settings

HERE = os.path.dirname(__file__)
BUILD_SCRIPTS_DIR = os.path.join(HERE, '..', '..', 'build-scripts')


class Requester:
    """A minimal requester for the interfaces. The master identifies the
    user through its ``id`` (the same way the webui does when talking to
    the master through the hole)."""

    def __init__(self, id, email='someguy@bla.com'):
        self.id = id
        self.email = email


async def get_db():
    from mongomotor.connection import get_connection
    conn = get_connection()
    return conn[os.environ.get('DBNAME', 'toxicnotifications-test')]


async def create_user(context):
    """Creates the ``someguy`` user directly in the master database and
    stores a lightweight requester in the context."""

    import bcrypt
    from bson.objectid import ObjectId

    db = await get_db()
    coll = db['user']
    password = bcrypt_string('123', bcrypt.gensalt(8))
    user_id = ObjectId()
    await coll.insert_one({
        '_id': user_id,
        'email': 'someguy@bla.com',
        'username': 'someguy',
        'password': password,
        'is_superuser': True,
        'allowed_actions': ['add_user', 'add_repo', 'add_slave',
                            'remove_user', 'remove_repo', 'remove_slave'],
        'organizations': [],
        'member_of': [],
    })
    context.user = Requester(user_id)


async def del_user(context):
    db = await get_db()
    await db['user'].delete_many({'username': 'someguy'})


async def create_root_user(context):
    from bson.objectid import ObjectId

    db = await get_db()
    coll = db['user']
    doc = await coll.find_one({'_id': ObjectId(settings.ROOT_USER_ID)})
    if doc:
        return

    await coll.insert_one({
        '_id': ObjectId(settings.ROOT_USER_ID),
        'email': 'nobody@nowhere.nada',
        'username': 'already-exists',
        'allowed_actions': ['add_user'],
        'organizations': [],
        'member_of': [],
    })


def create_browser(context):
    """Creates a new selenium browser using Chrome driver and
    sets it in the behave context.

    :param context: Behave's context."""
    context.browser = SeleniumBrowser()


def quit_browser(context):
    """Quits the selenium browser.

    :param context: Behave's context."""
    context.browser.quit()


async def create_slave(context):
    """Creates a slave to be used in repo tests"""

    from toxicwebui import settings

    await SlaveInterface.add(
        context.user, name='repo-slave', host=settings.TEST_SLAVE_HOST,
        owner=context.user,
        port=2222,
        token='123',
        use_ssl=True,
        validate_cert=False)


async def del_slave(context):
    """Deletes the slaves created in the tests"""

    db = await get_db()
    await db['slave'].delete_many({})


async def del_auth_token(context):
    await AccessToken.drop_collection()


async def create_repo(context):
    """Creates a new repo to be used in tests"""

    repo = await RepositoryInterface.add(
        context.user,
        name='repo-bla', update_seconds=1,
        owner=context.user,
        vcs_type='git', url=REPO_DIR,
        slaves=['repo-slave'])

    await repo.add_branch('master', False)


async def del_repo(context):
    """Deletes the repositories created in tests."""

    db = await get_db()
    await db['repository'].delete_many({})


def before_all(context):
    if not os.environ.get('TEST_DOCKER_IMAGES'):
        # Clean the test database so we always start with a fresh state.
        # Without this, re-running the suite leaves duplicated users/slaves
        # behind and the login/`slave_get` calls fail with
        # ``MultipleObjectsReturned``.
        drop_test_data()

        start_slave()
        start_poller()
        start_notifications()
        start_secrets()
        start_master()
        start_webui()

    create_browser(context)

    async def create(context):
        await create_user(context)

    loop = _loop
    loop.run_until_complete(create(context))


def before_feature(context, feature):
    """Executed before every feature. It starts a slave, a master,
    a webui and creates a selenium browser.

    :param context: Behave's context.
    :param feature: The feature being executed."""

    fname = feature.filename.split(os.path.sep)[-1]

    async def create(context):
        await create_slave(context)
        create_repo_features = ['waterfall.feature', 'notifications.feature',
                                'buildset.feature', 'build.feature']
        if fname in create_repo_features:
            await create_repo(context)

            if fname == 'notifications.feature':
                await create_output_access_token()

        elif fname == 'register.feature':
            await create_root_user(context)

    loop = _loop
    loop.run_until_complete(create(context))


def after_feature(context, feature):
    """Executed after every feature. It stops the webui, the master,
    the slave, quits the selenium browser and deletes data created in
    tests.

    :param context: Behave's context.
    :param feature: The feature that was executed."""

    async def delete(context):
        await del_slave(context)
        await del_repo(context)
        await del_auth_token(context)

    loop = _loop
    loop.run_until_complete(delete(context))


def before_scenario(context, scenario):
    if scenario.name == 'A user cancels a build':
        # we stop the slave so we can be sure the build is pending
        # when we try to cancel it
        stop_slave()


def after_scenario(context, scenario):
    if scenario.name == 'A user cancels a build':
        # starting it for the other tests, if any
        start_slave()


def after_all(context):

    if not os.environ.get('TEST_DOCKER_IMAGES'):
        stop_webui()
        stop_notifications()
        stop_secrets()
        stop_poller()
        stop_master()
        stop_slave()

    async def delete(context):
        await del_user(context)

    loop = _loop
    loop.run_until_complete(delete(context))

    quit_browser(context)
