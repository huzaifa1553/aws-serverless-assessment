import json
import boto3
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Bedrock client
bedrock_runtime = boto3.client('bedrock-runtime')

def lambda_handler(event, context):
    """
    AWS Lambda handler for Bedrock Inference.
    Expects a Function URL event with a JSON body containing 'prompt'.
    Model: amazon.nova-lite-v1:0
    """
    logger.info("Received event: %s", json.dumps(event))
    
    try:
        # Parse body
        body_str = event.get('body', '{}')
        if not body_str:
             body_str = '{}'
        
        # Handle base64 encoding
        if event.get('isBase64Encoded', False):
            import base64
            body_str = base64.b64decode(body_str).decode('utf-8')
            
        body = json.loads(body_str)
        prompt = body.get('prompt', '')

        if not prompt:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing "prompt" in request body'})
            }

        # Check for Mock Mode
        if os.environ.get('BEDROCK_MOCK', 'false').lower() == 'true':
           logger.info("Mock mode enabled.")
           return {
               'statusCode': 200,
               'headers': {'Content-Type': 'application/json'},
               'body': json.dumps({
                   'response': f"Mock response to: {prompt}",
                   'model': 'mock-model'
               })
           }

        # Call Bedrock
        model_id = 'amazon.nova-lite-v1:0'
        logger.info(f"Invoking Bedrock model: {model_id}")

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }

        response = bedrock_runtime.invoke_model(
            body=json.dumps(payload),
            modelId=model_id,
            accept='application/json',
            contentType='application/json'
        )
        
        response_body = json.loads(response.get('body').read())
        output_text = response_body.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'response': output_text,
                'model': model_id
            })
        }

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'attempted_model_id': locals().get('model_id', 'unknown')
            })
        }
