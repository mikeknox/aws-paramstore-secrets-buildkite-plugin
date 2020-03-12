#!/usr/bin/env bash

_source="${BASH_SOURCE[0]}"
_source_dir="$( cd "$( dirname "${_source}" )" && pwd )"

echo "Install requirements"
pip3 install -r "${_source_dir}/bk_ssm_secrets/requirements.txt"

echo "and add the bk_ssm_secrets package"
pip3 install "${_source_dir}/bk_ssm_secrets"
