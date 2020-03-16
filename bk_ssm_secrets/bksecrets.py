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
        if slug in self.store and self.check_acls(slug):
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

        if not 'SSH_AGENT_PID' in os.environ:
            logging.debug("Starting an ephemeral ssh-agent")

            ssh_agent_process = subprocess.run(
                ['ssh-agent', '-s'], text=True, capture_output=True
            )
            if ssh_agent_process.returncode != 0:
                logging.debug(
                    f"ssh-agent process stdout: {ssh_agent_process.stdout}"
                )
                logging.debug(
                    f"ssh-agent process stderr: {ssh_agent_process.stderr}"
                )
                raise RuntimeError("starting ssh agent failed.")
            else:
                helpers.extract_ssh_agent_envars(ssh_agent_process.stdout)

        if 'SSH_AGENT_PID' in os.environ:
            logging.debug(
                f"Adding ssh-key into agent (pid {os.environ['SSH_AGENT_PID']})"
            )

            os.environ['SSH_ASKPASS'] = '/bin/false'
            ssh_add_process = subprocess.run(
                ['ssh-add', '-'], input=ssh_key+'\n',
                text=True, capture_output=True,
            )
            del os.environ['SSH_ASKPASS']
            if ssh_add_process.returncode != 0:
                logging.error(f"ssh-add process stdout: {ssh_add_process.stdout}")
                logging.error(f"ssh-add process stderr: {ssh_add_process.stderr}")
                raise RuntimeError("ssh-add failed.")
        else:
            raise RuntimeError("Starting")

    def process_gitcred_secret(self, slug, key):
        # FIXME: not implemented yet
        logging.debug("slug:", slug, "key:", key)
        logging.debug("Adding git-credentials in $path as a credential helper", file=sys.stderr)

    def check_pipeline_acl(self, slug=None):
        pipeline_allowed = True
        if slug in self.store.keys() and 'allowed_pipelines' in self.store[slug].keys():
            # if os.environ['BUILDKITE_PIPELINE_SLUG'] is in list allow
            pipeline_allowed = False
            if 'BUILDKITE_PIPELINE_SLUG' in os.environ and os.environ['BUILDKITE_PIPELINE_SLUG'] in self.store[slug]['allowed_pipelines'].split('\n'):
                pipeline_allowed = True

        return pipeline_allowed

    def check_team_allowed(self, slug=None):
        team_allowed = True # Allow access if ACL's are not set

        if slug in self.store.keys() and 'allowed_teams' in self.store[slug].keys():
            # Compare os.environ['BUILDKITE_TEAMS'] (colon delimited list) with team_list
            # if there is a common value, return true
            team_allowed = False

            # TODO:validate envVar
            if 'BUILDKITE_BUILD_CREATOR_TEAMS' in os.environ:
                current_teams = os.environ['BUILDKITE_BUILD_CREATOR_TEAMS'].split(':')

                if self.store[slug]['allowed_teams']:
                    allowed_teams = self.store[slug]['allowed_teams'].split('\n')
                    common_teams = set(allowed_teams).intersection(current_teams)
                    if len(common_teams) >= 1:
                        team_allowed = True

        return team_allowed

    def check_acls(self, slug=None):
        pipeline_allowed = self.check_pipeline_acl(slug)
        team_allowed = self.check_team_allowed(slug)

        return pipeline_allowed and team_allowed