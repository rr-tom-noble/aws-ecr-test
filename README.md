# AWS Software Deployment Example

This repository demonstrates the use of the [AWS Cloud Development Kit (CDK)](https://aws.amazon.com/cdk/) and 
[AWS Elastic Container Registry (ECR)](https://aws.amazon.com/ecr/) to distribute built software to end-users, 
developers, and GitHub Actions via a cloud-hosted Docker registry.

CDK is used for Infrastructure as Code, which manages related groups of AWS resources as stacks, which are deployed
via [AWS CloudFormation](https://aws.amazon.com/cloudformation/)

Each stack in the application consists of an ECR instance with users and groups of varying levels of access.

The application consists of three such stacks:

- A Development stack, used to manage feature branch images
- A Master stack, used to manage master branch images
- A Release stack, used to manage manually released images

[AWS Identity and Access Management (IAM)](https://aws.amazon.com/iam/) is used to secure the registry and provide
appropriate levels of access to the relevant parties.

Using ECR, CDK, and IAM for managing Docker images and users grants the following benefits:

- Automated scanning of image dependencies for vulnerabilities.
- Automated archiving of images when no longer relevant.
- Version controlled management of infrastructure via code.
- Easier integration of software with other AWS services.
- Easier integration with third-party authorization methods.
- Finer grained and more robust access and security features.

## Overview

TODO: Architecture Diagram

### Permissions

Permissions to the registry are granted at four levels:

- Authorize access: Required by any user to log in to the registry.
- Read access: Required by a user to download images from the registry.
- Write access: Required by a user to push images to the registry.
- Metadata access: Required by a user to view AWS metadata about the registry.

The relevant identities are split into three categories:

- Developers: People who will be working on and testing the source code.
- End Users: People who will be downloading and using the built code.
- GitHub Actions: Automated GitHub runners that will be building, testing, and releasing the code.

The following tables show which identities have which permissions in each stack.

**Development**

| Permissions | Developers | End Users | GitHub |
|-------------|------------|-----------|--------|
| Authorize   | ✔️️        | ❌         | ️✔️    |
| Read        | ✔️         | ❌         | ✔️     |
| Write       | ✔️         | ❌         | ✔️     |
| Metadata    | ✔️         | ❌         | ✔️     |

**Master**

| Permissions | Developers | End Users | GitHub |
|-------------|------------|-----------|--------|
| Authorize   | ✔️️        | ❌         | ️✔️    |
| Read        | ✔️         | ❌         | ❌️     |
| Write       | ❌️         | ❌         | ✔️     |
| Metadata    | ✔️         | ❌         | ❌️     |

**Release**

| Permissions | Developers | End Users | GitHub |
|-------------|------------|-----------|--------|
| Authorize   | ✔️️        | ✔         | ️✔️    |
| Read        | ✔️         | ✔         | ❌️     |
| Write       | ❌️         | ❌         | ✔️     |
| Metadata    | ✔️         | ❌         | ❌️     |


## Prerequisites

### Setting up your account

You should begin by [creating an AWS account](https://portal.aws.amazon.com/billing/signup#/start/email) to deploy to.

1. Log in to the AWS Console and navigate to the IAM Dashboard.
2. Create a user for yourself with the AdministratorAccess policy.
3. Run `aws configure` and enter your user ID and secret key when prompted.

### Bootstrapping the account

The AWS account will need to be bootstrapped to facilitate deployments through CDK.

1. Install pip and npm.
2. Run `npm install && pip3 -r requirements.txt`.
3. Run `cdk bootstrap`

## Setting up deployments via GitHub

### Authentication flow

1. GitHub runners are trusted by GitHub.
2. A GitHub runner uses the [Configure AWS Credentials](https://github.com/aws-actions/configure-aws-credentials) action.
3. GitHub passes an OIDC token to AWS to identify the runner as trusted.
4. If the runner is for the correct repository and branch, the runner is granted the deployment role.
5. The runner executes a number of CDK commands.
6. With the deployment role, the runner can access CloudFormation and assume tighter-scoped roles provided by CDK.

This method of authentication bypasses the need for any AWS credentials to be stored directly on the GitHub.

### Adding GitHub identity management

An identity provider is required to allow GitHub runners to identify themselves within AWS.

1. Log in to the AWS Console and navigate to the IAM Dashboard.
2. Create a new identity provider, GithubOIDCIdentityProvider, of type OpenId Connect:
    - `Provider URL`: https://token.actions.githubusercontent.com
    - `Audience`: sts.amazonaws.com

### Creating a deployment policy

A deployment policy is required to grant trusted users permission to deploy to the account through CDK.

1. Log in to the AWS Console and navigate to the IAM Dashboard.
2. Create a new policy, CDKDeploymentPolicy
3. Use the contents of [policies/deployment.json](policies/deployment.json) as policy document.

The policy will allow trusted users to assume the required CDK roles and give them full access to CloudFormation.

### Granting GitHub deployment permissions

A role is required to associate identified GitHub runners with the deployment policy.

1. Log in to the AWS Console and navigate to the IAM Dashboard.
2. Create a new role, GitHubDeploymentRole.
3. Configure the role to use the GitHubOIDCIdentityProvider for identification.
4. Assign the CDKDeploymentPolicy to the role.
5. Replace the trust policy of the role with the contents of [policies/trust_github.json](policies/trust_github.json)

The role can only be assumed by runners for the master branch of the repository, identified through GitHub.

### Configuring GitHub to use the role

The repository needs to be configured with an environment to use the deployment role.

1. From this repository, navigate to Settings > Environments.
2. Create a new environment, Deployment.
3. Configure the environment to require approval from a trusted user, and set the deployment branch to master.
4. Add the following secrets to the environment:
    - `AWS_DEFAULT_REGION`: The name of the deployment region.
    - `AWS_DEPLOYMENT_ROLE_ARN`: The ARN of GithubDeploymentRole.
    - `AWS_GITHUB_PROVIDER_ARN`: The ARN of GithubIdentityProvider.

### Creating deployment workflows

Deployment workflows should use the Deployment environment and the [Configure AWS Credentials](https://github.com/aws-actions/configure-aws-credentials)
action when deploying, along with permissions to obtain an OIDC token:

```yaml
---
name: Deploy to AWS
...
jobs:
  Deploy:
    ...
    environment: Deployment
    permissions:
        id-token: write
        contents: read
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOYMENT_ROLE_ARN }}
          aws-region: ${{ secrets.AWS_DEFAULT_REGION }}
      - name: Deploy a stack
        run: ...
```

## Developers: Deployment Repository

The following section outlines the workflow for developers working on this repository.

### Prerequisites
1. Run `python3 -m venv .venv` to create a virtual environment.
2. Run `source .venv/bin/activate` to activate the virtual environment.
3. Run `npm install && pip3 install -r requirements.txt -r requrements-dev.txt` to install the dependencies.

### Development

1. Make changes to the code.
2. Run `black app.py aws_ecr_test/ --max-line-length 90` to reformat the code.
3. Push the changes to GitHub.

### Deployment

1. Navigate to the Actions page of the repository.
2. Manually run the Deploy to AWS workflow for each stack.


## Image repository workflow

### Setting up Docker registry access

Once the stacks have been deployed, the target repository and developers will need access to push and pull images
from the deployed registries.

#### GitHub Access

1. From the target repository, Navigate to Settings > Environments.
2. Create a new environment, Development.
3. Add the following secrets to the environment:
    - `AWS_DEFAULT_REGION`: The name of the deployment region.
    - `AWS_GITHUB_ROLE_ARN`: The ARN of SampleImageDevelopment...GitHubRole.
    - `AWS_ECR_REGISTRY_ARN`: The ARN of SampleImageDevelopment...ImageRepository.
4. Repeat steps 2 and 3 for each deployment environment.
    - Non-development environments should use master only as the deployment branch.
    - Release environments should require approval by a trusted user.


#### Developer Access

1. Log in to the AWS Console and Navigate to the IAM Dashboard.
2. Create a user for the developer with programmatic and password access (MFA enabled).
3. Assign the user to the following groups:
    - SampleImageDevelopment...DeveloperGroup
    - SampleImageMaster...DeveloperGroup
    - SampleImageRelease...DeveloperGroup


### Development

- The image for a feature branch can be manually pushed using `make docker-push`.
- The image for a feature branch can be manually pulled using `make docker-pull`.
- Pushing to a feature branch with an open pull request will automatically push a changed image to the development registry.
- Merging a feature branch with master will automatically push a changed image to the master registry.

### Release

1. From the target repository, Navigate to Actions.
2. Run the Release workflow (a trusted user will need to approve the workflow).
3. The image will be pushed to the release registry.
