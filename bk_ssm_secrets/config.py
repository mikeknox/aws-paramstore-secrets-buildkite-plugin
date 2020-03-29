import os


BASE_PATH = os.environ.get(
    "AWS_PARAMSTORE_SECRETS_PATH", "/vendors/buildkite/secrets"
)
DEFAULT_SLUG = os.environ.get(
    "AWS_PARAMSTORE_SECRETS_DEFAULT_KEY", "global"
)
VERBOSE = os.environ.get("AWS_PARAMSTORE_SECRETS_VERBOSE") == "1"
