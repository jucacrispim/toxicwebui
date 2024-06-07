# -*- coding: utf-8 -*-

# Copyright 2017, 2023 Juca Crispim <juca@poraodojuca.net>

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

from unittest import TestCase
from unittest.mock import Mock, patch, AsyncMock
from toxiccommon import interfaces
from toxicwebui import utils
from tests import async_test


class UtilsDateTimeTest(TestCase):

    @patch.object(utils, 'settings', Mock())
    def test_get_dtformat(self):
        utils.settings.DTFORMAT = '%y %a'
        returned = utils.get_dtformat()
        self.assertEqual(returned, utils.settings.DTFORMAT)

    def test_get_dtformat_no_settings(self):
        returned = utils.get_dtformat()
        self.assertEqual(returned, utils.DTFORMAT)


class BuildsetUtilsTest(TestCase):

    @async_test
    async def setUp(self):
        self.user = Mock()

    @patch.object(interfaces.BuilderInterface, 'list', AsyncMock(
        spec=interfaces.BuilderInterface.list))
    @async_test
    async def test_get_builders_for_buildset(self):
        builder_dict = {'id': 'the-id', 'name': 'asdf'}
        buildset_dict = {
            'id': 'some-repo-id',
            'commit': '9023840238',
            'branch': 'master',
            'author': 'zé',
            'title': 'the commit',
            'builds': [
                {
                    'uuid': 'the uuid',
                    'builder': builder_dict
                }
            ]
        }
        buildset = interfaces.BuildSetInterface(
            self.user, ordered_kwargs=buildset_dict)

        interfaces.BuilderInterface.list.return_value = [
            interfaces.BuilderInterface(
                self.user, ordered_kwargs=builder_dict)]

        returned = await utils.get_builders_for_buildsets(self.user,
                                                          [buildset])
        called_args = interfaces.BuilderInterface.list.call_args[1]

        expected = {'id__in': ['the-id']}
        self.assertEqual(expected, called_args)

        self.assertEqual(returned[0].id, 'the-id')
