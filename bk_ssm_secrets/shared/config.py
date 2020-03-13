import os

from bk_ssm_secrets.shared import url_parser


BASE_PATH = os.environ.get(
    "BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH", "/vendors/buildkite/secrets"
)
DEFAULT_SLUG = os.environ.get(
    "BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DEFAULT_KEY", "global"
)
SECRET_TYPES = os.environ.get(
    "BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_TYPES", "env:ssh:git-creds"
).split(":")


def base_path():
    return BASE_PATH


def default_slug():
    return DEFAULT_SLUG


def secret_types():
    """
    Return an array of the secret types that we can retrieve.
    This is derived from the env var BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_TYPES.
    This is a colon delimited list.
    """
    return SECRET_TYPES


def secrets_slug():
    key_value = ""
    if "BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_KEY" in os.environ:
        key = os.environ["BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_KEY"]
        key_value = os.environ[key]
    elif "BUILDKITE_PIPELINE_SLUG" in os.environ:
        key_value = os.environ["BUILDKITE_PIPELINE_SLUG"]

    if key_value and url_parser.valid_url(key_value):
        key_value = url_parser.url_to_key(key_value)
    return key_value
