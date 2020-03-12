import os

import boto3
from bk_ssm_secrets.shared import url_parser
from bk_ssm_secrets.shared import config

def env_is_true(env_var):
    if env_var in os.environ:
        if os.environ[env_var] == "1" or os.environ[env_var].lower() == "true":
            return True
        else:
            return False
    else:
        return False

def verbose():
    return env_is_true('BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_VERBOSE')

def extract_ssh_agent_envars(agent_output):
    '''
    Parse the output from ssh-agent to get only the variables and values

    Sample output:
    SSH_AUTH_SOCK=/tmp/ssh-KgoPdeGP2LPZ/agent.24789; export SSH_AUTH_SOCK;
    SSH_AGENT_PID=24790; export SSH_AGENT_PID;
    echo Agent pid 24790;
    '''

    agent_env_vars = {}
    if verbose():
        print("agent_output:", agent_output)
    output = agent_output.replace('\n', '').split(';')

    for line in output:
        key_val_pair = line.split('=')
        if len(key_val_pair) == 2:
            agent_env_vars[key_val_pair[0]] = key_val_pair[1]
            os.environ[key_val_pair[0]]  = key_val_pair[1]

    return agent_env_vars

def dump_env_secrets(env_before):
    if env_is_true('BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DUMP_ENV'):
        env_now = os.environ

        # Get difference in sets
        diff = set(env_now).difference(env_before)

        for key in diff:
            value = "'" + os.environ[key] + "'"
            print("export ", key, "=", value, sep='')
