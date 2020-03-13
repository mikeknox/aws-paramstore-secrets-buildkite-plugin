# import pytest, os
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
import os
from bk_ssm_secrets.shared import config

# from ./environment.py # import *
# from environment import base_path
# import hooks/environment
# from urllib.parse import urlparse
# from shared import shared


class TestConfigMethods(unittest.TestCase):
    def check_aws_env(self):
        with patch.dict(os.environ, {'AWS_REGION': 'e-boo-1'}, clear=True):
            assert(config.check_aws_env() == 'e-boo-1')

        with patch.dict(os.environ, {'AWS_DEFAULT_REGION': 'e-boo-2'}, clear=True):
            assert(config.check_aws_env() == 'e-boo-2')
        
        with patch.dict(os.environ, {'AWS_REGION': 'e-boo-1'}, clear=True):
            with patch.dict(os.environ, {'AWS_DEFAULT_REGION': 'e-boo-2'}, clear=True):
                assert(config.check_aws_env() == 'e-boo-1')

        # assert(config.base_path() == '/vendors/buildkite/secrets')
        # TODO: expect error if envs not defined

    def test_base_path(self):
        with patch.dict(os.environ, {'BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH': '/tmp/abc'}, clear=True):
            assert(config.base_path() == '/tmp/abc')

        assert(config.base_path() == '/vendors/buildkite/secrets')

    def test_default_slug(self):
        with patch.dict(os.environ, {'BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DEFAULT_KEY': 'boohiss'}, clear=True):
            assert(config.default_slug() == 'boohiss')

        assert(config.default_slug() == 'global')

    def test_secrets_slug(self):
        print("secrets_slug()")
        with patch.dict(os.environ, {'BUILDKITE_PIPELINE_SLUG': 'zip'}, clear=True):
            assert(config.secrets_slug() == 'zip')

        print("test substution")

        with patch.dict(os.environ, {
            'BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_KEY': 'zip',
            'zip': 'zap'}, clear=True):
            assert(config.secrets_slug() == 'zap')

        # TODO: add test for key val = URL
        assert(config.secrets_slug() == '')

if __name__ == '__main__':
    unittest.main()