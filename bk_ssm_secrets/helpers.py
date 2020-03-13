import os
import logging
import shlex
from urllib.parse import urlparse


def setup_logging():
    """Logging setup"""
    logging_kwargs = {
        "filename": "/tmp/bk-ssm-secrets.log",
        "format": "[%(asctime)s][%(levelname)s] %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    verbose_key = "BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_VERBOSE"
    if os.environ.get(verbose_key, "").lower() in ["1", "true"]:
        logging.basicConfig(level=logging.DEBUG, **logging_kwargs)
    else:
        logging.basicConfig(level=logging.INFO, **logging_kwargs)

def extract_ssh_agent_envars(agent_output):
    '''
    Parse the output from ssh-agent to get only the variables and values

    Sample output:
    SSH_AUTH_SOCK=/tmp/ssh-KgoPdeGP2LPZ/agent.24789; export SSH_AUTH_SOCK;
    SSH_AGENT_PID=24790; export SSH_AGENT_PID;
    echo Agent pid 24790;
    '''
    agent_env_vars = {}
    logging.debug(f"agent_output: {agent_output}")
    output = agent_output.replace('\n', '').split(';')

    for line in output:
        key_val_pair = line.split('=')
        if len(key_val_pair) == 2:
            agent_env_vars[key_val_pair[0]] = key_val_pair[1]
            os.environ[key_val_pair[0]]  = key_val_pair[1]

    return agent_env_vars

def dump_env_secrets(env_before):
    # Get difference in sets
    logging.debug(f"before: {env_before}")
    logging.debug(f"now: {os.environ}")
    for key in set(os.environ) & set(env_before):
        if os.environ[key] != env_before[key]:
            export = f"export {key}={shlex.quote(os.environ[key])}"
            logging.debug(f"exporting: {export}")
            print(export)
    for key in set(os.environ) - set(env_before):
        export = f"export {key}={shlex.quote(os.environ[key])}"
        logging.debug(f"exporting: {export}")
        print(export)

def url_to_slug(url):
    parsed = urlparse(url)
    if parsed.scheme == "":
        raise ValueError(f"Invalid URL scheme found: {url}")

    slug = f"{parsed.hostname}"
    if parsed.port:
        slug += f":{parsed.port}"
    if parsed.path:
        slug += "_" + parsed.path.strip("/").replace("/", "_").replace("~", "_")
    return slug
