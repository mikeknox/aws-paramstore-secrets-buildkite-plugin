#!/usr/bin/env bash

#set -o xtrace
set -eu -o pipefail

_source="${BASH_SOURCE[0]}"
_source_dir="$( cd "$( dirname "${_source}" )" && cd .. && pwd )"

export AWS_REGION=ap-southeast-2
export BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH=/vendors/buildkite/default

# shellcheck disable=SC1090
source "${_source_dir}/hooks/environment"

echo "testA: ${testA:-}"