import os
import re
import logging
import shlex
import subprocess
from urllib.parse import urlparse

from . import config


def setup_logging():
    """Logging setup"""
    logging_kwargs = {
        "filename": f"/tmp/bk-ssm-secrets.{os.getpid()}.log",
        "format": "[%(asctime)s][%(levelname)s] %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    if config.VERBOSE:
        logging.basicConfig(level=logging.DEBUG, **logging_kwargs)
    else:
        logging.basicConfig(level=logging.INFO, **logging_kwargs)


setup_logging()


def extract_ssh_agent_envars(agent_output):
    '''
    Parse the output from ssh-agent to get only the variables and values

    Sample output:
    SSH_AUTH_SOCK=/tmp/ssh-KgoPdeGP2LPZ/agent.24789; export SSH_AUTH_SOCK;
    SSH_AGENT_PID=24790; export SSH_AGENT_PID;
    echo Agent pid 24790;

    return a dict that looks like:

    {
        'SSH_AUTH_SOCK': '/tmp/ssh-KgoPdeGP2LPZ/agent.24789',
        'SSH_AGENT_PID': '24790'
    }
    '''
    pairs = [line.split(";")[0] for line in agent_output.decode().splitlines()[:2]]
    return {pair.split("=")[0]: pair.split("=")[1] for pair in pairs}

def dump_env_secrets(env_before):
    """
    Diff the current os.environ with env_before to find changed environment
    variables.
    """
    for key in os.environ:
        changed_value = key in env_before and os.environ[key] != env_before[key]

        if changed_value or key not in env_before:
            export = f"export {key}={shlex.quote(os.environ[key])}"
            logging.debug(f"exporting: {export}")
            print(export)

def url_to_slug(url):
    groups = re.match(r'.*(?:@|//)([\w.]*):?([\d]*)?/?(.*)', url).groups()
    return '{}{}{}'.format(
        groups[0],
        ('-' + groups[1]) if groups[1] else '',
        '_' + groups[2].replace('/', '_').replace('~', '_')
    )

def key_to_env_name(key_name):
    return key_name.upper().replace("-", "_")

def start_ssh_agent(ssh_key_text):
    """
    This function will start an SSH agent and add a ssh private key to it.

    This is used to start a separate ssh agent for the ssh key we obtained from
    parameter store.
    """
    ssh_agent = subprocess.run(
        ['ssh-agent', '-s'], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if ssh_agent.returncode != 0:
        logging.error(
            f"ssh-agent process failed with: {ssh_agent.returncode}."
            f"stdout: `{ssh_agent.stdout}`, stderr: `{ssh_agent.stderr}`"
        )
        raise RuntimeError("starting ssh agent failed.")

    envvars = os.environ.copy()
    envvars.update(extract_ssh_agent_envars(ssh_agent.stdout))
    logging.debug(f"Started new ssh-agent (pid {envvars['SSH_AGENT_PID']})")
    envvars['SSH_ASKPASS'] = '/bin/false'
    ssh_add = subprocess.run(
        ['ssh-add', '-'], input=ssh_key_text + '\n', env=envvars,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8',
    )

    if ssh_add.returncode != 0:
        logging.error(
            f"ssh-add process failed with: {ssh_add.returncode}."
            f"stdout: `{ssh_add.stdout}`, stderr: `{ssh_add.stderr}`"
        )
        raise RuntimeError("ssh-add failed.")

    return envvars
