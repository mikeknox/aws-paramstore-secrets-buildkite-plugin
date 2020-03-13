import os
from urllib.parse import urlparse


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
SECRETS_SLUG = secrets_slug()


def base_path():
    return BASE_PATH


def default_slug():
    return DEFAULT_SLUG


def secret_types():
    return SECRET_TYPES


def secrets_slug():
    slug = ""
    primary = "BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_KEY"
    secondary = "BUILDKITE_PIPELINE_SLUG"
    if primary in os.environ:
        key = os.environ[primary]
        slug = os.environ[key]
    else:
        slug = os.environ.get(secondary, "")

    if slug == "":
        msg = f"either {primary} or {secondary} must be set in envvar."
        raise ValueError(msg)

    parsed = urlparse(slug)
    if parsed.scheme == "":
        raise ValueError(f"Invalid URL scheme found: {slug}")

    key = f"{parsed.hostname}"
    if parsed.port:
        key += f":{parsed.port}"
    if parsed.path:
        key += "_" + parsed.path.strip("/").replace("/", "_").replace("~", "_")
    return key
