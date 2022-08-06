from constructs import Construct
from aws_cdk import (
    RemovalPolicy,
    aws_ecr as ecr,
    aws_iam as iam,
)

from aws_ecr_test.utils import verify_unset


class SampleRepository(ecr.Repository):
    def __init__(self, scope: Construct, construct_id: str, *args, **kwargs):
        verify_unset(kwargs, ["image_scan_on_push", "encryption_key", "removal_policy"])
        kwargs["image_scan_on_push"] = True
        kwargs["encryption_key"] = ecr.RepositoryEncryption.KMS
        kwargs["removal_policy"] = RemovalPolicy.DESTROY
        super(SampleRepository, self).__init__(scope, construct_id, *args, **kwargs)

    @staticmethod
    def grant_authorize(identity: iam.IGrantable):
        """Grants the identity access to obtain authorization tokens."""
        authorize_access = iam.PolicyStatement(
            actions=["ecr:GetAuthorizationToken"],
            resources=["*"],
        )
        identity.add_to_policy(authorize_access)

    def grant_read_images(self, identity: iam.IGrantable):
        """Grants the identity access to download images from the repository"""
        read_access = iam.PolicyStatement(
            actions=[
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:DescribeRepositories",
                "ecr:ListImages",
                "ecr:DescribeImages",
                "ecr:BatchGetImage",
            ],
            resources=[self.repository_arn],
        )
        identity.add_to_policy(read_access)

    def grant_write_images(self, identity: iam.IGrantable):
        """Grants the identity access to write images to the repository."""
        write_access = iam.PolicyStatement(
            actions=[
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:PutImage",
            ],
            resources=[self.repository_arn],
        )
        identity.add_to_policy(write_access)

    def grant_read_metadata(self, identity: iam.IGrantable):
        """Grants the identity access to view AWS metadata about the repository."""
        meta_access = iam.PolicyStatement(
            actions=[
                "ecr:GetRepositoryPolicy",
                "ecr:GetLifecyclePolicy",
                "ecr:GetLifecyclePolicyPreview",
                "ecr:ListTagsForResource",
                "ecr:DescribeImageScanFindings",
            ],
            resources=[self.repository_arn],
        )
        identity.add_to_policy(meta_access)


class RepositoryGrant:
    AUTHORIZE = SampleRepository.grant_authorize
    READ_IMAGES = SampleRepository.grant_read_images
    WRITE_IMAGES = SampleRepository.grant_write_images
    READ_METADATA = SampleRepository.grant_read_metadata
