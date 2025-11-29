import boto3
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class DynamoDBClient:
    """DynamoDB client for tracking investigation timestamps per service"""
    
    def __init__(self, enabled: bool = False, region: str = "us-east-1"):
        self.enabled = enabled
        self.table_name = "sre-investigation-tracker"
        self.dynamodb = None
        self.table = None
        
        if not self.enabled:
            logger.info("DynamoDB tracking disabled")
            return
        
        try:
            self.dynamodb = boto3.resource('dynamodb', region_name=region)
            self._ensure_table_exists()
            self.table = self.dynamodb.Table(self.table_name)
            logger.info(f"DynamoDB client initialized: table={self.table_name}, region={region}")
        except Exception as e:
            logger.warning(f"DynamoDB initialization failed: {e}. Continuing without tracking.")
            self.enabled = False
    
    def _ensure_table_exists(self):
        """Create table if it doesn't exist"""
        try:
            existing_tables = list(self.dynamodb.tables.all())
            table_names = [t.name for t in existing_tables]
            
            if self.table_name in table_names:
                logger.debug(f"Table {self.table_name} already exists")
                return
            
            logger.info(f"Creating DynamoDB table: {self.table_name}")
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': 'service', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'service', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            table.wait_until_exists()
            logger.info(f"Table {self.table_name} created successfully")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                logger.debug(f"Table {self.table_name} already exists")
            else:
                raise
    
    def get_last_investigation_time(self, service: str) -> Optional[str]:
        """Get last investigation timestamp for a service (ISO format)"""
        if not self.enabled or not self.table:
            return None
        
        try:
            response = self.table.get_item(Key={'service': service})
            
            if 'Item' in response:
                last_time = response['Item'].get('last_investigation_time')
                logger.info(f"[{service}] Last investigation: {last_time}")
                return last_time
            
            logger.info(f"[{service}] No previous investigation found")
            return None
        except Exception as e:
            logger.warning(f"Failed to get last investigation time for {service}: {e}")
            return None
    
    def update_investigation_time(self, service: str, timestamp: str, incident_id: str) -> bool:
        """Update last investigation timestamp for a service"""
        if not self.enabled or not self.table:
            return False
        
        try:
            self.table.put_item(
                Item={
                    'service': service,
                    'last_investigation_time': timestamp,
                    'last_incident_id': incident_id,
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }
            )
            logger.info(f"[{service}] Updated investigation time: {timestamp}, incident: {incident_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update investigation time for {service}: {e}")
            return False
