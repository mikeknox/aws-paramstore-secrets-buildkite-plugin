import os
import logging

from . import config, helpers
from .bksecrets import BkSecrets


helpers.setup_logging()


def main():
    ssm_base_path = config.BASE_PATH
    secrets_path = [config.DEFAULT_SLUG]

    bksecret_store = BkSecrets()
    logging.debug(f"Running in {config.MODE} mode.")
    if config.MODE == "repo":
        secrets_path.append(helpers.url_to_slug(os.environ["BUILDKITE_REPO"]))
    else:
        secrets_path.append(os.environ["BUILDKITE_PIPELINE_SLUG"])

    logging.debug(
        f"Downloading secrets from paramstore: {config.BASE_PATH}"
    )

    env_before = os.environ.copy()  # In Python dict assingments are references

    for path_node in secrets_path:
        logging.debug(f"Checking paramstore secrets in: {path_node}")
        bksecret_store.get_secrets(path_node)

    helpers.dump_env_secrets(env_before)


if __name__ == '__main__':
    main()