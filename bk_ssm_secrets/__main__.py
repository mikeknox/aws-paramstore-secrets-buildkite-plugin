import os
from . import shared
from . import bksecrets

ssm_base_path = shared.config.base_path()
ssm_default_key = shared.config.default_slug()

key_value = shared.config.secrets_slug()

secrets_path = [ssm_default_key]

# import code
# code.interact(local=locals())

bksecret_store = bksecrets.bksecrets.BkSecrets(base_path=ssm_base_path)
if key_value:
    secrets_path.append(key_value)

if shared.shared.verbose():
    print("~~~ Downloading secrets from :aws: paramstore:", ssm_base_path)
env_before = os.environ.copy()    # In Python dict assingments are references

# import code
# code.interact(local=locals())

for path_node in secrets_path:
    if shared.shared.verbose():
        print("Checking paramstore secrets in:", path_node)
    bksecret_store.get_secrets(path_node)
shared.shared.dump_env_secrets(env_before)    

# import code
# code.interact(local=locals())