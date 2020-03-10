import os

import boto3
from . import url_parser
from . import config

def env_is_true(env_var):
    if env_var in os.environ:
        if os.environ[env_var] == "1" or os.environ[env_var].lower() == "true":
            return True
        else:
            return False
    else:
        return False

def dump_env_secrets(env_before):
    if env_is_true('BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DUMP_ENV'):
        env_now = os.environ

        # Get difference in sets
        diff = set(env_now).difference(env_before)

        for key in diff:
            value = "'" + os.environ[key] + "'"
            print(key, value, sep='=')
