#!/usr/bin/env bash

echo "Get working dir"
_source="${BASH_SOURCE[0]}"
_source_dir="$( cd "$( dirname "${_source}" )" && pwd )"
_current_dir="$(pwd)"

cd "${_source_dir}" || exit 1

echo "Setup Python virtual env"
python3 -m venv venv

export VIRTUAL_ENV_DISABLE_PROMPT=true
# shellcheck disable=SC1091
source "./venv/bin/activate"

echo "Install requirements"
venv/bin/pip3 install -r bk_ssm_secrets/requirements.txt

echo "and add the bk_ssm_secrets package"
venv/bin/pip3 install -e bk_ssm_secrets

cd "${_current_dir}" || exit