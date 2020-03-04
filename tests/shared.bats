#!/usr/bin/env bats

load '/usr/local/lib/bats/load.bash'
load '../lib/shared'

# export AWS_STUB_DEBUG=/dev/tty
# export SSH_AGENT_STUB_DEBUG=/dev/tty
# export SSH_ADD_STUB_DEBUG=/dev/tty
# export GIT_STUB_DEBUG=/dev/tty

#-------
# Default scope
@test "list_secrets() - single secret" {
  export AWS_DEFAULT_REGION=eu-boohar-99
  stub aws \
    "ssm describe-parameters --parameter-filters Key=Path,Option=Recursive,Values=/path 'Key=Type,Values=SecureString' --query 'Parameters[*][Name]' --region=eu-boohar-99  --output text : echo -e '/path/env'"

  run list_secrets /path

  assert_success
  assert_output "/path/env"

  unstub aws
}

@test "list_secrets() - multiple secrets" {
  export AWS_DEFAULT_REGION=eu-boohar-99
  cat <<EOF >/tmp/$$.asset
/path/env
/path/key2/env
EOF

  stub aws \
    "ssm describe-parameters --parameter-filters Key=Path,Option=Recursive,Values=/path 'Key=Type,Values=SecureString' --query 'Parameters[*][Name]' --region=eu-boohar-99  --output text : cat /tmp/$$.asset"

  run list_secrets /path

  assert_success
  assert_output "/path/env
/path/key2/env"

  unstub aws
}

@test "secret_exists() - success" {
  export AWS_DEFAULT_REGION=eu-boohar-99
  cat <<EOF >/tmp/$$.asset
/path/env
/path/key2/env
EOF

  stub aws \
    "ssm describe-parameters --parameter-filters Key=Path,Option=Recursive,Values=/path 'Key=Type,Values=SecureString' --query 'Parameters[*][Name]' --region=eu-boohar-99  --output text : cat /tmp/$$.asset"

  run secret_exists /path env

  assert_success

  unstub aws
}

@test "secret_exists() - failure" {
  export AWS_DEFAULT_REGION=eu-boohar-99
  cat <<EOF >/tmp/$$.asset
/path/env
/path/key2/env
EOF

  stub aws \
    "ssm describe-parameters --parameter-filters Key=Path,Option=Recursive,Values=/path 'Key=Type,Values=SecureString' --query 'Parameters[*][Name]' --region=eu-boohar-99  --output text : cat /tmp/$$.asset"

  run secret_exists /path no_env

  assert_failure

  unstub aws
}


@test "secret_download() - success" {
  export AWS_DEFAULT_REGION=eu-boohar-99
  stub aws \
    "ssm get-parameter --name /base_path/env --with-decryption --query 'Parameter.[Value]' --region=eu-boohar-99  --output text : echo fooblah"

  run secret_download /base_path/env

  assert_success

  assert_output "fooblah"

  unstub aws
}

@test "secret_download() - failure" {
  # export AWS_STUB_DEBUG=/dev/tty
  export AWS_DEFAULT_REGION=eu-boohar-99
  stub aws \
    "ssm get-parameter --name /base_path/env --with-decryption --query 'Parameter.[Value]' --region=eu-boohar-99  --output text : exit 1"

  run secret_download /base_path/env

  assert_failure

  unstub aws
}

@test "add_ssh_private_key_to_agent" {
  skip
  // TODO:
}

@test "grep_secrets" {
  skip
  // TODO:
}

@test "getSecretType() - happy path" {
  run getSecretType "/base_path/foo" "/base_path/foo/ssh/bar"
  assert_output "ssh"
  assert_success

  run getSecretType "/base_path" "/base_path/ssh/bar"
  assert_output "ssh"
  assert_success

  run getSecretType "/base_path/foo" "/base_path/foo/env/bar"
  assert_output "env"
  assert_success

  run getSecretType "/base_path/foo" "/base_path/foo/git-creds/bar"
  assert_output "git-creds"
  assert_success

}

@test "getSecretType() - unhappy path" {
  run getSecretType "/base_path/boo" "/base_path/foo/ssh/bar"

  assert_output "unknown"
  assert_success

  run getSecretType "/base_path" "/base_path/foo/ssh/bar"

  assert_output "unknown"
  assert_success
}

@test "valid_type() - happy" {
  run valid_type "ssh"
  assert_success

  run valid_type "env"
  assert_success

  run valid_type "git-creds"
  assert_success

}

@test "valid_type() - unhappy" {
  run valid_type "sshasdad"

  assert_failure
}