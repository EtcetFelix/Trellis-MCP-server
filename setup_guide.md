# Trellis MCP Server - Setup Guide

This guide walks you through setting up the Trellis MCP Server from scratch.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Getting Your Trellis Credentials](#getting-your-trellis-credentials)
4. [Configuring Claude Desktop](#configuring-claude-desktop)
5. [Testing Your Setup](#testing-your-setup)
6. [Next Steps](#next-steps)

## Prerequisites

### 1. Python 3.10+

Check your Python version:
```bash
python --version
```

If you need to install Python, visit https://www.python.org/downloads/

### 2. Poetry

Install Poetry (Python package manager):

**macOS/Linux**:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Windows (PowerShell)**:
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

Verify installation:
```bash
poetry --version
```

### 3. Claude Desktop

Download from: https://claude.ai/download

### 4. Trellis Access

Ensure you have:
- ✅ Access to the MCP OA organization in Claude
- ✅ Access to the MCP OA organization in Trellis

If you don't have access, contact founders@runtrellis.com

## Initial Setup

### Step 1: Clone the Repository

```bash
cd ~/Code  # Or your preferred directory
git clone <your-repo-url>
cd trellis-mcp-server
```

### Step 2: Install Dependencies

```bash
poetry install
```

This installs:
- `mcp` - Model Context Protocol framework
- `requests` - HTTP client library
- `python-dotenv` - Environment variable management

You should see output like:
```
Installing dependencies from lock file
...
Installing the current project: trellis-mcp (0.1.0)
```

### Step 3: Verify Installation

```bash
poetry run python -c "import mcp; print('MCP installed successfully')"
```

## Getting Your Trellis Credentials

You need three pieces of information to configure the server.

### 1. Get Your API Key

Your API key should have been provided by the Trellis team. It looks like:
```
Bearer trellis_xxxxxxxxxxxxxxxxxxxxx
```

💡 **Tip**: Check your email or the project documentation file.

### 2. Get Your Project ID

1. Log into Trellis: https://enterprise.training.dashboard.runtrellis.com/mcp-oa
2. Navigate to your project
3. Copy the Project ID from the URL:

```
https://enterprise.training.dashboard.runtrellis.com/mcp-oa/projects/proj_35GnIQ94TycwKhM9h2OuKGZz9f7
                                                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                                                        This is your PROJECT_ID
```

### 3. Create a New Workflow

⚠️ **Important**: Do NOT use the Example Workflow. Create a new one:

1. Go to Workflows in your Trellis project:
   ```
   https://enterprise.training.dashboard.runtrellis.com/mcp-oa/projects/YOUR_PROJECT_ID/workflows
   ```

2. Click "Create Workflow" or the "+" button

3. Name it something like "MCP Test Workflow"

4. Copy the Workflow ID from the URL:
   ```
   https://enterprise.training.dashboard.runtrellis.com/.../workflows/wflow_35Gv32Yf2rmNScDPohoJUS7qZ1X
                                                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                                                       This is your WORKFLOW_ID
   ```

### Summary Checklist

Before proceeding, ensure you have:
- [ ] API Key (starts with `Bearer trellis_`)
- [ ] Project ID (starts with `proj_`)
- [ ] Workflow ID (starts with `wflow_`)

## Configuring Claude Desktop

### Step 1: Locate Configuration File

**macOS**:
```bash
open ~/Library/Application\ Support/Claude/
```

**Windows**:
```
%APPDATA%\Claude\
```

**Linux**:
```bash
~/.config/Claude/
```

### Step 2: Edit Configuration

Open or create `claude_desktop_config.json` in this directory.

If the file doesn't exist, create it with this content:

```json
{
  "mcpServers": {
    "trellis-workflows": {
      "command": "poetry",
      "args": ["run", "-C", "/absolute/path/to/trellis-mcp-server", "trellis-mcp"],
      "env": {
        "TRELLIS_API_KEY": "Bearer trellis_your_api_key_here",
        "TRELLIS_WORKFLOW_ID": "wflow_XXXXX",
        "TRELLIS_PROJECT_ID": "proj_XXXXX"
      }
    }
  }
}
```

If the file already exists with other MCP servers, add the `trellis-workflows` entry to the existing `mcpServers` object.

### Step 3: Update Paths and Credentials

Replace the following:

1. **Path to repository**:
   
   **macOS/Linux example**:
   ```json
   "args": ["run", "-C", "/Users/alan/Code/trellis-mcp-server", "trellis-mcp"]
   ```
   
   **Windows example**:
   ```json
   "args": ["run", "-C", "C:/Users/Alan/Code/trellis-mcp-server", "trellis-mcp"]
   ```
   
   💡 **Tip**: Use forward slashes (/) even on Windows.

2. **Your credentials**:
   ```json
   "env": {
     "TRELLIS_API_KEY": "Bearer trellis_abc123xyz...",
     "TRELLIS_WORKFLOW_ID": "wflow_35Gv32Yf2rmNScDPohoJUS7qZ1X",
     "TRELLIS_PROJECT_ID": "proj_35GnIQ94TycwKhM9h2OuKGZz9f7"
   }
   ```

### Step 4: Validate JSON

Before saving, verify your JSON is valid using a JSON validator or:

**macOS/Linux**:
```bash
python3 -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows**:
```powershell
python -m json.tool $env:APPDATA\Claude\claude_desktop_config.json
```

If there are no errors, your JSON is valid. Save the file.

### Step 5: Restart Claude Desktop

**Completely quit** Claude Desktop:

- **macOS**: Cmd+Q or right-click dock icon → Quit
- **Windows**: Right-click system tray icon → Exit
- **Linux**: Close all windows and kill any background processes

Then restart Claude Desktop.

## Testing Your Setup

### Step 1: Check Connection Status

Look for the 🔌 icon in the bottom-right corner of Claude Desktop. If you see it, MCP servers are connected.

Click the icon to see connected servers. You should see `trellis-workflows` listed.

### Step 2: Test Basic Functionality

Try these prompts in order:

**Test 1: List Transformations**
```
What transformations are available in my Trellis project?
```

Expected: Claude uses `get_transformations` and shows a list of transformations.

**Test 2: List Entities**
```
What entities exist in this project?
```

Expected: Claude uses `get_entities` and shows entities like "Referral", "Patient", etc.

**Test 3: Get Workflow Config**
```
Show me the current workflow configuration
```

Expected: Claude uses `get_workflow_config` and describes the workflow (should be empty if you created a new workflow).

**Test 4: Get Entity Fields**
```
What fields does the Referral entity have?
```

Expected: Claude uses `get_entity_fields` and lists fields like "First Name", "Last Name", etc.

### Step 3: Test Workflow Creation

Try creating a simple workflow:

```
Create a workflow that triggers when a row is created on the Referral entity, 
runs the Referral transformation, and saves the outputs back to the Referral entity.
```

Expected behavior:
1. Claude fetches available entities and transformations
2. Claude creates three blocks:
   - Trigger block for row creation
   - Action block to run transformation
   - Action block to update entity
3. Claude confirms the workflow was created

Verify in Trellis:
1. Go to your workflow in the Trellis dashboard
2. You should see the three blocks Claude created
3. They should be connected in sequence

### Step 4: Verify Logs

Check the log file to see detailed operations:

**macOS/Linux**:
```bash
cat ~/.trellis_mcp/server.log
```

**Windows**:
```powershell
type %USERPROFILE%\.trellis_mcp\server.log
```

You should see entries like:
```
2024-11-15 10:30:15 - trellis_mcp - INFO - Trellis MCP Server starting...
2024-11-15 10:30:16 - trellis_mcp.client - INFO - Initialized TrellisClient for project proj_XXXXX
2024-11-15 10:30:20 - trellis_mcp - INFO - Tool called: get_transformations
2024-11-15 10:30:21 - trellis_mcp - INFO - Successfully retrieved transformations
```

## Troubleshooting

### Issue: 🔌 Icon Not Appearing

**Solution**:
1. Verify Claude Desktop is completely restarted (not just window closed)
2. Check configuration file path is correct
3. Ensure JSON is valid (no syntax errors)
4. Check logs for error messages

### Issue: "Command not found: poetry"

**Solution**:
1. Verify Poetry is installed: `poetry --version`
2. Add Poetry to your PATH:
   
   **macOS/Linux** (add to `~/.bashrc` or `~/.zshrc`):
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```
   
   **Windows**: Search "Environment Variables" in Start Menu and add Poetry to PATH

3. Restart your terminal and Claude Desktop

### Issue: Authentication Failed

**Solution**:
1. Verify API key is correct and includes "Bearer " prefix
2. Check Project ID matches your project
3. Ensure you have access to the MCP OA organization in Trellis
4. Try fetching a transformation manually to test credentials:
   ```bash
   curl -X GET "https://enterprise.training.api.runtrellis.com/v1/transforms?proj_ids[]=YOUR_PROJECT_ID" \
     -H "Authorization: YOUR_API_KEY" \
     -H "API-Version: 2025-03"
   ```

### Issue: "No such file or directory"

**Solution**:
1. Ensure the path in `claude_desktop_config.json` is absolute (starts with `/` on macOS/Linux or `C:/` on Windows)
2. Use forward slashes (/) even on Windows
3. Verify the directory exists:
   ```bash
   ls /absolute/path/to/trellis-mcp-server
   ```

### Issue: Claude Doesn't Use Tools

**Solution**:
1. Be explicit in your prompts: "Use your tools to fetch..."
2. Wait for initial connection (can take 5-10 seconds after restart)
3. Check logs for error messages
4. Try clicking the 🔌 icon to verify server status

## Next Steps

Now that your server is set up, you can:

1. **Explore Example Prompts**: Try the example prompts from the README
2. **Build Complex Workflows**: Create multi-step workflows with child entities
3. **Experiment with Mappings**: Test different field mapping configurations
4. **Read the API Docs**: Explore the Trellis API documentation for advanced features

## Getting Help

If you're still having issues:

1. Check `~/.trellis_mcp/server.log` for detailed error messages
2. Review the main README.md for architectural details
3. Contact founders@runtrellis.com for Trellis access issues
4. Check the MCP documentation at https://modelcontextprotocol.io

## Configuration Reference

Complete example configuration:

```json
{
  "mcpServers": {
    "trellis-workflows": {
      "command": "poetry",
      "args": ["run", "-C", "/Users/alan/Code/trellis-mcp-server", "trellis-mcp"],
      "env": {
        "TRELLIS_API_KEY": "Bearer trellis_abc123xyz789",
        "TRELLIS_WORKFLOW_ID": "wflow_35Gv32Yf2rmNScDPohoJUS7qZ1X",
        "TRELLIS_PROJECT_ID": "proj_35GnIQ94TycwKhM9h2OuKGZz9f7"
      }
    }
  }
}
```

## Quick Start Checklist

Use this checklist for future setups:

- [ ] Python 3.10+ installed
- [ ] Poetry installed
- [ ] Repository cloned
- [ ] Dependencies installed (`poetry install`)
- [ ] API key obtained
- [ ] Project ID copied
- [ ] New workflow created
- [ ] Workflow ID copied
- [ ] `claude_desktop_config.json` edited
- [ ] Absolute path to repo set
- [ ] All credentials added
- [ ] JSON validated
- [ ] Claude Desktop restarted
- [ ] 🔌 icon visible
- [ ] Test prompts working
- [ ] Workflow visible in Trellis dashboard

Congratulations! Your Trellis MCP Server is now set up and ready to use. 🎉