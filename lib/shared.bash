#!/bin/bash
set -ueo pipefail

[ -z "${TMPDIR:-}" ] && TMPDIR=${TMPDIR:-/tmp}

list_secrets() {
  local basePath="$1"

  local _list
  _list="$(aws ssm describe-parameters --parameter-filters "Key=Path,Option=Recursive,Values=${basePath}" 'Key=Type,Values=SecureString' --query 'Parameters[*][Name]' --region="${AWS_DEFAULT_REGION}" --output text)"
  local retVal=${PIPESTATUS[0]}
  echo "${_list:-}"

  return "$retVal"
}

secret_exists() {
  local basePath="$1"
  local key="$2"

  local _list
  _list="$(list_secrets "${basePath}")"

  echo "${_list}" | grep "^${basePath}/${key}$" >& /dev/null
  # shellcheck disable=SC2181
  if [ "$?" -ne 0 ] ; then
    return 1
  else
    return 0
  fi
}

secret_download() {
  local path="$1"

  _secret="$(aws ssm get-parameter --name "${path}" --with-decryption --query 'Parameter.[Value]' --region="${AWS_DEFAULT_REGION}" --output text)"
  # shellcheck disable=SC2181
  if [ "$?" -ne 0 ] ; then
    return 1
  fi
  echo "$_secret"
}

add_ssh_private_key_to_agent() {
  local ssh_key="$1"

  if [[ -z "${SSH_AGENT_PID:-}" ]] ; then
    echo "Starting an ephemeral ssh-agent" >&2;
    eval "$(ssh-agent -s)"
  fi

  echo "Loading ssh-key into ssh-agent (pid ${SSH_AGENT_PID:-})" >&2;
  echo "$ssh_key" | env SSH_ASKPASS="/bin/false" ssh-add -
}

grep_secrets() {
  grep -E 'private_ssh_key|id_rsa_github|env|environment|git-credentials$' "$@"
}

getSecretType() {
  # Given 2 paths, return the first element that differs
  # return success if that 1st differign element is a validType

  local base_path="$1"
  local path="$2"

  # shellcheck disable=SC2207
  local base_path_elements=($(echo "$base_path" | tr "/" "\n"))
  # shellcheck disable=SC2207
  local path_elements=($(echo "$path" | tr "/" "\n"))

  local secret_type="unknown"
  
  local i ; for i in $(seq 0 ${#path_elements[@]}); do
    if [ "${base_path_elements[$i]:-}" != "${path_elements[$i]}" ] ; then
      secret_type="${path_elements[$i]}"
      break
    fi
  done

  # echo "${secret_type:-}"  
  valid_type "${secret_type:-}"
  retVal=$?

  if [ ${retVal} -ne 0 ] ; then
    secret_type="unknown"
  fi

  echo "${secret_type:-}"  
  return 0
}

valid_type() {
  # Return success if the string we're passed is an accepted param type
  local type_to_validate="${1:-}"
  local secret_types=(
    'env'
    'git-creds'
    'ssh'
  )

  local my_type='unknown'

  local secret_type ;for secret_type in "${secret_types[@]}" ; do
    [ "${secret_type:-}" == "${type_to_validate:-}" ] && my_type="${secret_type:-}"
  done

  if [ "${my_type}" == "unknown" ] ; then
    return 1
  else
    return 0
  fi
}

# The function creates global variables with the parsed results.
# It returns 0 if parsing was successful or non-zero otherwise.
#
# [schema://][user[:password]@]host[:port][/path][?[arg1=val1]...][#fragment]
#
# from http://vpalos.com/537/uri-parsing-using-bash-built-in-features/
parse_url() {
  local uri="$*"

  # safe escaping
  uri="${uri//\`/%60}"
  uri="${uri//\"/%22}"

  # top level parsing
  pattern='^(([a-z]{3,5}):\/\/)?((([^:\/]+)(:([^@\/]*))?@)?([^:\/?]+)(:([0-9]+))?)(\/[^?]*)?(\?[^#]*)?(#.*)?$'
  [[ "$uri" =~ $pattern ]] || return 1;

  # component extraction
  uri=${BASH_REMATCH[0]}
  export uri_schema=${BASH_REMATCH[2]}
  export uri_address=${BASH_REMATCH[3]}
  export uri_user=${BASH_REMATCH[5]}
  export uri_password=${BASH_REMATCH[7]}
  export uri_host=${BASH_REMATCH[8]}
  export uri_port=${BASH_REMATCH[10]}
  export uri_path=${BASH_REMATCH[11]}
  export uri_query=${BASH_REMATCH[12]}
  export uri_fragment=${BASH_REMATCH[13]}

  # path parsing
  count=0
  path="$uri_path"
  pattern='^/+([^/]+)'
  while [[ $path =~ $pattern ]]; do
    eval "uri_parts[$count]=\"${BASH_REMATCH[1]}\""
    path="${path:${#BASH_REMATCH[0]}}"
    (( count++ ))
  done

  # query parsing
  count=0
  query="$uri_query"
  pattern='^[?&]+([^= ]+)(=([^&]*))?'
  while [[ $query =~ $pattern ]]; do
    eval "uri_args[$count]=\"${BASH_REMATCH[1]}\""
    eval "uri_arg_${BASH_REMATCH[1]}=\"${BASH_REMATCH[3]}\""
    query="${query:${#BASH_REMATCH[0]}}"
    (( count++ ))
  done

  # loop exist when $query is empty, but this results in a failure code
  # by default this is returned. A non-zero due to a empty $query is not a failure
  local retVal=$?
  [ -z "${query:-}" ] && retVal=0

  return $retVal
}