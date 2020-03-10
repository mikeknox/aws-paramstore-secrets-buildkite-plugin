#!/usr/bin/env bash

python3 -m venv venv

# shellcheck disable=SC1091
source ./venv/bin/activate

pip3 install -r bk_ssm_secrets/requirements.txt

pip3 install -e bk_ssm_secrets