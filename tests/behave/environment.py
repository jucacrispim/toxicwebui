# -*- coding: utf-8 -*-

import asyncio
import os
from toxiccore.utils import log
from toxicmaster import create_settings_and_connect
from toxicslave import create_settings
from toxicwebui import create_settings as create_settings_ui
from toxicnotifications import (
    create_settings_and_connect as create_settings_output)
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

toxicoutput_conf = os.environ.get('TOXICOUTPUT_SETTINGS')
if not toxicoutput_conf:
    toxicoutput_conf = os.path.join(NOTIFICATIONS_ROOT_DIR, 'toxicoutput.conf')
    os.environ['TOXICOUTPUT_SETTINGS'] = toxicoutput_conf

create_settings()
create_settings_ui()
create_settings_and_connect()
create_settings_output()

from pyrocumulus.auth import AccessToken  # noqa f402
from toxiccommon.exchanges import scheduler_action, conn  # noqa f402
from toxicwebui import settings  # noqa f402
from toxicmaster.users import User  # noqa f402
from toxiccommon.interfaces import (  # noqa 402
    SlaveInterface, RepositoryInterface, BaseInterface)
from tests.functional import (start_slave, stop_slave,  # noqa 402
                              start_master, stop_master,
                              start_poller, stop_poller,
                              start_notifications, stop_notifications,
                              start_webui, stop_webui,
                              start_secrets, stop_secrets,
                              REPO_DIR)
from tests.behave import SeleniumBrowser  # noqa 402


BaseInterface.settings = settings

HERE = os.path.dirname(__file__)
BUILD_SCRIPTS_DIR = os.path.join(HERE, '..', '..', 'build-scripts')


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

    slaves = await SlaveInterface.list(context.user)
    for slave in slaves:
        try:
            await slave.delete()
        except Exception as e:
            log('Error deleting slave ' + str(e), level='warning')


async def del_auth_token(context):
    await AccessToken.drop_collection()


async def create_repo(context):
    """Creates a new repo to be used in tests"""

    from toxicmaster import settings as master_settings
    await conn.connect(**master_settings.RABBITMQ_CONNECTION)
    await scheduler_action.declare()

    repo = await RepositoryInterface.add(
        context.user,
        name='repo-bla', update_seconds=1,
        owner=context.user,
        vcs_type='git', url=REPO_DIR,
        slaves=['repo-slave'])

    await repo.add_branch('master', False)


async def create_user(context):
    user = User(email='someguy@bla.com', is_superuser=True)
    user.set_password('123')
    await user.save()
    context.user = user
    context.user.id = str(context.user.id)


async def del_user(context):
    await context.user.delete()


async def del_repo(context):
    """Deletes the repositories created in tests."""

    repos = await RepositoryInterface.list(context.user)
    for repo in repos:
        try:
            await repo.delete()
            # await scheduler_action.declare()
            # await scheduler_action.queue_delete()
            # await scheduler_action.connection.disconnect()
        except Exception as e:
            log('Error deleting repo ' + str(e), level='warning')

    from toxicmaster.repository import Repository as RepoModel

    await RepoModel.drop_collection()


async def create_root_user(context):
    user = User(id=settings.ROOT_USER_ID, username='already-exists',
                email='nobody@nowhere.nada', allowed_actions=['add_user'])
    await user.save(force_insert=True)


def before_all(context):
    if not os.environ.get('TEST_DOCKER_IMAGES'):
        start_slave()
        start_poller()
        start_notifications()
        start_secrets()
        start_master()
        start_webui()

    create_browser(context)

    async def create(context):
        await create_user(context)

    loop = asyncio.get_event_loop()
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

    loop = asyncio.get_event_loop()
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
        await User.objects(username='already-exists').delete()
        await User.objects(username='already-existsa-good-username').delete()

    loop = asyncio.get_event_loop()
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

    loop = asyncio.get_event_loop()
    loop.run_until_complete(delete(context))

    quit_browser(context)
