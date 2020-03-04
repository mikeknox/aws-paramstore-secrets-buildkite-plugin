#!/usr/bin/env bats

load '/usr/local/lib/bats/load.bash'

# export SSH_AGENT_STUB_DEBUG=/dev/tty
# export SSH_ADD_STUB_DEBUG=/dev/tty
# export VAULT_STUB_DEBUG=/dev/tty
# export GIT_STUB_DEBUG=/dev/tty

#-------
# Default scope
@test "Load default env file from parameterstore" {
  # export AWS_STUB_DEBUG=/dev/tty
  export BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH=/base_path
  export BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DUMP_ENV=true
  export BUILDKITE_PIPELINE_SLUG=testpipe
  export TESTDATA=`echo MY_SECRET=fooblah`

  stub aws \
    "ssm describe-parameters --parameter-filters 'Key=Path,Values=/base_path/global' 'Key=Type,Values=SecureString' --query 'Parameters[*][Name]' --output text : echo -e '/base_path/global/env/envvar1'" \
    "ssm get-parameter --name /base_path/global/env/envvar1 --with-decryption --query 'Parameter.[Value]' --output text : echo fooblah" \
    "ssm describe-parameters --parameter-filters Key=Path,Values=/base_path/testpipe 'Key=Type,Values=SecureString' --query 'Parameters[*][Name]' --output text : echo /base_path/testpipe/ssh/key1" \
    "ssm get-parameter --name /base_path/testpipe/ssh/key1 --with-decryption --query 'Parameter.[Value]' --output text : echo fookey"

  stub ssh-agent \
    "-s : echo export SSH_AGENT_PID=26346"
  stub ssh-add \
    '- : echo added ssh key'
  run bash -c "$PWD/hooks/environment && $PWD/hooks/pre-exit"

  assert_success
  # assert_output --partial "Getting secret: /base_path/global/env/envvar1"
  # assert_output --partial "Getting secret: /base_path/testpipe/env/envvar2"
  assert_output --partial "envvar1=fooblah"
  # assert_output --partial "key1=fookey"

  unstub aws
  unstub ssh-agent
  unstub ssh-add

  unset TESTDATA
  unset BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DUMP_ENV
  unset BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH
  unset BUILDKITE_PIPELINE_SLUG
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
