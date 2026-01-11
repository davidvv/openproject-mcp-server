# OpenProject MCP Server - Usage Guide

This guide explains how to use the OpenProject MCP (Model Context Protocol) Server with Claude Desktop.

## What is This MCP Server?

This MCP server provides Claude Desktop with direct integration to OpenProject, allowing you to:
- Manage projects and work packages
- Track time on tasks
- Assign work to team members
- Query project status and progress
- Manage work package relationships and dependencies

## Connection Information

### Server Details
- **Protocol**: SSE (Server-Sent Events)
- **Endpoint**: `http://localhost:39127/sse`
- **Status Dashboard**: `http://localhost:8082/`
- **Docker Container**: `openproject-mcp-server`

### OpenProject Instance
- **URL**: https://openproject.dvvcloud.work
- **Internal Connection**: Direct to OpenProject Docker containers
- **API Version**: v3
- **OpenProject Version**: 16.4.1

## Claude Desktop Configuration

Add this to your Claude Desktop MCP settings file:

**Location**:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Configuration**:
```json
{
  "mcpServers": {
    "openproject": {
      "command": "curl",
      "args": [
        "-N",
        "-H",
        "Accept: text/event-stream",
        "http://localhost:39127/sse"
      ]
    }
  }
}
```

After adding this configuration, restart Claude Desktop.

## Available Tools (22 Total)

### Health & System
- `health_check` - Check if OpenProject connection is working

### Project Management
- `create_project` - Create a new project
- `get_projects` - List all projects
- `get_project_summary` - Get detailed project information with statistics

### Work Package Management
- `create_work_package` - Create a new task/work package
- `get_work_packages` - List work packages (with filtering)
- `update_work_package` - Update work package details (subject, description, status, priority, assignee)
- `create_work_package_dependency` - Create dependencies between work packages
- `get_work_package_relations` - View relationships between work packages
- `delete_work_package_relation` - Remove work package relationships

### Assignment & Users
- `get_users` - List all users in OpenProject
- `assign_work_package_by_email` - Assign a work package to a user by their email
- `get_project_members` - List members of a specific project

### Time Tracking
- `log_time_entry` - Log hours worked on a task
- `get_time_entries` - View time logs (with filtering by work package, project, user, date range)
- `update_time_entry` - Modify existing time entries
- `delete_time_entry` - Remove time entries
- `get_time_activities` - List available activity types (e.g., Development, Testing, Management)
- `get_time_report` - Generate comprehensive time tracking reports

### Metadata & Configuration
- `get_work_package_types` - Get available work package types (Task, Bug, Feature, etc.)
- `get_work_package_statuses` - Get available statuses (New, In Progress, Closed, etc.)
- `get_priorities` - Get available priorities (Low, Normal, High, Immediate)

## Common Usage Examples

### Example 1: Check Connection
```
Can you check if the OpenProject MCP server is working?
```

Expected response: Connection status, OpenProject version, available tools.

### Example 2: Create a Task and Log Time
```
Create a work package called "Implement user authentication" in the MCP Development project,
then log 3 hours of work on it for today.
```

Claude will:
1. Find or create the project
2. Create the work package
3. Log the time entry

### Example 3: View Project Status
```
Show me a summary of the "MCP Development" project including all work packages and time spent.
```

Claude will:
1. Get project details
2. List all work packages
3. Retrieve time entries
4. Present a formatted summary

### Example 4: Assign Work
```
Assign the work package #88 to david@example.com
```

Claude will look up the user by email and assign the work package.

### Example 5: Generate Time Report
```
Generate a time report for the last week showing all time entries grouped by user and work package.
```

Claude will use `get_time_report` with appropriate date filters.

### Example 6: Manage Dependencies
```
Make work package #90 depend on work package #88 (it should be blocked by #88).
```

Claude will create a "blocks" relationship between the work packages.

## Time Tracking Details

### Activity Types
Common activity IDs (use `get_time_activities` to see all):
- **1**: Default activity
- May include: Development, Testing, Project Management, Support, etc.

### Time Entry Format
- **Hours**: Decimal format (e.g., 2.5 for 2 hours 30 minutes)
- **Date**: YYYY-MM-DD format
- **Maximum**: 24 hours per entry
- **Minimum**: Greater than 0

### Example Time Logging Commands
```
Log 2.5 hours on work package #88 for today with comment "Initial research and setup"

Log time: 4 hours on "API development" task for 2026-01-08

Add a time entry: 1.5 hours yesterday on the authentication work package
```

## Project Structure

Current projects in your OpenProject instance:
- **MCP Development Test** (ID: 13) - For MCP server development and testing

## User Information

You are currently authenticated as:
- **Name**: David Vences
- **User ID**: 5
- **Role**: Administrator

## Troubleshooting

### MCP Server Not Responding
1. Check if container is running: `docker ps | grep openproject-mcp-server`
2. Check container health: `docker ps` (look for "healthy" status)
3. View logs: `docker logs openproject-mcp-server`
4. Restart container: `cd /home/david/docker/openproject-mcp && docker compose restart`

### Connection Issues
1. Verify endpoint is accessible: `curl http://localhost:39127/sse`
2. Check status dashboard: `curl http://localhost:8082/health`
3. Verify OpenProject connection in dashboard

### Tool Errors
- Check the status dashboard for connection status
- Verify work package/project IDs exist
- Ensure user has proper permissions
- Check date formats (must be YYYY-MM-DD)

## Best Practices

### When Creating Work Packages
- Always specify a clear subject
- Include meaningful descriptions
- Set appropriate type, status, and priority
- Assign to specific users when known

### When Logging Time
- Log time regularly (daily is best)
- Include descriptive comments
- Use appropriate activity types
- Keep entries under 24 hours (split long sessions)

### When Querying Data
- Use filters to narrow results (date ranges, users, projects)
- Request summaries for overview information
- Query specific IDs when known

## Technical Notes

### API Access
- The MCP server connects directly to OpenProject's Docker container
- Uses API key authentication (configured in .env file)
- Bypasses Cloudflare Access by connecting internally
- All API calls use OpenProject API v3

### Data Formats
- Work packages use HAL+JSON format
- Time durations use ISO 8601 format (PT2.5H)
- Dates use ISO 8601 date format (YYYY-MM-DD)
- All responses are formatted as JSON

### Rate Limiting
- No explicit rate limiting on the MCP server
- OpenProject may have its own rate limits
- Pagination is used for large result sets (100 items per page)

## Need Help?

### View All Available Tools
```
What tools are available in the OpenProject MCP server?
```

### Get Tool Details
```
What parameters does the log_time_entry tool accept?
```

### Check Server Status
```
Check the OpenProject MCP server health and show me the status dashboard information.
```

## Additional Documentation

For more detailed information about specific features:
- **Time Tracking**: See `TIME_TRACKING_GUIDE.md` in the project directory
- **OpenProject API**: https://www.openproject.org/docs/api/
- **MCP Protocol**: https://modelcontextprotocol.io/

---

**Server Location**: `/home/david/docker/openproject-mcp/`
**Last Updated**: 2026-01-09
**Version**: 1.0
