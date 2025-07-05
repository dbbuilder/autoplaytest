"""
Lambda handler for test execution
Executes AutoPlayTest test suites in AWS Lambda environment
"""

import json
import os
import sys
import traceback
import asyncio
from datetime import datetime
import boto3
import uuid

# Add the package to path
sys.path.insert(0, '/opt/python')
sys.path.insert(0, '/var/task')

# Import after path setup
from src.simple_runner import run_test_suite
from src.core.engine.main_engine import TestConfiguration

# AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
sqs = boto3.client('sqs')

# Environment variables
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
S3_BUCKET = os.environ['S3_BUCKET']
SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')

# Get API keys from environment (injected from Secrets Manager)
os.environ['ANTHROPIC_API_KEY'] = os.environ.get('ANTHROPIC_API_KEY', '')
os.environ['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', '')
os.environ['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY', '')


def execute_test(event, context):
    """
    Lambda handler for test execution
    
    Args:
        event: Lambda event containing test configuration
        context: Lambda context
        
    Returns:
        Response with test results or error
    """
    print(f"Received event: {json.dumps(event)}")
    
    # Extract parameters
    task_id = event.get('task_id', str(uuid.uuid4()))
    url = event.get('url')
    username = event.get('username')
    password = event.get('password')
    test_types = event.get('test_types', ['login', 'navigation'])
    browser = event.get('browser', 'chromium')
    headless = event.get('headless', True)
    timeout = event.get('timeout', 30000)
    
    if not url:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'URL is required'})
        }
    
    # Update task status in DynamoDB
    table = dynamodb.Table(DYNAMODB_TABLE)
    table.update_item(
        Key={'task_id': task_id},
        UpdateExpression='SET #status = :status, started_at = :started_at',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': 'running',
            ':started_at': datetime.now().isoformat()
        }
    )
    
    try:
        # Run the test suite
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        results = loop.run_until_complete(
            run_test_suite(
                url=url,
                username=username,
                password=password,
                test_types=test_types,
                browser=browser,
                headless=headless,
                timeout=timeout
            )
        )
        
        # Store results in S3
        result_key = f"test-results/{task_id}/results.json"
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=result_key,
            Body=json.dumps(results, indent=2),
            ContentType='application/json'
        )
        
        # Update task status
        table.update_item(
            Key={'task_id': task_id},
            UpdateExpression='SET #status = :status, completed_at = :completed_at, result_s3_key = :s3_key, summary = :summary',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'completed',
                ':completed_at': datetime.now().isoformat(),
                ':s3_key': result_key,
                ':summary': {
                    'total_tests': results.get('total_tests', 0),
                    'passed': results.get('passed', 0),
                    'failed': results.get('failed', 0),
                    'duration': results.get('duration', 0)
                }
            }
        )
        
        # Send result to SQS for processing
        if SQS_QUEUE_URL:
            sqs.send_message(
                QueueUrl=SQS_QUEUE_URL,
                MessageBody=json.dumps({
                    'task_id': task_id,
                    'status': 'completed',
                    'result_s3_key': result_key
                })
            )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'task_id': task_id,
                'status': 'completed',
                'results': results
            })
        }
        
    except Exception as e:
        error_message = str(e)
        error_trace = traceback.format_exc()
        
        print(f"Error executing test: {error_message}")
        print(f"Traceback: {error_trace}")
        
        # Update task status with error
        table.update_item(
            Key={'task_id': task_id},
            UpdateExpression='SET #status = :status, completed_at = :completed_at, error = :error',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'failed',
                ':completed_at': datetime.now().isoformat(),
                ':error': {
                    'message': error_message,
                    'trace': error_trace
                }
            }
        )
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'task_id': task_id,
                'status': 'failed',
                'error': error_message
            })
        }
    finally:
        if 'loop' in locals() and loop:
            loop.close()