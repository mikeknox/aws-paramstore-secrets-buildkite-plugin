import contextlib
import copy
import io
import logging
import os
import unittest
import unittest.mock

from ..bksecrets import BkSecrets
from ..config import DEFAULT_SLUG


class TestBKSecrets(unittest.TestCase):
    def setUp(self):
        self.os_environ = copy.copy(os.environ)
        self.patcher = unittest.mock.patch(
            "bk_ssm_secrets.ssm_parameter_store.SSMParameterStore", spec=True,
        )
        self.patcher.start()
        self.bksecrets = BkSecrets("slug")
        self.bksecrets.store = {}

        # setup capture logging streams.
        self.logger = logging.getLogger()
        self.stream = io.StringIO()
        self.handler = logging.StreamHandler(self.stream)

        self.orig_handler = self.logger.handlers[0]
        self.orig_handler.close()
        self.logger.removeHandler(self.logger.handlers[0])

        # add handler to logger
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.patcher.stop()
        os.environ = self.os_environ
        self.stream.close()
        self.logger.removeHandler(self.handler)
        self.logger.addHandler(self.orig_handler)
        del self.bksecrets

    def test_check_team_allowed_empty_ssm(self):
        self.bksecrets.store = {}
        with unittest.mock.patch(
            "bk_ssm_secrets.helpers.get_buildkite_teams",
            return_value={'team1', 'team2'},
        ):
            self.bksecrets.check_team_allowed()

    def test_check_team_allowed(self):
        self.bksecrets.store = {"allowed_teams": "team1"}
        with unittest.mock.patch(
            "bk_ssm_secrets.helpers.get_buildkite_teams",
            return_value={'team1', 'team2'},
        ):
            self.bksecrets.check_team_allowed()

    def test_check_team_not_allowed(self):
        self.bksecrets.store = {"allowed_teams": "team3"}
        with unittest.mock.patch(
            "bk_ssm_secrets.helpers.get_buildkite_teams",
            return_value={'team1', 'team2'},
        ):
            with self.assertRaises(RuntimeError) as context:
                self.bksecrets.check_team_allowed()
            self.assertEqual(
                "Your team does not have access to this namespace.",
                str(context.exception)
            )

    def test_check_team_scheduled_allowed(self):
        os.environ = {
            'BUILDKITE_SOURCE': 'schedule'
        }
        self.bksecrets.store = {"allowed_teams": "team1"}
        with unittest.mock.patch(
            "bk_ssm_secrets.helpers.get_buildkite_teams",
            return_value=set(),
        ):
            self.bksecrets.check_team_allowed()

    def test_check_team_scheduled_not_allowed_for_teams(self):
        """
        Buildkite might not possibly pass this in, but it is a case for
        completeness sake.
        """
        os.environ = {
            'BUILDKITE_SOURCE': 'schedule'
        }
        self.bksecrets.store = {"allowed_teams": "team1"}
        with unittest.mock.patch(
            "bk_ssm_secrets.helpers.get_buildkite_teams",
            return_value={"team2", "team3"},
        ):
            with self.assertRaises(RuntimeError) as context:
                self.bksecrets.check_team_allowed()
            self.assertEqual(
                "Your team does not have access to this namespace.",
                str(context.exception)
            )

    def test_check_pipeline_allowed(self):
        self.bksecrets.store = {"allowed_pipelines": "foo"}
        os.environ = {
            'BUILDKITE_PIPELINE_SLUG': 'foo',
        }
        self.bksecrets.check_pipeline_allowed()

    def test_check_pipeline_not_allowed(self):
        self.bksecrets.store = {"allowed_pipelines": "foo"}
        os.environ = {'BUILDKITE_PIPELINE_SLUG': 'bar'}
        with self.assertRaises(RuntimeError) as context:
            self.bksecrets.check_pipeline_allowed()
        self.assertEqual(
            "Your pipeline does not have access to this namespace.",
            str(context.exception)
        )

    def test_parse_env_null_case(self):
        os.environ = {}
        self.bksecrets.parse_env()
        self.assertEqual(os.environ, {})

    def test_parse_env_single_env_case(self):
        os.environ = {}
        self.bksecrets.store = {"env": {"A": "a"}}

        self.bksecrets.parse_env()
        self.assertEqual(os.environ, {'A': 'a'})

    def test_parse_env_multiple_env_case(self):
        os.environ = {}
        self.bksecrets.store = {"env": {"A": "a", "B": "b"}}

        self.bksecrets.parse_env()
        self.assertEqual(os.environ, {'A': 'a', "B": "b"})

    def test_parse_ssh_ignore_pipeline_ssh(self):
        os.environ = {'BUILDKITE_PIPELINE_SLUG': 'slug'}
        self.bksecrets.store = {"ssh": {"key": "text"}}
        self.bksecrets.parse_ssh()
        self.assertEqual(
            self.stream.getvalue().strip(), "Ignore pipeline level ssh keys."
        )

    def test_parse_ssh_ignore_default_key(self):
        os.environ = {'BUILDKITE_PIPELINE_SLUG': "foo"}

        self.bksecrets.slug = DEFAULT_SLUG
        self.bksecrets.store = {"ssh": {"key": "text"}}
        self.bksecrets.parse_ssh()
        self.assertEqual(
            self.stream.getvalue().strip(), "Ignore default ssh keys."
        )

    def test_parse_ssh_no_ssh(self):
        os.environ = {'BUILDKITE_PIPELINE_SLUG': "foo"}

        self.bksecrets.store = {"not-ssh": {"key": "text"}}
        self.logger.setLevel(logging.DEBUG)
        self.bksecrets.parse_ssh()
        expected = "\n".join([
            "Looking for ssh key: `/vendors/buildkite/secrets/slug/ssh/key`.",
            "No ssh key defined for /vendors/buildkite/secrets/slug."
        ])
        self.assertEqual(
            self.stream.getvalue().strip(), expected
        )

    def test_parse_ssh_no_key(self):
        os.environ = {'BUILDKITE_PIPELINE_SLUG': "foo"}

        self.bksecrets.store = {"ssh": {"not-key": "text"}}
        current_level = self.logger.getEffectiveLevel()
        self.logger.setLevel(logging.DEBUG)
        self.bksecrets.parse_ssh()
        expected = "\n".join([
            "Looking for ssh key: `/vendors/buildkite/secrets/slug/ssh/key`.",
            "No ssh key defined for /vendors/buildkite/secrets/slug."
        ])
        self.assertEqual(
            self.stream.getvalue().strip(), expected
        )
        self.logger.setLevel(current_level)

    def test_parse_ssh(self):
        os.environ = {'BUILDKITE_PIPELINE_SLUG': "foo"}
        self.bksecrets.store = {"ssh": {"key": "text"}}
        with unittest.mock.patch(
            "bk_ssm_secrets.helpers.start_ssh_agent",
            return_value={"SSH_AGENT_PID": "pid", "SSH_AUTH_SOCK": "sock"},
        ):
            buffer = io.StringIO()
            with contextlib.redirect_stderr(buffer):
                self.bksecrets.parse_ssh()

        self.assertEqual(
            buffer.getvalue().strip(),
            "Added key `/vendors/buildkite/secrets/slug/ssh/key` to ssh agent.",
        )

        self.assertEqual(
            os.environ,
            {
                'BUILDKITE_PIPELINE_SLUG': "foo",
                'AWS_PARAMSTORE_SECRETS_AGENT_PID': 'pid',
                'AWS_PARAMSTORE_SECRETS_AUTH_SOCK': 'sock'
            }
        )