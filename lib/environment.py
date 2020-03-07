#!/usr/bin/env python3

import sys, os
import boto3
from urllib.parse import urlparse
from ssm_parameter_store import SSMParameterStore
# from rfc3987 import parse
# https://code-examples.net/en/q/bfba6a
# def valid_url(url):
#     parse(url, rule='IRI')
# username = os.environ['USER']

def valid_url(url):
    parsed = urlparse(url)
    if parsed.scheme:
        return True
    else:
        return False

def url_to_key(url):
    parsed = urlparse(url)
    key=''
    if parsed.hostname:
        key+=parsed.hostname
    if parsed.port:
        key+='_'+str(parsed.port)
    if parsed.path:
        key+='_'+parsed.path.strip('/').replace('/','_')
    return key

def check_aws_env():
    # AWS_REGION
    #
    aws_region=''
    if 'AWS_REGION' in os.environ:
        aws_region=os.environ['AWS_REGION']
    if 'AWS_DEFAULT_REGION' in os.environ:
        aws_region=os.environ['AWS_DEFAULT_REGION']
    return aws_region

def base_path():
    if 'BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH' in os.environ:
        ssm_base_path=os.environ['BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH']
    else:
        ssm_base_path='/vendors/buildkite/secrets'

    return ssm_base_path

def default_slug():
    if 'BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DEFAULT_KEY' in os.environ:
        ssm_default_key=os.environ['BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DEFAULT_KEY']
    else:
        ssm_default_key='global'
    return ssm_default_key

def secrets_slug():
    key_value=''
    if 'BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_KEY' in os.environ:
        key_value=os.environ[os.environ['BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_KEY']]
    elif 'BUILDKITE_PIPELINE_SLUG' in os.environ:
        key_value=os.environ['BUILDKITE_PIPELINE_SLUG']   
    
    if key_value and valid_url(key_value):
        key_value=url_to_key(key_value)

    return key_value

def check_pipeline_acl(store):
    pipeline_allowed = True
    if 'allowed_pipelines' in store:
        # if os.environ['BUILDKITE_PIPELINE_SLUG'] is in list allow
        pipeline_allowed = False
        if 'BUILDKITE_PIPELINE_SLUG' in os.environ and os.environ['BUILDKITE_PIPELINE_SLUG'] in store['allowed_pipelines']:
            pipeline_allowed = True

    return pipeline_allowed

def check_team_allowed(store):
    team_allowed = True # Allow access if ACL's are not set

    if 'allowed_teams' in store:
        # Compare os.environ['BUILDKITE_TEAMS'] (colon delimited list) with team_list
        # if there is a common value, return true
        team_allowed = False
        
        # TODO:validate envVar
        if 'BUILDKITE_TEAMS' in os.environ:
            current_teams = os.environ['BUILDKITE_TEAMS'].split(':')
        else:
            current_teams = 'No team has been defined'

        if store['allowed_teams']:
            allowed_teams = store['allowed_teams']
            common_teams = set(allowed_teams).intersection(current_teams)
            if len(common_teams) >= 1:
                team_allowed = True

    return team_allowed

def check_acls(store):
    pipeline_allowed = check_pipeline_acl(store)
    team_allowed = check_team_allowed(store)

    return pipeline_allowed and team_allowed

def get_ssm_client():
    aws_region=check_aws_env()
    return boto3.client('ssm', region_name=aws_region)

def get_secrets(path_node):
    ssm_client = get_ssm_client()

    store = SSMParameterStore(prefix=path_node, ssm_client=ssm_client)
    if check_team_allowed(store):
        keys = store.keys()

        # print("keys:", store.keys())
        if 'env' in keys:
            for key in store['env'].keys():
                process_env_secret(store['env'], key)
        if 'ssh' in keys:
            for key in store['ssh'].keys():
                process_ssh_secret(store['ssh'], key)
        if 'git-creds' in keys:
            for key in store['git-creds'].keys():
                process_gitcred_secret(store['git-creds'], key)

def process_env_secret(store, key):
    os.environ[key] = store[key]

def process_ssh_secret(store, key):
    print("key:", key)

def process_gitcred_secret(store, key):
    print("key:", key)

def env_is_true(env_var):
    if env_var in os.environ:
        if os.environ[env_var] == "1" or os.environ[env_var].lower() == "true":
            return True
        else:
            return False
    else:
        return False

def dump_env_secrets(env_before):
    if env_is_true('BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DUMP_ENV'):
        env_now = os.environ

        # Get difference in sets
        diff = set(env_now).difference(env_before)
        
        for key in diff:
            print(key,"'"+os.environ[key]+"'", sep='=')

def main(argv):
    ssm_base_path=base_path()
    ssm_default_key=default_slug()
 
    key_value=secrets_slug()

    secrets_path = [ssm_base_path+'/'+ssm_default_key]

    if key_value:
        secrets_path.append(ssm_base_path+'/'+key_value)

    # print("~~~ Downloading secrets from :aws: paramstore:", ssm_base_path)
    env_before=os.environ.copy()    # In Python dict assingments are references

    for path_node in secrets_path:
        # print("Checking paramstore secrets in:", path_node)
        get_secrets(path_node)
    dump_env_secrets(env_before)    

if __name__ == "__main__":
   main(sys.argv[1:])