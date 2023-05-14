# Elastic CI Stack SSM secrets hooks

:warning: I can't actively support or develop this plugin at the moment.
I would strongly recommend looking at this <https://github.com/buildkite-plugins/aws-ssm-buildkite-plugin> instead.

__This project was heavily inspired by [Elastic CI stack S3 secrets hook](https://github.com/buildkite/elastic-ci-stack-s3-secrets-hooks)__

This hook wil expose secrets to your build steps stored in AWS SSM parameter store. Comparing to the S3 solution, this hook have the following features:

* Speed. Typically it will take around 1-2 seconds to do the AWS API call and retrieve the secrets, while it may take around 10 seconds to retrieve the secrets from S3(YMMV).
* Security. While the S3 based solution offers no organization and makes it hard to restrict which agent can access what, we have a meaningful hierarchy in SSM and we can easily control that in this plugin.
* Finer-grained access control. We have implemented a simple ACL that can do access control, so you can say only this team in Buildkite or these pipelines in buildkite have access to these secrets.

## Installation

We will need to install this hook the bootstrap script. We have the following snippet in ours:

```bash
# Enable ssm secrets plugin at top level
echo "export AWS_SSM_SECRETS_PLUGIN_ENABLED=1" >> /var/lib/buildkite-agent/cfn-env

# Download the plugin
SSM_PLUGIN_VER="v0.8.2"
mkdir -p /usr/local/buildkite-aws-stack/hooks/aws-paramstore-secrets
git clone -b "${SSM_PLUGIN_VER}" https://github.com/mikeknox/aws-paramstore-secrets-buildkite-plugin.git /usr/local/buildkite-aws-stack/hooks/aws-paramstore-secrets

# Install the plugin
cd /usr/local/buildkite-aws-stack/hooks/aws-paramstore-secrets && \
  python3 -m pip install . && \
  AWS_PARAMSTORE_SECRETS_PATH=/vendors/buildkite/ bash configure.sh
```

After this, we will need to add the following IAM policy to your buildkite instance profile (use the `ManagedPolicyARN` parameter in [elastic-ci-stack-for-aws](https://github.com/buildkite/elastic-ci-stack-for-aws)).

```yml
  BKInstancePolicy:
    Type: AWS::IAM::ManagedPolicy
    Properties:
      ManagedPolicyName: buildkite-agent-instance-policies
      PolicyDocument:
        Version: 2012-10-17
        Statement:
          - Effect: Allow
            Action:
              - 'ssm:GetParameter*'
            Resource:
              - !Sub "arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/vendors/buildkite/*"
          - Effect: Allow
            Action:
              - 'ssm:DescribeParameters'
            Resource:
              - !Sub "arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:*"
```

## Usage

We store these two types of items in SSM parameter store:

* `ssh` for SSH Private Keys(Deploy keys)
* `env` Environment Variables

As mentioned before, we have defined the following SSM namespace hierarchy:

* `<BASE_PATH>/<slug>/env/<env name>`
* `<BASE_PATH>/<slug>/ssh/key`

Where `BASE_PATH` is where you want the SSM items to be saved. `slug` is either the slug of your pipeline or a calculated repo slug. For example: if your `BASE_PATH` is `/vendors/buildkite/`, and you have an environment variable name `ACCESS_TOKEN`  for a pipeline named `build-awesome-product`, you'll need to save an SSM item with name `/vendors/buildkite/build-awesome-product/env/ACCESS_TOKEN`. For ssh deploy keys, we would prefer to store it in a repo-based slug so if the repository is used in many pipelines, we don't have to define the key for all the pipelines. In this case, if our repo is `git@github.com:torvarlds/linux.git`, the calculated ssm path would be `/vendors/buildkite/github.com_torvarlds_linux.git/ssh/key`.

## Advanced Features

We also have a few more advanced usage patterns to exert the full strength of this plugin:

* Global secrets
* Different `BASE_PATH` for different agents
* Global deploy key
* Access Control lists

We will explain these use cases one by one.

### Global secrets

At times, we want to make some secrets globally accessible for all projects. This is achieved by using a special slug named `global`.

For example, we have an internal go module hosted in JFrog and we would like it to be available to all the user repositories, so we have added an SSM item under `<BASE_PATH>/global/env/JFROG_GO_TOKEN`. Later on, all pipelines can reference this secret as `JFROG_GO_TOKEN` in their pipeline environment variables.

Another use case is, we are have a few internal buildkite plugins hosted on our SCM and we would like to make it public internally. So we have created a deploy key for all the plugins, and we saved this key to `<BASE_PATH>/global/ssh/key`, so it's always available.

If you think about it, the global ssh key is a bit hard to implement, because this is not really like an environment variable you can set and forget, we need to make it work together with another SSH key for the project, and it won't work if you add multiple deploy keys to the same SSH agent, as only the first SSH key will be attempted. So under the hood, we run multiple SSH agents in the process, and use the `pre-checkout` and `post-checkout` hooks to switch the SSH environment variables.

### Different `BASE_PATH` for different agents

We are using Buildkite for our build and deployment process, and we have an internal requirement that we are managing the permission right. Our solution is to use separate buildkite agents with different access to different SSM namespaces. For example, agents from the default queue will have `BASE_PATH` set to `/vendors/buildkite/default/`, and the agents for our CDE(Card Data Environment) environment will have `BASE_PATH` set to `/vendors/buildkite/cde`. We have the IAM Role setup so that the default queue cannot use the build secrets for CDE.

### Access Control lists

A limited form of ACL has been added to this plugin, each `<slug>` can contain:

* `allowed_teams`   - A list of teams that can access the secrets at this node
* `allowed_pipelines`   - A list of pipelines that can access the teams at this node

If either of these params exist at a node, then access is denied unless the current team and/or pipeline is listed.

The plugin assesses team membership based on data supplied in `BUILDKITE_BUILD_CREATOR_TEAMS` and `BUILDKITE_UNBLOCKER_TEAMS` environment variables.
:warning: If both of those variables are empty, *and* `BUILDKITE_SOURCE == "schedule"` then `allowed_teams` is deemed true.
The assumption is that the scheduled build was created by an approved individual, as creating a Scheduled Build in BuildKite requires 'Full Access' to the pipeline.

Don't let this lure you into a false sense of security; as your agent has access to the Parameter Store tree with the secrets, any pipeline could bypass the plugin and access the secrets directly.

## Testing

To run locally:

```bash
docker-compose run shellcheck
docker-compose run unittest
```

## License

MIT (see [LICENSE](LICENSE))
