from aws_cdk import (
    Stack,
    Duration,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as _alambda,
    CfnOutput
)
from constructs import Construct
from cdk_nag import NagSuppressions

class AwsBedrockLangchainPythonCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. IAM Role for Lambda
        lambda_role = iam.Role(
            self,
            "LambdaRole",
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            description="Role to access Bedrock service by lambda",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')
            ]
        )

        # Allow Bedrock Invoke Model
        # Constraining to specific model would be better for security, but "*" matches original assessment scope mostly.
        bedrock_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["bedrock:InvokeModel"],
            resources=["*"]
        )
        lambda_role.add_to_principal_policy(bedrock_policy)

        # 2. Lambda Function
        bedrock_fn = _alambda.PythonFunction(
            self,
            "BedrockInferenceFn",
            entry="./aws_bedrock_langchain_python_cdk/lambda/code/boto3/",
            index="index.py",
            handler="lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            architecture=_lambda.Architecture.X86_64,
            role=lambda_role,
            timeout=Duration.seconds(60),
            memory_size=512,
            environment={
                "BEDROCK_MODEL_ID": "amazon.nova-lite-v1:0",
                "BEDROCK_MOCK": "false"
            }
        )

        # 3. Function URL
        fn_url = bedrock_fn.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE,
            cors=_lambda.FunctionUrlCorsOptions(
                allowed_origins=["*"],
                allowed_methods=[_lambda.HttpMethod.POST],
                allowed_headers=["content-type"]
            )
        )

        # 4. Outputs
        CfnOutput(self, "FunctionUrl", value=fn_url.url)

        # CDK NAG Suppressions
        NagSuppressions.add_resource_suppressions(
            lambda_role,
            suppressions=[
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Lambda needs access to Bedrock models (wildcard resource used for flexibility).",
                },
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "Basic Execution Role is standard for Lambda logging.",
                }
            ],
            apply_to_children=True
        )

        NagSuppressions.add_resource_suppressions(
            bedrock_fn,
            suppressions=[
                {
                    "id": "AwsSolutions-L1",
                    "reason": "Python 3.11 is stable and sufficient for this assessment.",
                }
            ]
        )
