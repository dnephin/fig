from __future__ import absolute_import
from __future__ import unicode_literals
import hashlib
import logging

from docker import errors
from docker.utils import version_lt
from pytest import skip

from .. import unittest
from compose.cli.docker_client import docker_client
from compose.config.config import process_service
from compose.config.config import resolve_environment
from compose.config.config import ServiceConfig
from compose.const import LABEL_PROJECT
from compose.progress_stream import stream_output
from compose.service import Service


log = logging.getLogger(__name__)


LABEL_TEST_IMAGE = 'com.docker.compose.test-image'


def pull_busybox(client):
    try:
        client.inspect_image('busybox:latest')
    except errors.APIError:
        client.pull('busybox:latest', stream=False)


class DockerClientTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = docker_client()

    def tearDown(self):
        project_label = '%s=%s' % (LABEL_PROJECT, self.project_name)
        for c in self.client.containers(
                all=True,
                filters={'label': project_label}):
            self.client.kill(c['Id'])
            self.client.remove_container(c['Id'])
        for i in self.client.images(
                filters={'label': LABEL_TEST_IMAGE}):
            try:
                self.client.remove_image(i)
            except Exception as e:
                log.warn("Failed to remove %s: %s" % (i, e))

    def create_service(self, name, **kwargs):
        if 'image' not in kwargs and 'build' not in kwargs:
            kwargs['image'] = 'busybox:latest'

        kwargs.setdefault('command', ["top"])

        service_config = ServiceConfig('.', None, name, kwargs)
        options = process_service(service_config)
        options['environment'] = resolve_environment('.', kwargs)

        labels = options.setdefault('labels', {})
        labels['com.docker.compose.test-name'] = self.id()

        return Service(
            name,
            project=self.project_name,
            client=self.client,
            **options)

    @property
    def project_name(self):
        hash = hashlib.new('md5')
        hash.update(self.id().encode('utf-8'))
        return 'ct' + hash.hexdigest()

    def check_build(self, *args, **kwargs):
        kwargs.setdefault('rm', True)
        build_output = self.client.build(*args, **kwargs)
        stream_output(build_output, open('/dev/null', 'w'))

    def require_api_version(self, minimum):
        api_version = self.client.version()['ApiVersion']
        if version_lt(api_version, minimum):
            skip("API version is too low ({} < {})".format(api_version, minimum))
