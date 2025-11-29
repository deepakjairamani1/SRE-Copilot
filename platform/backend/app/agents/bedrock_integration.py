import os
import json
import httpx

async def call_bedrock(prompt: str, model: str) -> tuple[str, int]:
    """Call AWS Bedrock Claude API with 40000 max tokens"""
    import boto3
    
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 40000,
        "temperature": 0.3,
        "messages": [{"role": "user", "content": prompt}]
    })
    
    response = bedrock.invoke_model(
        modelId=model,
        body=body
    )
    
    response_body = json.loads(response['body'].read())
    response_text = response_body['content'][0]['text']
    tokens_used = response_body['usage']['input_tokens'] + response_body['usage']['output_tokens']
    
    return response_text, tokens_used