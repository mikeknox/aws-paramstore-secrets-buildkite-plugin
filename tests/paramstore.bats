#!/usr/bin/env bats

load '/usr/local/lib/bats/load.bash'
load '../lib/bats-helper'
load '../lib/paramstore'


@test "processAnySecrets()" {
  export AWS_DEFAULT_REGION=eu-boohar-99
  cat <<EOF >/tmp/$$.asset
/base_path/env/foo
/base_path/env/boo/barfoo
/base_path/ssh/bar
/base_path/git-creds/bar
EOF

  stub ssh-agent \
    "-s : echo export SSH_AGENT_PID=26346"
  stub ssh-add \
    '- : echo added ssh key'

  stub aws \
    "ssm describe-parameters --parameter-filters Key=Path,Option=Recursive,Values=/base_path 'Key=Type,Values=SecureString' --query 'Parameters[*][Name]' --region=eu-boohar-99  --output text : cat /tmp/$$.asset" \
    "ssm get-parameter --name /base_path/env/foo --with-decryption --query 'Parameter.[Value]' --region=eu-boohar-99  --output text : echo zip" \
    "ssm get-parameter --name /base_path/env/boo/barfoo --with-decryption --query 'Parameter.[Value]' --region=eu-boohar-99  --output text : echo boo" \
    "ssm get-parameter --name /base_path/ssh/bar --with-decryption --query 'Parameter.[Value]' --region=eu-boohar-99  --output text : echo fuzz"

  run getAllEnvVarsAfterCmd processAnySecrets "/base_path"

  assert_output --partial "Adding git-credentials in /base_path/git-creds/bar as a credential helper"
  assert_output --partial "Found /base_path/ssh/bar"
  assert_success

  unstub aws
  unstub ssh-add
  unstub ssh-agent
}

@test "processEnvSecret()" {
  export AWS_DEFAULT_REGION=eu-boohar-99
  stub aws \
    "ssm get-parameter --name /base_path/env/foo --with-decryption --query 'Parameter.[Value]' --region=eu-boohar-99  --output text : echo bar"

  run getAllEnvVarsAfterCmd processEnvSecret "/base_path/env/foo"

  assert_success
  assert_output --partial "foo=bar"

  unstub aws
}

@test "processGitCredentialsSecret()" {
  export AWS_DEFAULT_REGION=eu-boohar-99
  run getAllEnvVarsAfterCmd processGitCredentialsSecret "/base_path/git-creds/foo"

  assert_success
  assert_output --partial "Adding git-credentials in /base_path/git-creds/foo as a credential helper"
  assert_output --partial "GIT_CONFIG_PARAMETERS='credential.helper=/plugin/git-credential-parameterstore-secrets /base_path/git-creds/foo'"
}

@test "processSshSecret()" {
  export AWS_DEFAULT_REGION=eu-boohar-99
  stub aws \
    "ssm get-parameter --name /base_path/ssh/foo --with-decryption --query 'Parameter.[Value]' --region=eu-boohar-99  --output text : echo bar"

  run processSshSecret "/base_path/ssh/foo"

  assert_success
  assert_output --partial "Found /base_path/ssh/foo, downloading"

  unstub aws
}
