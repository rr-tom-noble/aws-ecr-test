import os

import aws_cdk as cdk

from aws_ecr_test.tn_stacks import SampleDistributionStack
from aws_ecr_test.tn_ecr import RepositoryGrant as Grant

app = cdk.App()

SampleDistributionStack(
    app,
    "SampleImageDevelopment",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    groups={
        "Developer": [Grant.READ_IMAGES, Grant.WRITE_IMAGES, Grant.READ_METADATA],
        "Github": [Grant.READ_IMAGES, Grant.WRITE_IMAGES],
    }
)

SampleDistributionStack(
    app,
    "SampleImageMaster",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    groups={
        "Developer": [Grant.READ_IMAGES, Grant.READ_METADATA],
        "GitHub": [Grant.WRITE_IMAGES],
    }
)

SampleDistributionStack(
    app,
    "SampleImageRelease",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    groups={
        "Developer": [Grant.READ_IMAGES, Grant.READ_METADATA],
        "EndUser": [Grant.READ_IMAGES],
        "Github": [Grant.WRITE_IMAGES],
    },
)

app.synth()
