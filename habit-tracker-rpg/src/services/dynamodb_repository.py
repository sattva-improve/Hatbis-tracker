"""DynamoDB repository base class."""
import os
from typing import Any, Dict, List, Optional
from datetime import datetime, date
import boto3
from boto3.dynamodb.conditions import Key, Attr


class DynamoDBRepository:
    """Base repository for DynamoDB operations."""
    
    def __init__(self, table_name: str):
        """Initialize repository with table name."""
        self.table_name = table_name
        self._table = None
    
    @property
    def table(self):
        """Get DynamoDB table resource (lazy loading)."""
        if self._table is None:
            endpoint_url = os.environ.get("DYNAMODB_ENDPOINT_URL")
            if endpoint_url:
                dynamodb = boto3.resource("dynamodb", endpoint_url=endpoint_url)
            else:
                dynamodb = boto3.resource("dynamodb")
            self._table = dynamodb.Table(self.table_name)
        return self._table
    
    def _serialize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize item for DynamoDB."""
        serialized = {}
        for key, value in item.items():
            if value is None:
                continue
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, date):
                serialized[key] = value.isoformat()
            elif isinstance(value, dict):
                serialized[key] = self._serialize_item(value)
            elif isinstance(value, list):
                serialized[key] = [
                    self._serialize_item(v) if isinstance(v, dict) else v
                    for v in value
                ]
            else:
                serialized[key] = value
        return serialized
    
    def put_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Put item into table."""
        serialized = self._serialize_item(item)
        self.table.put_item(Item=serialized)
        return serialized
    
    def get_item(self, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get item by key."""
        response = self.table.get_item(Key=key)
        return response.get("Item")
    
    def update_item(
        self,
        key: Dict[str, Any],
        updates: Dict[str, Any],
        condition: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update item with given updates."""
        if not updates:
            return self.get_item(key)
        
        # Build update expression
        update_parts = []
        expression_names = {}
        expression_values = {}
        
        for i, (field, value) in enumerate(updates.items()):
            if value is None:
                continue
            
            attr_name = f"#attr{i}"
            attr_value = f":val{i}"
            
            update_parts.append(f"{attr_name} = {attr_value}")
            expression_names[attr_name] = field
            
            if isinstance(value, datetime):
                expression_values[attr_value] = value.isoformat()
            elif isinstance(value, date):
                expression_values[attr_value] = value.isoformat()
            elif isinstance(value, dict):
                expression_values[attr_value] = self._serialize_item(value)
            else:
                expression_values[attr_value] = value
        
        if not update_parts:
            return self.get_item(key)
        
        update_expression = "SET " + ", ".join(update_parts)
        
        kwargs = {
            "Key": key,
            "UpdateExpression": update_expression,
            "ExpressionAttributeNames": expression_names,
            "ExpressionAttributeValues": expression_values,
            "ReturnValues": "ALL_NEW",
        }
        
        if condition:
            kwargs["ConditionExpression"] = condition
        
        try:
            response = self.table.update_item(**kwargs)
            return response.get("Attributes")
        except self.table.meta.client.exceptions.ConditionalCheckFailedException:
            return None
    
    def delete_item(self, key: Dict[str, Any]) -> bool:
        """Delete item by key."""
        try:
            self.table.delete_item(Key=key)
            return True
        except Exception:
            return False
    
    def query(
        self,
        key_condition: Any,
        filter_expression: Optional[Any] = None,
        index_name: Optional[str] = None,
        limit: Optional[int] = None,
        scan_forward: bool = True,
    ) -> List[Dict[str, Any]]:
        """Query items."""
        kwargs = {
            "KeyConditionExpression": key_condition,
            "ScanIndexForward": scan_forward,
        }
        
        if filter_expression is not None:
            kwargs["FilterExpression"] = filter_expression
        
        if index_name:
            kwargs["IndexName"] = index_name
        
        if limit:
            kwargs["Limit"] = limit
        
        items = []
        response = self.table.query(**kwargs)
        items.extend(response.get("Items", []))
        
        # Handle pagination
        while "LastEvaluatedKey" in response and (limit is None or len(items) < limit):
            kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
            response = self.table.query(**kwargs)
            items.extend(response.get("Items", []))
        
        return items[:limit] if limit else items
    
    def scan(
        self,
        filter_expression: Optional[Any] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Scan table."""
        kwargs = {}
        
        if filter_expression is not None:
            kwargs["FilterExpression"] = filter_expression
        
        if limit:
            kwargs["Limit"] = limit
        
        items = []
        response = self.table.scan(**kwargs)
        items.extend(response.get("Items", []))
        
        # Handle pagination
        while "LastEvaluatedKey" in response and (limit is None or len(items) < limit):
            kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
            response = self.table.scan(**kwargs)
            items.extend(response.get("Items", []))
        
        return items[:limit] if limit else items
