#!/usr/bin/env bats

load '/usr/local/lib/bats/load.bash'
load '../lib/shared'

# export SSH_AGENT_STUB_DEBUG=/dev/tty
# export SSH_ADD_STUB_DEBUG=/dev/tty
# export GIT_STUB_DEBUG=/dev/tty

#-------
# Default scope
@test "list_secrets() - single secret" {
  stub aws \
    "ssm describe-parameters --parameter-filters Key=Path,Values=/path 'Key=Type,Values=SecureString' --query 'Parameters[*][Name]' --output text : echo -e '/path/env'"

  run list_secrets /path

  assert_success
  assert_output "/path/env"

  unstub aws
}

@test "list_secrets() - multiple secrets" {
  cat <<EOF >/tmp/$$.asset
/path/env
/path/key2/env
EOF

  stub aws \
    "ssm describe-parameters --parameter-filters Key=Path,Values=/path 'Key=Type,Values=SecureString' --query 'Parameters[*][Name]' --output text : cat /tmp/$$.asset"

  run list_secrets /path

  assert_success
  assert_output "/path/env
/path/key2/env"

  unstub aws
}

@test "secret_exists() - success" {
  cat <<EOF >/tmp/$$.asset
/path/env
/path/key2/env
EOF

  stub aws \
    "ssm describe-parameters --parameter-filters Key=Path,Values=/path 'Key=Type,Values=SecureString' --query 'Parameters[*][Name]' --output text : cat /tmp/$$.asset"

  run secret_exists /path env

  assert_success

  unstub aws
}

@test "secret_exists() - failure" {
  cat <<EOF >/tmp/$$.asset
/path/env
/path/key2/env
EOF

  stub aws \
    "ssm describe-parameters --parameter-filters Key=Path,Values=/path 'Key=Type,Values=SecureString' --query 'Parameters[*][Name]' --output text : cat /tmp/$$.asset"

  run secret_exists /path no_env

  assert_failure

  unstub aws
}


@test "secret_download() - success" {
  stub aws \
    "ssm get-parameter --name /base_path/env --with-decryption --query 'Parameter.[Value]' --output text : echo fooblah"

  run secret_download /base_path/env

  assert_success

  assert_output "fooblah"

  unstub aws
}

@test "secret_download() - failure" {
  stub aws \
    "ssm get-parameter --name /base_path/env --with-decryption --query 'Parameter.[Value]' --output text : exit 1"

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
  assert_failure

  run getSecretType "/base_path" "/base_path/foo/ssh/bar"

  assert_output "unknown"
  assert_failure
}

@test "valid_type() - happy" {
  run validType "ssh"
  assert_success

  run validType "env"
  assert_success

  run validType "git-creds"
  assert_success

}

@test "valid_type() - unhappy" {
  run validType "sshasdad"

  assert_failure
}