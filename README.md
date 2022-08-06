# AWS Software Deployment Example

This repository demonstrates the use of the [AWS Cloud Development Kit (CDK)](https://aws.amazon.com/cdk/) and 
[AWS Elastic Container Registry (ECR)](https://aws.amazon.com/ecr/) to distribute built software to end-users, 
developers, and Github Actions via a cloud-hosted Docker registry.
[AWS Identity and Access Management(IAM)](https://aws.amazon.com/iam/) is used to secure the registry and provide
appropriate levels of access to the relevant parties.

CDK is used for Infrastructure as Code, which manages and related groups of AWS resources as stacks, which are deployed
via [AWS CloudFormation](https://aws.amazon.com/cloudformation/).

Each stack in the application consists of an ECR instance with users and groups of varying levels of access. 

The application consists of three such stacks:

- A Development stack, used to manage feature branch images
- A Master stack, used to manage master branch images
- A Release stack, used to manage manually released images

## Overview

TODO: Architecture Diagram

### Permissions

Permissions to the registry are granted at four levels:

- Authorize access: Required by any user to log in to the registry.
- Read access: Required by a user to download images from the registry.
- Write access: Required by a user to push images to the registry.
- Metadata access: Required by a user to view AWS metadata about the registry.

The relevant identities are split into three categories:

- Developers: People who will be working on the code.
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

### Workflow



## First Time Setup

1. Install pip and npm.
2. Run `npm install && pip3 -r requirements.txt`.
3. Create an AWS account [here](https://portal.aws.amazon.com/billing/signup#/start/email).
5. Log in to the AWS Console and navigate to the IAM Dashboard.
6. Create a new user, GitHubDeployment, with programmatic access and click Next.
7. Create a new group, DeploymentGroup, with the AWSCloudFormationFullAccess policy.
8. Continue through the Tags and Review steps to finish creating the user.
9. From the GitHub repository, navigate to Settings > Environments.
10. Create a new environment, Deployment.
11. Configure the environment with protection rules, and set the deployment branch to master.
12. Add the following secrets to the environment:
    - `AWS_ACCESS_KEY_ID`: The ID of the GithubDeployment user.
    - `AWS_ACCESS_SECRET_KEY`: The secret key of the GitHub Deployment user.
    - `AWS_DEFAULT_REGION`: The name of the deployment region.

## Deployment

1. Navigate to the Actions page of the repository.
2. Manually run the Deploy to AWS workflow for each stack.

## Post Deployment

1. Log in to the AWS Console and Navigate to the IAM Dashboard.
2. Create a user, GitHubDevelopment, with programmatic access.
3. Assign the user to the SampleImageDevelopment...GitHubGroup group.
4. Navigate to the repository containing the source of the Docker image.
5. Navigate to Settings > Environments.
6. Create an Environment, Development.
7. Configure the environment with protection rules and deployment branches.
8. Add the following secrets to the environment:
   - `AWS_SECRET_KEY_ID`: The ID of the GithubDevelopment user.
   - `AWS_ACCESS_KEY_ID`: The secret key of the GithubDevelopment user.
   - `AWS_DEFAULT_REGION`: The name of the deployment region.
   - `AWS_ECR_REGISTRY`: The ARN of the Development docker registry (found through the ECR Dashboard).
9. Repeat steps 2 through 8 for the Master and Release stacks **(development branch should be master only)**.


## New Developers

**Manager Steps**

1. Log in to the AWS Console and Navigate to the IAM Dashboard.
2. Create a user for the developer with programmatic and password access (MFA enabled).
3. Assign the user to the following groups:
   - SampleImageDevelopment...DeveloperGroup
   - SampleImageMaster...DeveloperGroup
   - SampleImageRelease...DeveloperGroup

**Developer Steps**

1. Run `pip3 install awscli`
2. Log in to the AWS Console and Navigate to the IAM Dashboard.
3. Navigate to Users > <Your User> > Security Credentials > Create Access Key
4. Run `aws configure` and enter your ID and secret key when prompted.