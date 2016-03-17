from __future__ import absolute_import
from __future__ import unicode_literals

import os

import mock
import pytest

from compose.config.interpolation import BlankDefaultDict
from compose.config.interpolation import interpolate
from compose.config.interpolation import interpolate_environment_variables


@pytest.yield_fixture
def mock_env():
    with mock.patch.dict(os.environ):
        os.environ['USER'] = 'jenny'
        os.environ['FOO'] = 'bar'
        yield


@pytest.fixture
def variable_mapping():
    return BlankDefaultDict({
        'FOO': 'first',
        'BAR': 'second',
        'EMPTY': ''
    })


def test_interpolate_environment_variables_in_services(mock_env):
    services = {
        'servivea': {
            'image': 'example:${USER}',
            'volumes': ['$FOO:/target'],
            'logging': {
                'driver': '${FOO}',
                'options': {
                    'user': '$USER',
                }
            }
        }
    }
    expected = {
        'servivea': {
            'image': 'example:jenny',
            'volumes': ['bar:/target'],
            'logging': {
                'driver': 'bar',
                'options': {
                    'user': 'jenny',
                }
            }
        }
    }
    assert interpolate_environment_variables(services, 'service') == expected


def test_interpolate_environment_variables_in_volumes(mock_env):
    volumes = {
        'data': {
            'driver': '$FOO',
            'driver_opts': {
                'max': 2,
                'user': '${USER}'
            }
        },
        'other': None,
    }
    expected = {
        'data': {
            'driver': 'bar',
            'driver_opts': {
                'max': 2,
                'user': 'jenny'
            }
        },
        'other': {},
    }
    assert interpolate_environment_variables(volumes, 'volume') == expected


def test_interpolate_missing(variable_mapping):
    assert interpolate("This ${missing} var", variable_mapping) == "This  var"


def test_interpolate_with_value(variable_mapping):
    assert interpolate("This $FOO var", variable_mapping) == "This first var"
    assert interpolate("This ${FOO} var", variable_mapping) == "This first var"


def test_interpolate_param_substition_missing_none_or_empty(variable_mapping):
    # see: http://tldp.org/LDP/abs/html/parameter-substitution.html
    # ${parameter-default}, ${parameter:-default}
    assert interpolate("ok ${missing:-def}", variable_mapping) == "ok def"
    assert interpolate("ok ${EMPTY:-def}", variable_mapping) == "ok def"


def test_interpolate_param_substition_missing_only(variable_mapping):
    # see: http://tldp.org/LDP/abs/html/parameter-substitution.html
    # ${parameter-default}, ${parameter:-default}
    assert interpolate("ok ${missing-def}", variable_mapping) == "ok def"
    assert interpolate("ok ${EMPTY-def}", variable_mapping) == "ok "
