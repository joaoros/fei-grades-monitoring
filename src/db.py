
"""
DynamoDB database access module for grade management.
"""
import os
import boto3
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def _get_table_name() -> str:
    """Gets the DynamoDB table name from environment variables."""
    return os.environ["GRADES_TABLE"]

def _get_table():
    """Returns the DynamoDB table object."""
    logger.info("Connecting to DynamoDB table.")
    dynamodb = boto3.resource('dynamodb')
    table_name = _get_table_name()
    logger.info(f"Using table: {table_name}")
    return dynamodb.Table(table_name)

def get_all_grades() -> List[Dict[str, Any]]:
    """Fetches all grades stored in the table."""
    logger.info("Fetching all grades from the table.")
    table = _get_table()
    response = table.scan()
    return response.get('Items', [])

def get_grade_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Fetches a specific grade by subject name."""
    logger.info(f"Fetching grade for subject: {name}")
    table = _get_table()
    response = table.get_item(Key={'nome': name})
    return response.get('Item')

def store_changed_grades(new_grades: List[Dict[str, Any]], old_grades: List[Dict[str, Any]]) -> List[Tuple[Optional[Dict[str, Any]], Dict[str, Any]]]:
    """Stores only grades that have changed, returning the changes."""
    logger.info("Storing only changed grades by subject name.")
    table = _get_table()
    changed = []
    old_grades_dict = {g['nome']: g for g in old_grades}
    for grade in new_grades:
        name = grade['nome']
        if old_grades_dict.get(name) != grade:
            item = {
                'nome': name,
                'notas': grade['notas'],
                'media': grade['media']
            }
            table.put_item(Item=item)
            changed.append((old_grades_dict.get(name), grade))
    return changed