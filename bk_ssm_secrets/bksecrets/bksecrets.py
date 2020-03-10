
from . import ssm_parameter_store
# from ssm_parameter_store import EC2ParameterStore
import boto3
from .. import shared
# from . import acls
import os

class BkSecrets(object):
    def __init__(self, ssm_client=None, base_path=None):
        self.ssm_client = ssm_client or self.get_ssm_client()
        self.store = ssm_parameter_store.SSMParameterStore(prefix=base_path, ssm_client=self.ssm_client)
        self.base_path = base_path

    def get_ssm_client(self):
        aws_region = shared.config.check_aws_env()
        return boto3.client('ssm', region_name=aws_region)

    def get_secrets(self, slug):
        if self.check_team_allowed(slug):
            keys = self.store[slug].keys()

            if 'env' in keys:
                for key in self.store[slug]['env'].keys():
                    self.process_env_secret(slug, key)
            if 'ssh' in keys:
                for key in self.store[slug]['ssh'].keys():
                    self.process_ssh_secret(slug, key)
            if 'git-creds' in keys:
                for key in self.store[slug]['git-creds'].keys():
                    self.process_gitcred_secret(slug, key)

    def process_env_secret(self, slug, key):
        os.environ[key] = self.store[slug]['env'][key]

    def process_ssh_secret(self, slug, key):
        print("key:", key)

    def process_gitcred_secret(self, slug, key):
        print("key:", key)

    def check_pipeline_acl(self, slug=None):
        pipeline_allowed = True
        print(self.store[slug].keys())
        if 'allowed_pipelines' in self.store[slug]:
            # if os.environ['BUILDKITE_PIPELINE_SLUG'] is in list allow
            pipeline_allowed = False
            if 'BUILDKITE_PIPELINE_SLUG' in os.environ and os.environ['BUILDKITE_PIPELINE_SLUG'] in self.store['allowed_pipelines']:
                pipeline_allowed = True

        return pipeline_allowed

    def check_team_allowed(self, slug=None):
        team_allowed = True # Allow access if ACL's are not set

        if 'allowed_teams' in self.store[slug]:
            # Compare os.environ['BUILDKITE_TEAMS'] (colon delimited list) with team_list
            # if there is a common value, return true
            team_allowed = False

            # TODO:validate envVar
            if 'BUILDKITE_TEAMS' in os.environ:
                current_teams = os.environ['BUILDKITE_TEAMS'].split(':')
            else:
                current_teams = 'No team has been defined'

            if self.store[slug]['allowed_teams']:
                allowed_teams = self.store[slug]['allowed_teams']
                common_teams = set(allowed_teams).intersection(current_teams)
                if len(common_teams) >= 1:
                    team_allowed = True

        return team_allowed

    def check_acls(self, slug=None):
        pipeline_allowed = self.check_pipeline_acl(slug)
        team_allowed = self.check_team_allowed(slug)

        return pipeline_allowed and team_allowed