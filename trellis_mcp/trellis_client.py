"""
Trellis API Client - HTTP wrapper for Trellis API endpoints.

Handles authentication, request/response formatting, and error handling
for all Trellis API operations.
"""

import os
import logging
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("trellis_mcp.client")



class TrellisClient:
    """HTTP client for interacting with the Trellis API."""
    
    # API constants
    API_VERSION = "2025-03"
    BASE_URL = "https://enterprise.training.api.runtrellis.com/v1"
    
    def __init__(self):
        """
        Initialize the Trellis API client.
        
        Loads configuration from environment variables:
        - TRELLIS_API_KEY: API authentication token
        - TRELLIS_WORKFLOW_ID: ID of the workflow to manipulate
        - TRELLIS_PROJECT_ID: ID of the project to work with
        """
        self.api_key = os.getenv("TRELLIS_API_KEY")
        self.workflow_id = os.getenv("TRELLIS_WORKFLOW_ID")
        self.project_id = os.getenv("TRELLIS_PROJECT_ID")
        
        if not self.api_key:
            raise ValueError("TRELLIS_API_KEY environment variable is required")
        if not self.workflow_id:
            raise ValueError("TRELLIS_WORKFLOW_ID environment variable is required")
        if not self.project_id:
            raise ValueError("TRELLIS_PROJECT_ID environment variable is required")
        
        logger.info(f"Initialized TrellisClient for project {self.project_id}")
        logger.info(f"Target workflow: {self.workflow_id}")
    
    def _get_headers(self) -> dict:
        """Build request headers with authentication and API version."""
        return {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "API-Version": self.API_VERSION,
        }
    
    def _request(
        self,
        method: str,
        endpoint: str,
        timeout: int = 30,
        **kwargs
    ) -> dict:
        """
        Make an HTTP request to the Trellis API.
        
        Args:
            method: HTTP method (GET, POST, PATCH, etc.)
            endpoint: API endpoint path (e.g., "/transforms")
            timeout: Request timeout in seconds (default: 30)
            **kwargs: Additional arguments to pass to requests.request()
        
        Returns:
            Full response JSON as dict
        
        Raises:
            requests.exceptions.RequestException: On network or HTTP errors
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers()
        
        # Merge custom headers if provided
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        
        logger.debug(f"{method} {url}")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=timeout,
                **kwargs
            )
            
            # Log response status
            logger.debug(f"Response status: {response.status_code}")
            
            # Raise for HTTP errors (4xx, 5xx)
            response.raise_for_status()
            
            # Return full response JSON
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            # Log the error with response body if available
            error_detail = ""
            try:
                error_body = e.response.json()
                error_detail = f" - {error_body}"
            except Exception:
                error_detail = f" - {e.response.text[:200]}"
            
            logger.error(f"HTTP error: {e}{error_detail}")
            raise
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout after {timeout}s: {e}")
            raise
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    # ===== Transformation Endpoints =====
    
    def get_transformations(self) -> dict:
        """
        Get all transformations in the project.
        
        Returns:
            Full API response containing transformation list
        """
        logger.info("Fetching transformations")
        return self._request(
            "GET",
            "/transforms",
            params={
                "proj_ids": [self.project_id],
                "include_transform_params": True,
            }
        )
    
    def get_transformation_operations(self, transform_id: str) -> dict:
        """
        Get detailed operations for a specific transformation.
        
        Args:
            transform_id: ID of the transformation
        
        Returns:
            Full API response containing transformation operations
        """
        logger.info(f"Fetching operations for transform {transform_id}")
        return self._request(
            "GET",
            f"/transforms/{transform_id}/operations"
        )
    
    # ===== Entity Endpoints =====
    
    def get_entities(self) -> dict:
        """
        Get all entities in the project.
        
        Returns:
            Full API response containing entity list
        """
        logger.info("Fetching entities")
        return self._request(
            "GET",
            "/entities",
            params={"project_id": self.project_id}
        )
    
    def get_entity_fields(self, entity_id: str) -> dict:
        """
        Get fields for a specific entity.
        
        Args:
            entity_id: ID of the entity
        
        Returns:
            Full API response containing entity fields
        """
        logger.info(f"Fetching fields for entity {entity_id}")
        return self._request(
            "GET",
            f"/entities/{entity_id}/fields"
        )
    
    # ===== Workflow Endpoints =====
    
    def get_workflow_config(self) -> dict:
        """
        Get the current workflow configuration including all blocks.
        
        Uses the workflow_id from environment variables.
        
        Returns:
            Full API response containing workflow configuration
        """
        logger.info(f"Fetching config for workflow {self.workflow_id}")
        return self._request(
            "GET",
            f"/workflows/{self.workflow_id}/config"
        )
    
    def update_workflow_blocks(
        self,
        blocks: list,
        deleted_block_ids: Optional[list] = None
    ) -> dict:
        """
        Update workflow blocks (create, update, or delete).
        
        Uses the workflow_id from environment variables.
        
        Args:
            blocks: List of block objects to create or update
                - Omit 'id' field to create a new block
                - Include 'id' field to update an existing block
            deleted_block_ids: Optional list of block IDs to delete
        
        Returns:
            Full API response
        
        Example:
            # Create a new trigger block
            client.update_workflow_blocks([
                {
                    "name": "New Asset Trigger",
                    "type": "trigger",
                    "position": {"x": 100, "y": 100},
                    "trigger": {
                        "event_name": "new_asset",
                        "entity_id": "entity_123"
                    }
                }
            ])
            
            # Update and delete blocks
            client.update_workflow_blocks(
                blocks=[{
                    "id": "block_123",
                    "name": "Updated name",
                    ...
                }],
                deleted_block_ids=["block_456", "block_789"]
            )
        """
        logger.info(f"Updating blocks for workflow {self.workflow_id}")
        logger.debug(f"Blocks to update: {len(blocks)}")
        if deleted_block_ids:
            logger.debug(f"Blocks to delete: {len(deleted_block_ids)}")
        
        payload = {"blocks": blocks}
        if deleted_block_ids:
            payload["deleted_block_ids"] = deleted_block_ids
        
        return self._request(
            "PATCH",
            f"/workflows/{self.workflow_id}/blocks",
            json=payload
        )