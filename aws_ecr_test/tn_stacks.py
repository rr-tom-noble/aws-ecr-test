from typing import List, Tuple

from constructs import Construct
from aws_cdk import Environment, Stack, aws_iam as iam

from aws_ecr_test import (
    tn_ecr,
    tn_iam,
)


class SampleDistributionStack(Stack):
    def __init__(
        self,
        scope: Construct,
        stack_id: str,
        *args,
        groups: Tuple,
        github: Tuple,
        **kwargs,
    ) -> None:
        super().__init__(scope, stack_id, *args, **kwargs)
        self.repository = tn_ecr.SampleRepository(self, f"{stack_id}ImageRepository")
        for group_id, grants in groups.items():
            group = iam.Group(self, f"{stack_id}{group_id}Group")
            self.repository.grant_authorize(group)
            [grant(self.repository, group) for grant in grants]
        provider_from_arn = iam.OpenIdConnectProvider.from_open_id_connect_provider_arn
        provider_arn, repo, environment, grants = github.values()
        github_provider = provider_from_arn(self, "ImportedGitHubProvider", provider_arn)
        github_principal = tn_iam.GitHubOIDCPrincipal(github_provider, repo, environment)
        github_role = iam.Role(self, f"{stack_id}GitHubRole", assumed_by=github_principal)
        self.repository.grant_authorize(github_role)
        [grant(self.repository, github_role) for grant in grants]
