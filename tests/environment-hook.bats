#!/usr/bin/env bats

load '/usr/local/lib/bats/load.bash'

# export SSH_AGENT_STUB_DEBUG=/dev/tty
# export SSH_ADD_STUB_DEBUG=/dev/tty
# export VAULT_STUB_DEBUG=/dev/tty
# export GIT_STUB_DEBUG=/dev/tty

function setup() {
  [ -f ./custom-defaults ] && rm ./custom-defaults
  true
}

function teardown() {
  [ -f ./custom-defaults ] && rm ./custom-defaults
  true
}


@test "Handle awkard env var values" {
  skip "doesnot handle single quote yet"
  # This is made difficult by bats
  # export AWS_STUB_DEBUG=/dev/tty
  export BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH=/base_path
  export BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DUMP_ENV=true
  export AWS_DEFAULT_REGION=eu-boohar-99

  env_vars=(
    "/base_path/global/env/has_a_space_in_the_value"
    "/base_path/global/env/has_a_double_quote_in_the_value"
    "/base_path/global/env/has_a_single_quote_in_the_value"
  )
  stub aws \
    "ssm describe-parameters --parameter-filters 'Key=Path,Option=Recursive,Values=/base_path/global' 'Key=Type,Values=SecureString' --query 'Parameters[*][Name]' --region=eu-boohar-99  --output text : echo -e \"${env_vars[*]}\"" \
    "ssm get-parameter --name ${env_vars[0]} --with-decryption --query 'Parameter.[Value]' --region=eu-boohar-99  --output text : echo -e 'foo blah'" \
    "ssm get-parameter --name ${env_vars[1]} --with-decryption --query 'Parameter.[Value]' --region=eu-boohar-99  --output text : echo -e 'ab\"cd'" \
    "ssm get-parameter --name ${env_vars[2]} --with-decryption --query 'Parameter.[Value]' --region=eu-boohar-99  --output text : echo -e \"kl\'zx\""

  run bash -c "$PWD/hooks/environment && $PWD/hooks/pre-exit"

  assert_success
  assert_output --partial "$(basename ${env_vars[0]})=foo blah"
  assert_output --partial "$(basename ${env_vars[1]})=ab\"cd"
  assert_output --partial "$(basename ${env_vars[2]})=kl'zx"

  unstub aws

  unset TESTDATA
  unset BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DUMP_ENV
  unset BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH
  unset BUILDKITE_PIPELINE_SLUG
  unset AWS_DEFAULT_REGION
}

# TODO: test envvar clobber

@test "Load default environment file from parameterstore" {
  skip
}

@test "Load default env and environments files from parameterstore" {
  skip
}

#-------
# Project scope
@test "Load project env file from parameterstore" {
  skip
}

@test "Load project environment file from parameterstore" {
  skip
}

@test "Load project env and environments files from parameterstore" {
  skip
}

#-------
# Combinations of scopes
@test "Load default and project env files from parameterstore" {
  skip
}

@test "Load default and project environment files from parameterstore" {
  skip
}

#-------
# All scopes and env, environment files
@test "Load env and environments files for project and default from parameterstore" {
  skip
}

#-------
# Git Credentials
@test "Load default git-credentials from parameterstore into GIT_CONFIG_PARAMETERS" {
  skip
}

@test "Load pipeline git-credentials from parameterstore into GIT_CONFIG_PARAMETERS" {
  skip
}

#-------
# ssh-keys
@test "Load default ssh-key from parameterstore into ssh-agent" {
  skip
}

@test "Load project ssh-key from parameterstore into ssh-agent" {
  skip
}

@test "Load default and project ssh-keys from parameterstore into ssh-agent" {
  skip
}

@test "Load default ssh-key and env from parameterstore" {
  skip
}

@test "Load project ssh-key and env from parameterstore" {
  skip
}

@test "Load default ssh-key, env and git-credentials from parameterstore into ssh-agent" {
  skip
}

@test "Load project ssh-key, env and git-credentials from parameterstore into ssh-agent" {
  skip
}

@test "Dump env secrets" {
  skip
}
