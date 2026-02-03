import json
import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Set Mock Region before importing lambda
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Add lambda directory to path to import index
sys.path.append(os.path.abspath("aws_serverless/lambda/code/boto3"))
import index

class TestLambdaHandler(unittest.TestCase):

    @patch('index.bedrock_runtime')
    def test_handler_success(self, mock_bedrock):
        # Setup mock response
        mock_response_body = json.dumps({
            'results': [{'outputText': 'Hello world'}]
        })
        mock_bedrock.invoke_model.return_value = {
            'body': MagicMock(read=lambda: mock_response_body)
        }

        event = {
            'body': json.dumps({'prompt': 'Hi'})
        }
        
        response = index.lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['response'], 'Hello world')
        
    def test_handler_missing_prompt(self):
        event = {
            'body': json.dumps({})
        }
        response = index.lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)

    @patch.dict(os.environ, {"BEDROCK_MOCK": "true"})
    def test_handler_mock_mode(self):
        event = {
            'body': json.dumps({'prompt': 'Hi'})
        }
        response = index.lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertIn("Mock response", body['response'])

if __name__ == '__main__':
    unittest.main()
