import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_bedrock_langchain_python_cdk.aws_serverlesss import AwsBedrockLangchainPythonCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_bedrock_langchain_python_cdk/aws_serverlesss.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsBedrockLangchainPythonCdkStack(app, "aws-serverlesss-bedrock")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
