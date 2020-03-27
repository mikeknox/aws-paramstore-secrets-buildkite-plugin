import os
import logging
import sys
import subprocess

import boto3
from . import config, helpers, ssm_parameter_store


helpers.setup_logging()


class BkSecrets(object):
    def __init__(self):
        self.store = ssm_parameter_store.SSMParameterStore(
            prefix=config.BASE_PATH
        )

    def get_secrets(self, slug):
        logging.debug(f"In get_secrets: {slug}")
        if slug in self.store:
            self.check_acls(slug)
            keys = self.store[slug].keys()

            allowed_types = set(keys) & set(config.SECRET_TYPES)
            logging.debug(f"Allowed types: {allowed_types}")

            for type_ in allowed_types:
                for key in self.store[slug][type_].keys():
                    processor = getattr(
                        self, f"process_{type_.replace('-', '_')}_secret"
                    )
                    processor(slug, key)

    def process_env_secret(self, slug, key):
        value = self.store[slug]['env'][key]
        logging.debug(f"current env: {key} is `{os.environ.get('key', '')}`")
        logging.debug(f"set env: {key} to `{value}`")
        os.environ[key] = value

    def process_ssh_secret(self, slug, key):
        ssh_key = self.store[slug]['ssh'][key]

        # Need to check whether another SSH agent with the same key exists.
        default_key = os.environ[
            'BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DEFAULT_KEY'
        ]
        secrets_mode = os.environ["BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_MODE"]
        if slug == default_key and secrets_mode == "pipeline":
            logging.debug("Skip adding global ssh key again.")
            return

        logging.debug("Starting an ephemeral ssh-agent")

        ssh_agent = subprocess.run(
            ['ssh-agent', '-s'], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if ssh_agent.returncode != 0:
            logging.debug(f"ssh-agent process stdout: {ssh_agent.stdout}")
            logging.debug(f"ssh-agent process stderr: {ssh_agent.stderr}")
            raise RuntimeError("starting ssh agent failed.")

        ssh_env = helpers.extract_ssh_agent_envars(ssh_agent.stdout)

        logging.debug(
            f"Started new ssh-agent (pid {ssh_env['SSH_AGENT_PID']})"
        )

        envvars = os.environ.copy()
        envvars.update(ssh_env)
        envvars['SSH_ASKPASS'] = '/bin/false'
        ssh_add = subprocess.run(
            ['ssh-add', '-'], input=ssh_key+'\n', env=envvars,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8',
        )

        if ssh_add.returncode != 0:
            logging.error(f"ssh-add process stdout: {ssh_add.stdout.decode()}")
            logging.error(f"ssh-add process stderr: {ssh_add.stderr.decode()}")
            raise RuntimeError("ssh-add failed.")
        print(f"Added {slug}/{key} to ssh agent .", file=sys.stderr)

        if key == "repo":
            prefix = "BK_SSM_SSH_AGENT_REPO"
        else:
            prefix = "BK_SSM_SSH_AGENT_PROJECT"

        os.environ[f"{prefix}_AGENT_PID"] = envvars["SSH_AGENT_PID"]
        os.environ[f"{prefix}_AUTH_SOCK"] = envvars["SSH_AUTH_SOCK"]


    def process_gitcred_secret(self, slug, key):
        # FIXME: not implemented yet
        logging.debug("slug:", slug, "key:", key)
        logging.debug("Adding git-credentials in $path as a credential helper", file=sys.stderr)

    def check_pipeline_acl(self, slug=None):
        if slug in self.store and 'allowed_pipelines' in self.store[slug]:
            current_slug = os.environ['BUILDKITE_PIPELINE_SLUG']
            allowed = self.store[slug]['allowed_pipelines'].split('\n')
            if current_slug not in allowed:
                logging.debug(f"current: {current_slug}. allowed:, {allowed}")
                raise RuntimeError(
                    "Your pipeline does not have access to this value."
                )

    def check_team_allowed(self, slug=None):
        if slug in self.store and 'allowed_teams' in self.store[slug]:
            current_teams = os.environ.get(
                "BUILDKITE_BUILD_CREATOR_TEAMS", ""
            ).split(":")
            allowed_teams = self.store[slug]['allowed_teams'].split('\n')
            if not (set(current_teams) & set(allowed_teams)):
                logging.debug(f"current: {current_teams}. allowed:, {allowed_teams}")
                raise RuntimeError(
                    "Your pipeline does not have access to this value."
                )

    def check_acls(self, slug=None):
        self.check_pipeline_acl(slug)
        self.check_team_allowed(slug)