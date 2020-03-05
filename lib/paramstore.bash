#!/bin/bash
set -ueo pipefail

_source="${BASH_SOURCE[0]}"
[ -z "${_source:-}" ] && _source="${0}"
basedir="$( cd "$( dirname "${_source}" )" && cd .. && pwd )"

# shellcheck disable=SC1090
. "$basedir/lib/shared.bash"

[ -z "${TMPDIR:-}" ] && TMPDIR=${TMPDIR:-/tmp}

processAnySecrets() {
  local base_path="$1"

  echo "Checking secret path ${base_path}" >&2
  secrets="$(list_secrets "${base_path}")"
  for secret in $secrets ; do
    secret_type=$(getSecretType "${base_path}" "$secret")
    echo "secret_type: ${secret_type:-}"
    case "${secret_type:-}" in
      env|environment) processEnvSecret "$secret";;
      ssh|private_ssh_key|id_rsa_github) processSshSecret "$secret";;
      git-creds|git-credentials) processGitCredentialsSecret "$secret";;
    esac
  
  done

  return 0
}

processSshSecret() {
  local path="$1"

  echo "Found ${path}, downloading" >&2;
  if ! ssh_key=$(secret_download "${path}") ; then
    echo "+++ :warning: Failed to download ssh-key $path" >&2;
    exit 1
  fi
  echo "Downloaded ${#ssh_key} bytes of ssh key"
  add_ssh_private_key_to_agent "$ssh_key"
  key_found=1

  if [[ -z "${key_found:-}" ]] && [[ "${BUILDKITE_REPO:-}" =~ ^git ]] ; then
    echo "+++ :warning: Failed to find an SSH key in secret bucket" >&2;
    exit 1
  fi
}

processEnvSecret() {
  # Load an env secret
  local path="$1"
  local envscript=''

  key_name="$(basename "$path")"
  echo "Downloading env secret from ${path}" >&2;
  secret="$(secret_download "${path}")"

  if [ -z "${secret:-}" ] ; then 
    echo "+++ :warning: Failed to download env from $path" >&2;
    exit 1
  fi

  envscript="${key_name}='${secret}'"
  echo "Evaluating ${#envscript} bytes of env"
  set -o allexport
  eval "$envscript"
  set +o allexport
}

processGitCredentialsSecret() {
  local path="$1"

  git_credentials=()

  echo "Adding git-credentials in $path as a credential helper" >&2;

  git_credentials+=("'credential.helper=$basedir/git-credential-parameterstore-secrets ${path}'")

  if [[ "${#git_credentials[@]}" -gt 0 ]] ; then
    export GIT_CONFIG_PARAMETERS
    GIT_CONFIG_PARAMETERS=$( IFS=' '; echo -n "${git_credentials[*]}" )
  fi
}

dumpEnvSecrets() {
  if [[ "${BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DUMP_ENV:-}" =~ ^(true|1)$ ]] ; then
    echo "~~~ Environment variables that were set" >&2;

    # shellcheck disable=SC2154 # var is defined as a global in hooks/environment
    comm -13 <(echo "$env_before") <(env | sort) || true
  fi
}