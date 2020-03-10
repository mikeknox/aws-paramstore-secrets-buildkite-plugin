import os
from . import url_parser

def check_aws_env():
    # AWS_REGION
    #
    aws_region = ''
    if 'AWS_REGION' in os.environ:
        aws_region = os.environ['AWS_REGION']
    if 'AWS_DEFAULT_REGION' in os.environ:
        aws_region = os.environ['AWS_DEFAULT_REGION']
    return aws_region

def base_path():
    if 'BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH' in os.environ:
        ssm_base_path = os.environ['BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH']
    else:
        ssm_base_path = '/vendors/buildkite/secrets'

    return ssm_base_path

def default_slug():
    if 'BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DEFAULT_KEY' in os.environ:
        ssm_default_key = os.environ['BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DEFAULT_KEY']
    else:
        ssm_default_key = 'global'
    return ssm_default_key

def secrets_slug():
    key_value = ''
    if 'BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_KEY' in os.environ:
        key = os.environ['BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_KEY']
        key_value = os.environ[key]
    elif 'BUILDKITE_PIPELINE_SLUG' in os.environ:
        key_value = os.environ['BUILDKITE_PIPELINE_SLUG']

    if key_value and url_parser.valid_url(key_value):
        key_value = url_parser.url_to_key(key_value)
    return key_value