import os


BASE_PATH = os.environ.get(
    "BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH", "/vendors/buildkite/secrets"
)
DEFAULT_SLUG = os.environ.get(
    "BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DEFAULT_KEY", "global"
)
# Return an list of the secret types that we can retrieve.
# This is derived from env var BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_TYPES.
# which is a colon delimited list.
SECRET_TYPES = os.environ.get(
    "BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_TYPES", "env:ssh:git-creds"
).split(":")
MODE = os.environ.get("BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_MODE", "pipeline")
