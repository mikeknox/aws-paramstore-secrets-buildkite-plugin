#!/usr/bin/env bats

load '/usr/local/lib/bats/load.bash'

# export SSH_AGENT_STUB_DEBUG=/dev/tty
# export SSH_ADD_STUB_DEBUG=/dev/tty
# export AWS_STUB_DEBUG=/dev/tty
# export GIT_STUB_DEBUG=/dev/tty


# Schema for git-crednetials Secrets
# [schema://][user[:password]@]host[:port][/path][?[arg1=val1]...][#fragment]

@test "Get basic git-credentials from parameterstore" {
  skip "git-credentials is not support yet"
  export BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH=/base_path
  export BUILDKITE_PIPELINE_SLUG=testpipe
  export GIT_CONFIG_PARAMETERS="'credential.helper=basedir/git-credential-parameterstore-secrets ${BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH}/git-creds/foobar'"
  export TEST_CREDS1="https://user:password@host.io:7999/path"
  export AWS_DEFAULT_REGION=eu-boohar-99

  stub aws \
    "ssm get-parameter --name /base_path/git-creds/foobar --with-decryption --query 'Parameter.[Value]' --region=eu-boohar-99  --output text : echo ${TEST_CREDS1}"

  run ./git-credential-parameterstore-secrets ${BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH}/git-creds/foobar

  assert_success
  assert_output --partial "protocol=https"
  assert_output --partial "host=host.io"
  assert_output --partial "username=user"
  assert_output --partial "password=password"

  unstub aws

  unset TEST_CREDS1
  unset GIT_CONFIG_PARAMETERS
  unset BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH
  unset BUILDKITE_PIPELINE_SLUG
  unset AWS_DEFAULT_REGION
}

@test "Get git-credentials with args from parameterstore" {
  skip "git-credentials is not support yet"
  export AWS_DEFAULT_REGION=eu-boohar-99
  export BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH=/base_path
  export BUILDKITE_PIPELINE_SLUG=testpipe
  export GIT_CONFIG_PARAMETERS="'credential.helper=basedir/git-credential-parameterstore-secrets ${BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH}/git-creds/foobar'"
  export TEST_CREDS1='https://user:password@host.io:7999/path?arg1=val1'
  
  stub aws \
    "ssm get-parameter --name /base_path/git-creds/foobar --with-decryption --query 'Parameter.[Value]' --region=eu-boohar-99  --output text : echo ${TEST_CREDS1}"

  run ./git-credential-parameterstore-secrets ${BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_PATH}/git-creds/foobar

  assert_success
  assert_output --partial "protocol=https"
  assert_output --partial "host=host.io"
  assert_output --partial "username=user"
  assert_output --partial "password=password"

  unstub aws

  unset TEST_CREDS1
  unset GIT_CONFIG_PARAMETERS
  unset BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_ADDR
  unset BUILDKITE_PIPELINE_SLUG
  unset AWS_DEFAULT_REGION
}
