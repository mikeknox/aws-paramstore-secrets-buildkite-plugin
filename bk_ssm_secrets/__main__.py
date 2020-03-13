import os

from . import config
from .bksecrets import BkSecrets

def main():
    ssm_base_path = config.BASE_PATH
    secrets_path = [config.DEFAULT_SLUG]

    bksecret_store = BkSecrets()
    if config.SECRETS_SLUG:
        secrets_path.append(config.SECRETS_SLUG)

    if config.VERBOSE:
        print(f"~~~ Downloading secrets from :aws: paramstore: {config.BASE_PATH}")

    env_before = os.environ.copy()  # In Python dict assingments are references

    for path_node in secrets_path:
        if config.VERBOSE:
            print("Checking paramstore secrets in:", path_node)
        bksecret_store.get_secrets(path_node)

    config.dump_env_secrets(env_before)


if __name__ == '__main__':
    main()