import os
import logging

from . import config
from .bksecrets import BkSecrets


config.setup_logging()


def main():
    ssm_base_path = config.BASE_PATH
    secrets_path = [config.DEFAULT_SLUG]

    bksecret_store = BkSecrets()
    if config.SECRETS_SLUG:
        secrets_path.append(config.SECRETS_SLUG)

    logging.debug(
        f"Downloading secrets from paramstore: {config.BASE_PATH}"
    )

    env_before = os.environ.copy()  # In Python dict assingments are references

    for path_node in secrets_path:
        logging.debug(f"Checking paramstore secrets in: {path_node}")
        bksecret_store.get_secrets(path_node)

    config.dump_env_secrets(env_before)


if __name__ == '__main__':
    main()