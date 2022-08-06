from aws_cdk import aws_iam as iam

from aws_ecr_test.utils import verify_unset


class GithubOIDCPrincipal(iam.OpenIdConnectPrincipal):
    """An OpenIdConnectPrincipal accessible to a GitHub runner on `branch` of `repo`."""

    def __init__(
        self, provider: iam.OpenIdConnectProvider, repo: str, branch: str, *args, **kwargs
    ) -> None:
        verify_unset(kwargs, ["conditions"])
        issuer = "token.actions.githubusercontent.com"
        kwargs["conditions"] = {
            "StringEquals": {
                f"{issuer}:aud": "sts.amazonaws.com",
                f"{issuer}:sub": f"repo:{repo}:ref:refs/heads/{branch}",
            }
        }
        super(GithubOIDCPrincipal, self).__init__(provider, *args, **kwargs)
