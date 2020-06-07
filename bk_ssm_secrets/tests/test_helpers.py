import contextlib
import copy
import io
import os
import types
import unittest

from ..helpers import (
    dump_env_secrets,
    extract_ssh_agent_envars,
    get_buildkite_teams,
    key_to_env_name,
    start_ssh_agent,
    url_to_slug,
)

# Fixture used by several tests.
SSH_AGENT_OUTPUT = \
b"""SSH_AUTH_SOCK=/tmp/ssh-KgoPdeGP2LPZ/agent.24789; export SSH_AUTH_SOCK;
SSH_AGENT_PID=24790; export SSH_AGENT_PID;
echo Agent pid 24790;"""


class TestURLToSlug(unittest.TestCase):
    CASES = {
        "https://github.com/a/b.git": "github.com_a_b.git",
        "git@github.com:a/b.git": "github.com_a_b.git",
        "user@github.com:a/b.git": "github.com_a_b.git",
        "https://git@github.com/a/b.git": "github.com_a_b.git",
        "ssh://git@github.com/a/b.git": "github.com_a_b.git",
        "ssh://git@github.com:22/a/b.git": "github.com-22_a_b.git",
        "https://github.com:8080/a/b.git": "github.com-8080_a_b.git",
        "https://github.com:8080/~a/b.git": "github.com-8080__a_b.git",
    }
    def test_url_to_slug_cases(self):
        for case in self.CASES:
            expected = self.CASES[case]
            self.assertEqual(url_to_slug(case), expected)


class TestGetBuildkiteTeams(unittest.TestCase):
    def setUp(self):
        self.os_environ = copy.copy(os.environ)

    def tearDown(self):
        os.environ = self.os_environ

    def test_no_env_teams(self):
        os.environ = {}
        self.assertEqual(get_buildkite_teams(), set())

    def test_creator_teams(self):
        os.environ = {"BUILDKITE_BUILD_CREATOR_TEAMS": "team1:team2"}
        self.assertEqual(get_buildkite_teams(), {"team1", "team2"})

    def test_unblocker_teams(self):
        os.environ = {"BUILDKITE_UNBLOCKER_TEAMS": "team3:team4"}
        self.assertEqual(get_buildkite_teams(), {"team3", "team4"})

    def test_creator_and_unblocker_teams(self):
        os.environ = {
            "BUILDKITE_UNBLOCKER_TEAMS": "team3:team4",
            "BUILDKITE_BUILD_CREATOR_TEAMS": "team1:team2",
        }
        self.assertEqual(
            get_buildkite_teams(), {"team1", "team2", "team3", "team4"}
        )

    def test_creator_and_unblocker_same_teams(self):
        os.environ = {
            "BUILDKITE_UNBLOCKER_TEAMS": "team1:team4",
            "BUILDKITE_BUILD_CREATOR_TEAMS": "team1:team2",
        }
        self.assertEqual(get_buildkite_teams(), {"team1", "team2", "team4"})

    def test_empty_teams(self):
        os.environ = {
            "BUILDKITE_UNBLOCKER_TEAMS": "",
            "BUILDKITE_BUILD_CREATOR_TEAMS": "",
        }
        self.assertEqual(get_buildkite_teams(), set())


class TestKeyToEnvName(unittest.TestCase):
    CASES = {
        "access-token": "ACCESS_TOKEN",
        "ACCESS-TOKEN": "ACCESS_TOKEN",
        "ACCESS_TOKEN": "ACCESS_TOKEN",
    }
    def test_key_to_env_name_cases(self):
        for case in self.CASES:
            expected = self.CASES[case]
            self.assertEqual(key_to_env_name(case), expected)


class TestExtractSSHAgentEnvars(unittest.TestCase):
    def test_flow(self):
        expected = {
            'SSH_AGENT_PID': '24790',
            'SSH_AUTH_SOCK': '/tmp/ssh-KgoPdeGP2LPZ/agent.24789'
        }
        self.assertEqual(extract_ssh_agent_envars(SSH_AGENT_OUTPUT), expected)


class TestDumpEnvSecrets(unittest.TestCase):
    def setUp(self):
        self.os_environ = copy.copy(os.environ)

    def tearDown(self):
        os.environ = self.os_environ

    def test_new_value(self):
        os.environ = {
            "A": "B",
        }
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            dump_env_secrets({})

        self.assertEqual(buffer.getvalue().strip(), "export A=B")

    def test_changed_value(self):
        os.environ = {
            "A": "C",
        }
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            dump_env_secrets({"A": "B"})

        self.assertEqual(buffer.getvalue().strip(), "export A=C")

    def test_mixed_value(self):
        os.environ = {
            "A": "C",
            "D": "E",
        }
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            dump_env_secrets({"A": "B"})

        self.assertEqual(buffer.getvalue().strip(), "export A=C\nexport D=E")


class TestStartSSHAgent(unittest.TestCase):
    def setUp(self):
        self.os_environ = copy.copy(os.environ)

    def tearDown(self):
        os.environ = self.os_environ

    def test_flow(self):
        os.environ = {}
        def _run(args, **kwargs):
            return types.SimpleNamespace(
                stdout=SSH_AGENT_OUTPUT, returncode=0
            )

        with unittest.mock.patch("subprocess.run", new=_run):
            envvars = start_ssh_agent("text")

            self.assertEqual(
                envvars,
                {
                    'SSH_AGENT_PID': '24790',
                    'SSH_ASKPASS': '/bin/false',
                    'SSH_AUTH_SOCK': '/tmp/ssh-KgoPdeGP2LPZ/agent.24789'
                }
            )

    def test_ssh_agent_failed(self):
        def _run(args, **kwargs):
            process = types.SimpleNamespace(
                stdout=SSH_AGENT_OUTPUT, stderr="",
            )
            if args[0] == "ssh-agent":
                process.returncode = 1
            else:
                process.returncode = 0
            return process

        with unittest.mock.patch("subprocess.run", new=_run):
            with self.assertRaises(RuntimeError) as context:
                start_ssh_agent("text")
            self.assertEqual("starting ssh agent failed.", str(context.exception))

    def test_ssh_add_failed(self):
        def _run(args, **kwargs):
            process = types.SimpleNamespace(
                stdout=SSH_AGENT_OUTPUT, stderr="",
            )
            if args[0] == "ssh-agent":
                process.returncode = 0
            else:
                process.returncode = 1
            return process

        with unittest.mock.patch("subprocess.run", new=_run):
            with self.assertRaises(RuntimeError) as context:
                start_ssh_agent("text")
            self.assertEqual("ssh-add failed.", str(context.exception))
