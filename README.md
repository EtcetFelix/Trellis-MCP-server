# Trellis MCP Server

An MCP (Model Context Protocol) server that enables Claude Desktop to manipulate Trellis Workflows through natural language commands. This server provides tools for managing workflow blocks, transformations, and entities in the Trellis platform.

## Overview

This MCP server allows Claude to:
- Fetch transformation schemas and understand data extraction configurations
- Fetch entity schemas and understand data storage structures
- Create, read, update, and delete workflow blocks
- Build complete workflows through natural language prompts

## Prerequisites

- Python 3.10 or higher
- Poetry (Python package manager)
- Claude Desktop application
- Access to Trellis MCP OA organization (both Claude and Trellis platforms)

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd trellis-mcp-server
```

### 2. Install Dependencies

```bash
poetry install
```

This will install all required dependencies including:
- `mcp` - Model Context Protocol framework
- `requests` - HTTP client for Trellis API
- `python-dotenv` - Environment variable management

### 3. Get Your Trellis Credentials

You'll need three pieces of information from your Trellis project:

**API Key**: Found in your project settings or provided by the Trellis team

**Project ID**: Extract from your Trellis project URL
```
https://enterprise.training.dashboard.runtrellis.com/mcp-oa/projects/proj_XXXXX
                                                                        ^^^^^^^^
```

**Workflow ID**: Create a new workflow in your project, then extract its ID from the URL
```
https://enterprise.training.dashboard.runtrellis.com/mcp-oa/projects/proj_XXXXX/workflows/wflow_XXXXX
                                                                                            ^^^^^^^^^^
```

⚠️ **Important**: Create a NEW workflow separate from the Example Workflow. The MCP server is scoped to a single workflow ID to avoid accidentally editing existing configurations.

## Configuration

### Configure Claude Desktop

Edit your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following configuration:

```json
{
  "mcpServers": {
    "trellis-workflows": {
      "command": "poetry",
      "args": ["run", "-C", "/absolute/path/to/trellis-mcp-server", "trellis-mcp"],
      "env": {
        "TRELLIS_API_KEY": "your_api_key_here",
        "TRELLIS_WORKFLOW_ID": "wflow_XXXXX",
        "TRELLIS_PROJECT_ID": "proj_XXXXX"
      }
    }
  }
}
```

**Replace**:
- `/absolute/path/to/trellis-mcp-server` with the full path to your cloned repository
- `your_api_key_here` with your Trellis API key
- `wflow_XXXXX` with your workflow ID
- `proj_XXXXX` with your project ID

### Restart Claude Desktop

After saving the configuration, completely quit and restart Claude Desktop for the changes to take effect.

## Verification

Once Claude Desktop is restarted, you should see the 🔌 icon in the bottom right corner indicating MCP servers are connected. You can verify the server is working by asking Claude:

```
"What transformations are available in my Trellis project?"
```

If successful, Claude will use the `get_transformations` tool to fetch and display your transformations.

## Available Tools

The MCP server exposes six tools that Claude can use:

### 1. `get_transformations`
Retrieves all transformation schemas in the project. Transformations define how to extract data from documents.

### 2. `get_transformation_details`
Gets detailed operations/schema for a specific transformation, including what data it extracts and how.

### 3. `get_entities`
Retrieves all entities (data tables) in the project. Entities store extracted information.

### 4. `get_entity_fields`
Gets fields (columns) for a specific entity, including field types and relationships.

### 5. `get_workflow_config`
Retrieves the current workflow configuration including all blocks and their connections.

### 6. `update_workflow_blocks`
Creates, updates, or deletes workflow blocks. This is the primary tool for building workflows.

## Architecture

### Project Structure

```
trellis-mcp-server/
├── trellis_mcp/
│   ├── __init__.py          # Package initialization
│   ├── server.py            # MCP server with FastMCP (main entry point)
│   └── trellis_client.py    # HTTP client for Trellis API
├── pyproject.toml           # Poetry dependencies and project config
└── README.md                # This file
```

### How It Works

1. **FastMCP Framework**: The server uses FastMCP to handle MCP protocol communication with Claude Desktop.

2. **Tool Registration**: Six tools are registered as MCP tools using the `@mcp.tool()` decorator.

3. **Trellis API Client**: The `TrellisClient` class wraps all HTTP communication with the Trellis API, handling:
   - Authentication via API key
   - Request formatting with proper headers
   - Error handling and logging
   - Response parsing

4. **Logging**: All operations are logged to `~/.trellis_mcp/server.log` for debugging.

5. **Scoping**: The server is scoped to a single project and workflow ID via environment variables, preventing accidental edits to other workflows.

## Troubleshooting

### Server Not Connecting

1. Check that Claude Desktop is completely restarted
2. Verify the path to your repository is absolute and correct
3. Check environment variables are set correctly
4. Look at logs: `~/.trellis_mcp/server.log` (macOS/Linux) or `%USERPROFILE%\.trellis_mcp\server.log` (Windows)

### Authentication Errors

- Verify your `TRELLIS_API_KEY` is correct
- Ensure you have access to the MCP OA organization in Trellis
- Check that your API key hasn't expired

### Workflow Not Updating

- Confirm the `TRELLIS_WORKFLOW_ID` matches your target workflow
- Verify you're not trying to edit the Example Workflow (use a new workflow)
- Check the Trellis dashboard to see if changes are appearing

### Tool Calls Failing

- Run `get_workflow_config` first to understand current state
- Ensure entity and transformation IDs are correct
- Check logs for detailed error messages

## API Reference

### Trellis API Version

This server uses API version `2025-03` with the following base URL:
```
https://enterprise.training.api.runtrellis.com/v1
```

### Key Endpoints Used

- `GET /transforms` - List transformations
- `GET /transforms/{id}/operations` - Get transformation details
- `GET /entities` - List entities
- `GET /entities/{id}/fields` - Get entity fields
- `GET /workflows/{id}/config` - Get workflow configuration
- `PATCH /workflows/{id}/blocks` - Update workflow blocks

## Security Notes

- API keys are stored in Claude Desktop's configuration file
- The server is scoped to a single workflow ID to prevent accidental edits
- Never commit your `.env` file or expose API keys

## Limitations

- Scoped to a single project and workflow (by design)
- Only supports "Row Created" triggers (per assignment requirements)
- Does not support "Row Updated" or "Email Received" triggers
- Cannot edit transformations or entities (read-only access)
