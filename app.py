import os
import aws_cdk as cdk

from aws_ecr_test.tn_stacks import SampleDistributionStack
from aws_ecr_test.tn_ecr import RepositoryGrant as Grant

app = cdk.App()
env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
)
github_provider = os.environ["AWS_GITHUB_PROVIDER_ARN"]

SampleDistributionStack(
    app,
    "SampleImageDevelopment",
    env=env,
    groups={"Developer": [Grant.READ_IMAGES, Grant.WRITE_IMAGES, Grant.READ_METADATA]},
    github={
        "provider": github_provider,
        "repo": "rr-tom-noble/aws-ecr-test",
        "branch": "foo",
        "grants": [Grant.READ_IMAGES, Grant.WRITE_IMAGES],
    },
)

SampleDistributionStack(
    app,
    "SampleImageMaster",
    env=env,
    groups={"Developer": [Grant.READ_IMAGES, Grant.READ_METADATA]},
    github={
        "provider": github_provider,
        "repo": "rr-tom-noble/aws-ecr-test",
        "branch": "master",
        "grants": [Grant.WRITE_IMAGES, Grant.WRITE_IMAGES],
    },
)

SampleDistributionStack(
    app,
    "SampleImageRelease",
    env=env,
    groups={
        "Developer": [Grant.READ_IMAGES, Grant.READ_METADATA],
        "EndUser": [Grant.READ_IMAGES],
    },
    github={
        "provider": github_provider,
        "repo": "rr-tom-noble/aws-ecr-test",
        "branch": "master",
        "grants": [Grant.WRITE_IMAGES],
    },
)

app.synth()
