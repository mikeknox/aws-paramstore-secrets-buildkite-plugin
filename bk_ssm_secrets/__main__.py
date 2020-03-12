import os

from .shared import config, shared
from .bksecrets.bksecrets import BkSecrets

def main():
    ssm_base_path = config.base_path()
    ssm_default_key = config.default_slug()

    key_value = config.secrets_slug()

    secrets_path = [ssm_default_key]

    bksecret_store = BkSecrets(base_path=ssm_base_path)
    if key_value:
        secrets_path.append(key_value)

    if shared.verbose():
        print("~~~ Downloading secrets from :aws: paramstore:", ssm_base_path)
    env_before = os.environ.copy()    # In Python dict assingments are references

    for path_node in secrets_path:
        if shared.verbose():
            print("Checking paramstore secrets in:", path_node)
        bksecret_store.get_secrets(path_node)
    shared.dump_env_secrets(env_before)

if __name__ == '__main__':
    main()