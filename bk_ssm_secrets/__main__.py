import os
import logging

from . import config, helpers
from .bksecrets import BkSecrets


helpers.setup_logging()


def main():
    stores = [
        BkSecrets(config.DEFAULT_SLUG),
        BkSecrets(helpers.url_to_slug(os.environ["BUILDKITE_REPO"])),
        BkSecrets(os.environ["BUILDKITE_PIPELINE_SLUG"]),
    ]

    env_before = os.environ.copy()  # In Python dict assingments are references

    for store in stores:
        store.parse_ssh()
        store.parse_env()

    helpers.dump_env_secrets(env_before)


if __name__ == '__main__':
    main()