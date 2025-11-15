"""
Trellis MCP Server - Main entry point using FastMCP.

This server provides tools for Claude Desktop to manipulate Trellis Workflows
through natural language commands.
"""

import logging
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from .trellis_client import TrellisClient


# Configure file-based logging
def setup_logging():
    """Set up file-based logging for the MCP server."""
    log_dir = Path.home() / ".trellis_mcp"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "server.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
        ]
    )
    
    logger = logging.getLogger("trellis_mcp")
    logger.info("Trellis MCP Server starting...")
    return logger


logger = setup_logging()

# Create FastMCP instance
mcp = FastMCP("trellis-workflows")

# Initialize Trellis client
client = TrellisClient()


# ===== Transformation Tools =====

@mcp.tool()
def get_transformations() -> dict:
    """
    Get all transformations in the Trellis project.
    
    Transformations are extraction schemas that define how to extract data
    from documents. Each transformation has operations that specify what
    data to extract and how.
    
    Use this tool to discover available transformations before referencing
    them in workflow actions.
    
    Returns:
        dict: API response containing list of transformations with:
            - id: Transformation ID (use this to reference in workflows)
            - name: Human-readable name
            - description: What the transformation does
            - params: Operations/schema details (if included)
            - Other metadata
    """
    logger.info("Tool called: get_transformations")
    try:
        result = client.get_transformations()
        logger.info("Successfully retrieved transformations")
        return result
    except Exception as e:
        logger.error(f"Failed to get transformations: {e}")
        raise


@mcp.tool()
def get_transformation_details(transform_id: str) -> dict:
    """
    Get detailed operations/schema for a specific transformation.
    
    Use this to understand what a transformation extracts and how it's
    configured. This is helpful when you need to understand what outputs
    a transformation will produce.
    
    Args:
        transform_id: The ID of the transformation to get details for
    
    Returns:
        dict: API response containing transformation operations and schema
            details. The structure includes information about what data
            the transformation extracts and how.
    """
    logger.info(f"Tool called: get_transformation_details(transform_id={transform_id})")
    try:
        result = client.get_transformation_operations(transform_id)
        logger.info(f"Successfully retrieved details for transform {transform_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to get transformation details: {e}")
        raise


# ===== Entity Tools =====

@mcp.tool()
def get_entities() -> dict:
    """
    Get all entities in the Trellis project.
    
    Entities are data tables that store extracted information. Each entity
    has fields (columns) that define what data it holds. Entities can be
    related to each other in a hierarchical structure (parent-child
    relationships).
    
    Use this tool to discover available entities before referencing them
    in workflow triggers or actions.
    
    Returns:
        dict: API response containing list of entities with:
            - id: Entity ID (use this to reference in workflows)
            - name: Human-readable name
            - entity_type: Type of entity (e.g., "inbox", "custom")
            - tags: Entity tags/categories
            - Other metadata
    """
    logger.info("Tool called: get_entities")
    try:
        result = client.get_entities()
        logger.info("Successfully retrieved entities")
        return result
    except Exception as e:
        logger.error(f"Failed to get entities: {e}")
        raise


@mcp.tool()
def get_entity_fields(entity_id: str) -> dict:
    """
    Get fields (columns) for a specific entity.
    
    Use this to understand what fields an entity has, which is essential
    when:
    - Mapping transformation outputs to entity fields
    - Understanding entity structure
    - Working with child entities (look for row_relation type fields)
    
    Args:
        entity_id: The ID of the entity to get fields for
    
    Returns:
        dict: API response containing entity fields information with:
            - Field names
            - Field types (text, number, row_relation, etc.)
            - Field IDs
            - Other field metadata
    """
    logger.info(f"Tool called: get_entity_fields(entity_id={entity_id})")
    try:
        result = client.get_entity_fields(entity_id)
        logger.info(f"Successfully retrieved fields for entity {entity_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to get entity fields: {e}")
        raise


# ===== Workflow Tools =====

@mcp.tool()
def get_workflow_config() -> dict:
    """
    Get the current workflow configuration including all blocks and edges.
    
    Use this tool to see what blocks already exist in the workflow before
    making changes. This helps you understand the current state and avoid
    duplicating blocks.
    
    Returns:
        dict: API response containing workflow configuration with:
            - id: Workflow ID
            - name: Workflow name
            - is_active: Whether workflow is enabled
            - nodes: List of blocks in the workflow
            - edges: Connections between blocks
            - Other metadata
    """
    logger.info("Tool called: get_workflow_config")
    try:
        result = client.get_workflow_config()
        logger.info("Successfully retrieved workflow config")
        return result
    except Exception as e:
        logger.error(f"Failed to get workflow config: {e}")
        raise


@mcp.tool()
def update_workflow_blocks(
    blocks: list[dict],
    deleted_block_ids: list[str] | None = None
) -> dict:
    """
    Update workflow blocks - create new blocks, update existing ones, or delete blocks.
    
    This is the primary tool for building workflows. The workflow_id is automatically
    injected by the client - DO NOT include it in blocks.
    
    IMPORTANT: When creating a NEW block, you MUST provide a unique 'id' field.
    This can be any string like "my_trigger_001" or "patient_action_block".
    
    Args:
        blocks: List of block objects to create or update. Each block needs:
            
            ==== FOR CREATING NEW BLOCKS ====
            Required fields:
            - id: (str) A unique identifier you create (e.g., "new_trigger_123")
            - name: (str) Human-readable name for the block
            - type: (str) Either "trigger" or "action"
            - position: (dict) Visual position with {"x": int, "y": int}
            
            For TRIGGER blocks, also include:
            - trigger: (dict) with:
                - event_name: (str) Event to watch for, e.g., "new_asset"
                - entity_id: (str) The entity ID to watch (get from get_entities())
            
            For ACTION blocks, also include:
            - action: (dict) with:
                - name: (str) Action type, e.g., "run_transformation", "create_record"
                - entity_id: (str) Entity to act on (if applicable)
                - transform_id: (str) Transformation to run (if action is run_transformation)
                - mapping_config: (dict) Field mapping (if action is create_record/update_entity)
            
            Example NEW trigger block:
            {
                "id": "referral_trigger_001",
                "name": "Watch for New Referrals",
                "type": "trigger",
                "position": {"x": 100, "y": 100},
                "trigger": {
                    "event_name": "new_asset",
                    "entity_id": "entity_35Gos7u7s4FtuKX9cZGRBzQDNG6"
                }
            }
            
            Example NEW action block:
            {
                "id": "extract_patient_001",
                "name": "Extract Patient Data",
                "type": "action",
                "position": {"x": 300, "y": 100},
                "action": {
                    "name": "run_transformation",
                    "transform_id": "transform_abc123"
                }
            }
            
            ==== FOR UPDATING EXISTING BLOCKS ====
            Required fields:
            - id: (str) The existing block's ID from get_workflow_config() (starts with "wblock_")
            
            Optional fields (only include what you want to change):
            - name: (str) New name
            - position: (dict) New position
            - Any other fields to update
            
            Example UPDATE:
            {
                "id": "wblock_35WmLblUNPVyNomrenTbffqTtLg",
                "name": "Updated Trigger Name",
                "position": {"x": 200, "y": 150}
            }
        
        deleted_block_ids: Optional list of block IDs to delete. Use the full
            block IDs from get_workflow_config() (e.g., ["wblock_abc123", "wblock_def456"])
    
    Returns:
        dict: API response confirming the update with workflow_id
    """
    logger.info(f"Tool called: update_workflow_blocks(blocks={len(blocks)}, deleted_block_ids={deleted_block_ids})")
    try:
        result = client.update_workflow_blocks(
            blocks=blocks,
            deleted_block_ids=deleted_block_ids
        )
        logger.info("Successfully updated workflow blocks")
        return result
    except Exception as e:
        logger.error(f"Failed to update workflow blocks: {e}")
        raise

def run():
    mcp.run()

# Entry point
if __name__ == "__main__":
    run()