#!/bin/bash

# Package Lambda functions for deployment
# This script creates deployment packages for each Lambda function

set -e

echo "📦 Packaging Lambda functions..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create deployment packages
echo -e "${YELLOW}Creating deployment packages...${NC}"

# Package test executor
cd lambda_functions
zip -j test_executor.zip test_executor_handler.py
echo -e "${GREEN}✅ Created test_executor.zip${NC}"

# Package API handler
zip -j api_handler.zip api_handler.py
echo -e "${GREEN}✅ Created api_handler.zip${NC}"

# Package result processor
cat > result_processor_handler.py << 'EOF'
"""
Lambda handler for processing test results
Processes results from S3 and updates metrics
"""

import json
import boto3
import os
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def process_results(event, context):
    """Process test results from S3"""
    
    # Extract S3 event
    for record in event['Records']:
        if record['eventName'].startswith('ObjectCreated'):
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            # Get object from S3
            response = s3.get_object(Bucket=bucket, Key=key)
            results = json.loads(response['Body'].read())
            
            # Extract task_id from key
            task_id = key.split('/')[1]
            
            # Process results (add your processing logic here)
            print(f"Processing results for task {task_id}")
            
            # Update test results table
            table = dynamodb.Table(os.environ['DYNAMODB_TABLE'].replace('-tasks', '-test-results'))
            
            # Store individual test results
            for test in results.get('tests', []):
                table.put_item(Item={
                    'test_id': test.get('id'),
                    'timestamp': datetime.now().isoformat(),
                    'task_id': task_id,
                    'test_type': test.get('type'),
                    'status': test.get('status'),
                    'duration': test.get('duration'),
                    'details': test
                })
    
    return {
        'statusCode': 200,
        'body': json.dumps('Results processed successfully')
    }
EOF

zip -j result_processor.zip result_processor_handler.py
rm result_processor_handler.py
echo -e "${GREEN}✅ Created result_processor.zip${NC}"

cd ..

echo -e "${GREEN}🎉 Lambda packaging complete!${NC}"
echo "Deployment packages created:"
echo "  - lambda_functions/test_executor.zip"
echo "  - lambda_functions/api_handler.zip"
echo "  - lambda_functions/result_processor.zip"