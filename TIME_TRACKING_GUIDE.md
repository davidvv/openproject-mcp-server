# OpenProject MCP Server - Time Tracking Guide

## 🎉 Quick Start

Your OpenProject MCP server now has **full time tracking** capabilities!

### Container Status
- **MCP SSE Endpoint**: http://localhost:39127/sse
- **Status Dashboard**: http://localhost:8082/
- **Health Check**: http://localhost:8082/health
- **Container**: openproject-mcp-server (healthy)

---

## ⏱️ Time Tracking Features

### 1. Log Time Entry
Log hours worked on a task/work package.

**Example requests to Claude:**
- "Log 3 hours of work on task 42 for today"
- "Log 2.5 hours on work package 15 for yesterday with comment 'Bug fixes'"
- "Log 4 hours of development work on task 28 for 2026-01-08"

**Parameters:**
- `work_package_id`: Task ID (required)
- `hours`: Decimal hours, e.g., 2.5 = 2h 30m (required)
- `spent_on`: Date in YYYY-MM-DD format (required)
- `comment`: What you worked on (optional)
- `activity_id`: Activity type ID - use get_time_activities (default: 1)

---

### 2. Get Time Entries
View time logs with flexible filtering.

**Example requests:**
- "Show all time entries for work package 42"
- "Get my time entries for this week"
- "Show time logged on project 5 in January"
- "List time entries from 2026-01-01 to 2026-01-31"

**Filters (all optional):**
- `work_package_id`: Filter by task
- `project_id`: Filter by project
- `user_id`: Filter by user
- `from_date`: Start date (YYYY-MM-DD)
- `to_date`: End date (YYYY-MM-DD)

---

### 3. Get Time Report
Generate comprehensive time tracking reports.

**Example requests:**
- "Generate a time report for project 5"
- "Show time breakdown for this month"
- "Time report by user for work package 42"
- "Weekly time tracking summary"

**Report includes:**
- Total hours logged
- Breakdown by user
- Breakdown by activity (Development, Testing, etc.)
- Breakdown by work package
- Daily time distribution

---

### 4. Update Time Entry
Modify existing time logs.

**Example requests:**
- "Update time entry 123 to 4 hours"
- "Change comment on time entry 456 to 'Code review completed'"
- "Update time entry 789 date to 2026-01-10"

**What you can update:**
- Hours worked
- Date (spent_on)
- Comment/description
- Activity type

---

### 5. Delete Time Entry
Remove a time log.

**Example request:**
- "Delete time entry 123"

---

### 6. Get Time Activities
List available activity types for time logging.

**Example request:**
- "What time entry activities are available?"
- "Show me the activity types"

**Common activities:**
- Development
- Testing
- Management
- Documentation
- Support

---

## 🔌 Setup with Claude Desktop

### 1. Find your Claude Desktop config file:
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. Add this configuration:
```json
{
  "mcpServers": {
    "openproject": {
      "url": "http://localhost:39127/sse"
    }
  }
}
```

### 3. Restart Claude Desktop

That's it! All 22 MCP tools will be available in Claude.

---

## 📊 Complete Tool List (22 tools)

### Project Management
- `create_project` - Create new projects
- `get_projects` - List all projects
- `get_project_summary` - Get project overview with stats

### Work Packages (Tasks)
- `create_work_package` - Create tasks with dates, estimates
- `get_work_packages` - List tasks in a project
- `update_work_package` - Modify existing tasks
- `create_work_package_dependency` - Link tasks for Gantt charts
- `get_work_package_relations` - View task dependencies
- `delete_work_package_relation` - Remove dependencies

### Users & Teams
- `get_users` - List users (with email filter)
- `assign_work_package_by_email` - Assign tasks by email
- `get_project_members` - See project team members

### Metadata
- `get_work_package_types` - Get task types (Task, Bug, Feature, etc.)
- `get_work_package_statuses` - Get available statuses
- `get_priorities` - Get priority levels

### ⏱️ Time Tracking (NEW!)
- `log_time_entry` - Log work hours
- `get_time_entries` - View time logs with filters
- `update_time_entry` - Modify time entries
- `delete_time_entry` - Remove time entries
- `get_time_activities` - List activity types
- `get_time_report` - Generate time tracking reports

### System
- `health_check` - Check server and OpenProject connection

---

## 💡 Pro Tips

1. **Decimal Hours**: Use decimals for partial hours
   - 1.5 = 1 hour 30 minutes
   - 2.25 = 2 hours 15 minutes
   - 0.5 = 30 minutes

2. **Time Reports**: Generate reports by week/month to track productivity
   - "Show time report for this week"
   - "Generate monthly time summary for project 5"

3. **Activity Types**: Use appropriate activity types for better reporting
   - Development for coding
   - Testing for QA work
   - Management for meetings
   - Documentation for writing docs

4. **Bulk Queries**: Ask Claude to analyze multiple work packages
   - "Show total time spent on work packages 10, 11, and 12"
   - "Compare time logged vs estimated hours for project 3"

---

## 🔧 Troubleshooting

### Check Server Status
```bash
docker ps | grep openproject-mcp-server
curl http://localhost:8082/health | python3 -m json.tool
```

### View Logs
```bash
docker logs openproject-mcp-server --tail 50
```

### Restart Server
```bash
docker compose restart
```

---

## 📚 Example Workflows

### Daily Time Logging
1. "Show me my open tasks"
2. Work on tasks throughout the day
3. "Log 3 hours on task 42 for today - implemented authentication"
4. "Log 2 hours on task 43 - code review and testing"

### Weekly Time Review
1. "Generate a time report for this week"
2. Review hours by activity type
3. Compare with estimated hours
4. "Show which tasks took more time than estimated"

### Project Time Analysis
1. "Get time report for project 5"
2. "Show time breakdown by user"
3. "Which work packages consumed the most time?"
4. Use insights for future project planning

---

## 🚀 Ready to Use!

Your OpenProject MCP server is fully configured with time tracking!

Start Claude Desktop and try:
- "Show me all projects in OpenProject"
- "Log 2 hours of work on task 42 for today"
- "Generate a time report for this week"

Happy time tracking! ⏱️✨
