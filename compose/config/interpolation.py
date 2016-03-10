from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import os
from string import Template

import six

from .errors import ConfigurationError
log = logging.getLogger(__name__)


def interpolate_environment_variables(config, section):
    mapping = BlankDefaultDict(os.environ)

    def process_item(name, config_dict):
        return dict(
            (key, interpolate_value(name, key, val, section, mapping))
            for key, val in (config_dict or {}).items()
        )

    return dict(
        (name, process_item(name, config_dict or {}))
        for name, config_dict in config.items()
    )


def interpolate_value(name, config_key, value, section, mapping):
    try:
        return recursive_interpolate(value, mapping)
    except InvalidInterpolation as e:
        raise ConfigurationError(
            'Invalid interpolation format for "{config_key}" option '
            'in {section} "{name}": "{string}"'.format(
                config_key=config_key,
                name=name,
                section=section,
                string=e.string))


def recursive_interpolate(obj, mapping):
    if isinstance(obj, six.string_types):
        return interpolate(obj, mapping)
    elif isinstance(obj, dict):
        return dict(
            (key, recursive_interpolate(val, mapping))
            for (key, val) in obj.items()
        )
    elif isinstance(obj, list):
        return [recursive_interpolate(val, mapping) for val in obj]
    else:
        return obj


class TemplateWithDefaults(Template):
    idpattern = r'[_a-z][_a-z0-9]*(?::-[_a-z0-9]+)?'

    # Modified from python2.7/string.py
    def substitute(self, mapping):
        # Helper function for .sub()
        def convert(mo):
            # Check the most common path first.
            named = mo.group('named') or mo.group('braced')
            if named is not None:
                if ':-' in named:
                    var, _, default = named.partition(':-')
                    return mapping.get(var, default)
                val = mapping[named]
                return '%s' % (val,)
            if mo.group('escaped') is not None:
                return self.delimiter
            if mo.group('invalid') is not None:
                self._invalid(mo)
            raise ValueError('Unrecognized named group in pattern',
                             self.pattern)
        return self.pattern.sub(convert, self.template)


def interpolate(string, mapping):
    try:
        return TemplateWithDefaults(string).substitute(mapping)
    except ValueError:
        raise InvalidInterpolation(string)


class BlankDefaultDict(dict):
    def __init__(self, *args, **kwargs):
        super(BlankDefaultDict, self).__init__(*args, **kwargs)
        self.missing_keys = []

    def __getitem__(self, key):
        try:
            return super(BlankDefaultDict, self).__getitem__(key)
        except KeyError:
            if key not in self.missing_keys:
                log.warn(
                    "The {} variable is not set. Defaulting to a blank string."
                    .format(key)
                )
                self.missing_keys.append(key)

            return ""


class InvalidInterpolation(Exception):
    def __init__(self, string):
        self.string = string
