from aws_cdk import (
    Stack,
    aws_secretsmanager as secretsmanager,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions
)
from constructs import Construct

class BpInfraFinalStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Referencia o segredo que contém seu token do GitHub
        github_token = secretsmanager.Secret.from_secret_name_v2(
            self, "GitHubToken", "github-token"
        )
        
        # 2. Define a fonte do pipeline a partir do seu repositório no GitHub
        source_artifact = codepipeline.Artifact()
        source_action = codepipeline_actions.GitHubSourceAction(
            action_name="GitHub_Source",
            owner="bruno0nline",
            repo="bp-bioenergy-prod-pipeline",
            oauth_token=github_token.secret_value,
            output=source_artifact,
            branch="master"
        )

        # 3. Define o projeto de compilação
        build_project = codebuild.PipelineProject(self, "BPBioenergyBuildProject",
            build_spec=codebuild.BuildSpec.from_source_filename('buildspec.yml')
        )
        build_artifact = codepipeline.Artifact("BPBioenergyBuildArtifact")
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="BP-CodeBuild",
            project=build_project,
            input=source_artifact,
            outputs=[build_artifact]
        )

        # 4. Define o pipeline com os estágios
        codepipeline.Pipeline(self, "BPBioenergyPipeline",
            pipeline_name="BPBioenergy-CICD-Pipeline",
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[source_action]
                ),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[build_action]
                ),
                codepipeline.StageProps(
                    stage_name="Approval",
                    actions=[
                        codepipeline_actions.ManualApprovalAction(
                            action_name="BP-Deploy-Approval"
                        )
                    ]
                )
            ]
        )