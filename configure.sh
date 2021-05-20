#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

AWS_PARAMSTORE_SECRETS_VERBOSE="${AWS_PARAMSTORE_SECRETS_VERBOSE:-0}"
AWS_PARAMSTORE_SECRETS_DEFAULT_KEY="${AWS_PARAMSTORE_SECRETS_DEFAULT_KEY:-"global"}"
AWS_PARAMSTORE_SECRETS_SECRETS_PATH="${AWS_PARAMSTORE_SECRETS_PATH:-"/vendors/buildkite"}"
AWS_PARAMSTORE_SECRETS_GLOBAL_SSH="${AWS_PARAMSTORE_SECRETS_GLOBAL_SSH:-}"
AWS_PARAMSTORE_SECRETS_RUN_SSH_AGENT_DURING_COMMAND="${AWS_PARAMSTORE_SECRETS_RUN_SSH_AGENT_DURING_COMMAND:-0}"

mkdir -p /usr/local/buildkite-aws-stack/plugins/aws-paramstore-secrets
cat << EOF > /usr/local/buildkite-aws-stack/plugins/aws-paramstore-secrets/custom-defaults
export AWS_PARAMSTORE_SECRETS_VERBOSE="${AWS_PARAMSTORE_SECRETS_VERBOSE}"
export AWS_PARAMSTORE_SECRETS_DEFAULT_KEY="${AWS_PARAMSTORE_SECRETS_DEFAULT_KEY}"
export AWS_PARAMSTORE_SECRETS_SECRETS_PATH="${AWS_PARAMSTORE_SECRETS_SECRETS_PATH}"
export AWS_PARAMSTORE_SECRETS_GLOBAL_SSH="${AWS_PARAMSTORE_SECRETS_GLOBAL_SSH}"
export AWS_PARAMSTORE_SECRETS_RUN_SSH_AGENT_DURING_COMMAND="${AWS_PARAMSTORE_SECRETS_RUN_SSH_AGENT_DURING_COMMAND}"
EOF

# Install the hooks, repo first so pipeline can override the repo preset.
mkdir -p /etc/buildkite-agent/hooks
cat << 'EOF' >> /etc/buildkite-agent/hooks/environment

# --- Start AWS paramstore secrets plugin ---
# AWS_SSM_SECRETS_PLUGIN_ENABLED is typically configured in /var/lib/buildkite-agent/cfn-env

if [[ -n "${AWS_SSM_SECRETS_PLUGIN_ENABLED:-}" && "${AWS_SSM_SECRETS_PLUGIN_ENABLED:-}" == "1" ]]
then
  source /usr/local/buildkite-aws-stack/plugins/aws-paramstore-secrets/hooks/environment

  # clean up
  for name in $(export | grep "AWS_PARAMSTORE_SECRETS_" | sed "s/=/ /g" | awk '{print $3}')
  do
    if [ $name = "AWS_PARAMSTORE_SECRETS_AUTH_SOCK" ] || [ $name = "AWS_PARAMSTORE_SECRETS_AGENT_PID" ]
    then
      continue
    fi
    unset $name
  done
fi
# --- End AWS paramstore secrets plugin ---
EOF

cat << 'EOF' >> /etc/buildkite-agent/hooks/pre-exit
if [[ -n "${AWS_SSM_SECRETS_PLUGIN_ENABLED:-}" && "${AWS_SSM_SECRETS_PLUGIN_ENABLED:-}" == "1" ]]
then
  source /usr/local/buildkite-aws-stack/plugins/aws-paramstore-secrets/hooks/pre-exit
fi
EOF

cat << 'EOF' >> /etc/buildkite-agent/hooks/pre-checkout
if [[ -n "${AWS_SSM_SECRETS_PLUGIN_ENABLED:-}" && "${AWS_SSM_SECRETS_PLUGIN_ENABLED:-}" == "1" ]]
then
  source /usr/local/buildkite-aws-stack/plugins/aws-paramstore-secrets/hooks/pre-checkout
fi
EOF

cat << 'EOF' >> /etc/buildkite-agent/hooks/post-checkout
if [[ -n "${AWS_SSM_SECRETS_PLUGIN_ENABLED:-}" && "${AWS_SSM_SECRETS_PLUGIN_ENABLED:-}" == "1" ]]
then
  source /usr/local/buildkite-aws-stack/plugins/aws-paramstore-secrets/hooks/post-checkout
fi
EOF

chmod +x /etc/buildkite-agent/hooks/{post-checkout,pre-checkout,pre-exit,environment}
