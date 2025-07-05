"""
Lambda handler for API Gateway requests
Handles REST API endpoints for AutoPlayTest
"""

import json
import os
import boto3
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

# AWS clients
dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')

# Environment variables
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
TEST_EXECUTOR_FUNCTION = os.environ['TEST_EXECUTOR_FUNCTION']
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')


def decimal_default(obj):
    """JSON encoder for Decimal types"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def handle_api(event, context):
    """
    Main Lambda handler for API Gateway requests
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    print(f"Received event: {json.dumps(event)}")
    
    # Extract HTTP method and path
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')
    
    # Route to appropriate handler
    if path == '/health':
        return handle_health_check()
    elif path == '/tests/run' and http_method == 'POST':
        return handle_run_tests(event)
    elif path == '/tests/generate' and http_method == 'POST':
        return handle_generate_tests(event)
    elif path == '/tests' and http_method == 'GET':
        return handle_list_tests(event)
    elif path.startswith('/tests/') and http_method == 'GET':
        task_id = path.split('/')[-1]
        return handle_get_test(task_id)
    elif path.startswith('/tests/') and http_method == 'DELETE':
        task_id = path.split('/')[-1]
        return handle_delete_test(task_id)
    else:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Not found'})
        }


def handle_health_check():
    """Handle health check endpoint"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'healthy',
            'environment': ENVIRONMENT,
            'timestamp': datetime.now().isoformat(),
            'ai_providers': {
                'claude': bool(os.environ.get('ANTHROPIC_API_KEY')),
                'gpt': bool(os.environ.get('OPENAI_API_KEY')),
                'gemini': bool(os.environ.get('GOOGLE_API_KEY'))
            }
        })
    }


def handle_run_tests(event):
    """Handle POST /tests/run"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Validate required fields
        if not body.get('url'):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'URL is required'})
            }
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Create task in DynamoDB
        table = dynamodb.Table(DYNAMODB_TABLE)
        task_item = {
            'task_id': task_id,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'user_id': event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'anonymous'),
            'request': body,
            'ttl': int((datetime.now() + timedelta(days=7)).timestamp())  # Auto-delete after 7 days
        }
        table.put_item(Item=task_item)
        
        # Invoke test executor Lambda asynchronously
        lambda_client.invoke(
            FunctionName=TEST_EXECUTOR_FUNCTION,
            InvocationType='Event',  # Async invocation
            Payload=json.dumps({
                'task_id': task_id,
                **body
            })
        )
        
        return {
            'statusCode': 202,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'task_id': task_id,
                'status': 'pending',
                'message': 'Test execution started',
                'created_at': task_item['created_at']
            })
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    except Exception as e:
        print(f"Error handling run tests: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }


def handle_generate_tests(event):
    """Handle POST /tests/generate"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # For Lambda, we'll invoke the same executor but with a generate flag
        task_id = str(uuid.uuid4())
        
        # Create task
        table = dynamodb.Table(DYNAMODB_TABLE)
        task_item = {
            'task_id': task_id,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'user_id': event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'anonymous'),
            'request': body,
            'operation': 'generate',
            'ttl': int((datetime.now() + timedelta(days=1)).timestamp())
        }
        table.put_item(Item=task_item)
        
        # Invoke with generate flag
        lambda_client.invoke(
            FunctionName=TEST_EXECUTOR_FUNCTION,
            InvocationType='Event',
            Payload=json.dumps({
                'task_id': task_id,
                'operation': 'generate',
                **body
            })
        )
        
        return {
            'statusCode': 202,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'task_id': task_id,
                'status': 'pending',
                'message': 'Test generation started'
            })
        }
        
    except Exception as e:
        print(f"Error handling generate tests: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }


def handle_list_tests(event):
    """Handle GET /tests"""
    try:
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        status_filter = query_params.get('status')
        limit = int(query_params.get('limit', '100'))
        
        table = dynamodb.Table(DYNAMODB_TABLE)
        
        # Query based on status if provided
        if status_filter:
            response = table.query(
                IndexName='status-created_at-index',
                KeyConditionExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': status_filter},
                Limit=limit,
                ScanIndexForward=False  # Newest first
            )
        else:
            # Scan all items (less efficient)
            response = table.scan(Limit=limit)
        
        items = response.get('Items', [])
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'tasks': items,
                'count': len(items),
                'limit': limit
            }, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error listing tests: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }


def handle_get_test(task_id):
    """Handle GET /tests/{id}"""
    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        response = table.get_item(Key={'task_id': task_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Task not found'})
            }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response['Item'], default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error getting test: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }


def handle_delete_test(task_id):
    """Handle DELETE /tests/{id}"""
    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        
        # Check if task exists and is cancellable
        response = table.get_item(Key={'task_id': task_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Task not found'})
            }
        
        task = response['Item']
        if task['status'] not in ['pending', 'running']:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f"Cannot cancel task in {task['status']} status"})
            }
        
        # Update status to cancelled
        table.update_item(
            Key={'task_id': task_id},
            UpdateExpression='SET #status = :status, completed_at = :completed_at',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'cancelled',
                ':completed_at': datetime.now().isoformat()
            }
        )
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'task_id': task_id,
                'status': 'cancelled',
                'message': 'Task cancelled successfully'
            })
        }
        
    except Exception as e:
        print(f"Error deleting test: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }