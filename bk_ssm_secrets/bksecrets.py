import os
import logging

from . import config, helpers, ssm_parameter_store


helpers.setup_logging()


class BkSecrets(object):
    def __init__(self, path):
        self.slug = path
        self.base = f"{config.BASE_PATH}/{path}"
        logging.debug(f"Reading items from {self.base}.")
        self.store = ssm_parameter_store.SSMParameterStore(prefix=self.base)

    def parse_env(self):
        self.check_acls()
        if 'env' not in self.store:
            return
        for key in self.store['env']:
            value = self.store['env'][key]
            key_name = helpers.key_to_env_name(key)
            logging.debug(
                f"current env: {key_name} is `{os.environ.get('key_name', '')}`"
            )
            logging.debug(f"set env: {key_name} to `{value}`")
            os.environ[key_name] = value

    def parse_ssh(self):
        if self.slug == os.environ["BUILDKITE_PIPELINE_SLUG"]:
            logging.debug("Ignore pipeline level ssh keys.")
            return

        if self.slug == config.DEFAULT_SLUG:
            logging.debug("Ignore default ssh keys.")
            return

        self.check_acls()
        logging.debug(f"Looking for ssh key: `{self.base}/ssh/key`.")
        if 'ssh' not in self.store or 'key' not in self.store['ssh']:
            logging.debug(f"No ssh key defined for {self.base}.")
            return

        logging.debug(
            f"Starting an ephemeral ssh-agent for `{self.base}/ssh/key`"
        )
        envvars = helpers.start_ssh_agent(self.store['ssh']['key'])
        print(f"Added key `{self.base}/ssh/key` to ssh agent.")

        os.environ.update({
            "AWS_PARAMSTORE_SECRETS_AGENT_PID": envvars["SSH_AGENT_PID"],
            "AWS_PARAMSTORE_SECRETS_AUTH_SOCK": envvars["SSH_AUTH_SOCK"],
        })

    def check_pipeline_allowed(self):
        if 'allowed_pipelines' in self.store:
            logging.debug(f"Reading allowed pipelines")
            current_pipeline = os.environ['BUILDKITE_PIPELINE_SLUG']
            allowed = self.store['allowed_pipelines'].split('\n')
            if current_pipeline not in allowed:
                logging.error(
                    f"current pipeline: {current_pipeline}. allowed:, {allowed}"
                )
                raise RuntimeError(
                    "Your pipeline does not have access to this namespace."
                )
            logging.debug(f"Passing allowed pipelines")

    def check_team_allowed(self):
        if 'allowed_teams' in self.store:
            logging.debug(f"Reading allowed teams")
            current_teams = os.environ.get(
                "BUILDKITE_BUILD_CREATOR_TEAMS", ""
            ).split(":")
            allowed_teams = self.store['allowed_teams'].split('\n')
            if len(set(current_teams) & set(allowed_teams)) == 0:
                logging.error(
                    f"current teams: {current_teams}. allowed:, {allowed_teams}"
                )
                raise RuntimeError(
                    "Your team does not have access to this namespace."
                )
            logging.debug(f"Passing allowed teams")

    def check_acls(self):
        self.check_pipeline_allowed()
        self.check_team_allowed()