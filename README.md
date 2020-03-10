# AWS Parameterstore Secrets Buildkite Plugins

__This plugin was originally inspired and based on the the *AWS S3 Secrets Buildkite Plugin*__

It currently runs on an AWS based Buildkite stack, but it should work on any agent.

Expose secrets to your build steps. AWS Paramaterstore parameters (Secure and clear) are made available to pipeilines.

Different types of secrets are supported and exposed to your builds in appropriate ways:

- `ssh-agent` for SSH Private Keys
- Environment Variables for strings
- `git-credential` via git's credential.helper

Secrets (and in the clear) are exposed from a toplevel path (`BASE_PATH`):

- `<BASE_PATH>/<pipeline slug>/env/<env name>`
- `<BASE_PATH>/<pipeline slug>/ssh-agent/<key name>`
- `<BASE_PATH>/<pipeline slug>/git-credential/<cred name>`

The core functionality has been rewritten in Python as it provided incredibly difficult to parse repo URLs in a sane way.

## Note

The existing S3 / Vault plugins do not break out the secrets individually.

There is a virtual slug called `<global_defaults>`, which are downloaded for all pipelines in addition to the pipeline specific ones.

## Example

The following pipeline downloads a private key from `{ssm_store_path}/{pipeline}/ssh_private_key` and set of environment variables from `{ssm_store_path}/{pipeline}/environment`.
ssm_store_path - `/vendors/buildkite/secrets/` - provided as parameter

The private key is exposed to both the checkout and the command as an ssh-agent instance. The secrets in the env file are exposed as environment variables.

```yml
steps:
  - command: ./run_build.sh
    plugins:
      - mikeknox/aws-paramstore-secrets#v0.1.:
          path: /base_path
```

## IAM permissions

The agent needs to have the following permissions in IAM to access the secrets:

```yml
{
    "Action": [
        "ssm:GetParameter*"
    ],
    "Resource": [
        "arn:aws:ssm:<region>:<account>:parameter/<secret path>*"
    ],
    "Effect": "Allow"
},
{
    "Action": [
        "ssm:DescribeParameters"
    ],
    "Resource": [
        "arn:aws:ssm:<region>:<account>:*"
    ],
    "Effect": "Allow"
}
```

## Access Controls

A limited form of A.CL has been added to this plugin, each `<slug>` can contain:

- `allowed_teams`   - A list of teams that can access the secrets at this node
- `allowed_pipelines`   - A list of pipelines that can access the teams at this node

If either of these params exist at a node, then access is denied unless the current team and/or pipeline is listed.

### ACL Note

Don't let this lul you into a false sense of security; as your agent has access to the Parameter Store tree with the secrets, any pipeline could bypass the plugin and access the secrets directly.

## Uploading Secrets

### Environment secrets

Environment variable secrets are handled differently in this Parameterstore plugin to the S3 plugin.

Each environment variable is treated as an individually secret under the `env` node for a project.
eg.
project foo/env/var1
project foo/env/var2
etc

### SSH Keys

This example uploads an ssh key and an environment file to the base of the Vault secret path, which means it matches all pipelines that use it. You use per-pipeline overrides by adding a path prefix of `/my-pipeline/`.

### Git credentials

For git over https, you can use a `git-credentials` file with credential urls in the format of:

```bash
https://user:password@host/path/to/repo
```

These are then exposed via a [gitcredential helper](https://git-scm.com/docs/gitcredentials) which will download the credentials as needed.

## Options

### `path`

defaults to: `/vendors/buildkite/secrets`
This is expected to be a path in Parameterstore where we should look for secrets.
It is expected that your BuildKite agent will have permissions to read all items in this path, and decrypt any secrets there.

Alternative Base Path to use for secrets

### `secrets_key`

defaults to: `BUILDKITE_PIPELINE_SLUG`

Can be set to any valid environment variable, sych as `BUILDKITE_REPO`

### `default_key`

defaults to: `global`

A slug for default secrets that are always loaded.

## Testing

To run locally:

```bash
BUILDKITE_PLUGIN_AWS_PARAMSTORE_SECRETS_DUMP_ENV=true
BUILDKITE_PLUGIN_AWS_PARAMSTORE_PATH=/base_path
BUILDKITE_PIPELINE_SLUG=my_pipeline
hooks/environment
```

To test with BATS:

```bash
docker-compose run tests
```

## License

MIT (see [LICENSE](LICENSE))
