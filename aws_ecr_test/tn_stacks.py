from typing import List, Dict

from constructs import Construct
from aws_cdk import (
    Environment,
    Stack,
    aws_iam as iam
)

from aws_ecr_test import tn_ecr as ecr


class SampleDistributionStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, groups: Dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        account = iam.AccountPrincipal(kwargs["env"].account)
        self.repository = ecr.SampleRepository(self, f"{construct_id}ImageRepository")
        self.groups = [self.build_group(construct_id, *group) for group in groups.items()]

    def build_group(self, prefix: str, id: str, grants: List):
        group = iam.Group(self, f"{prefix}{id}Group")
        self.repository.grant_authorize(group)
        [grant(self.repository, group) for grant in grants]
        return group
