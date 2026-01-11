#!/bin/bash
# Example: Log time entry for "MCP Server research and deployment"

# You need to set these values:
WORK_PACKAGE_ID=1  # Replace with actual work package ID
USER_ID=1          # Replace with David's user ID
HOURS=2.5
DATE=$(date +%Y-%m-%d)  # Today's date
COMMENT="MCP Server research and deployment"
ACTIVITY_ID=1      # 1 is usually "Development"

echo "=== Logging Time Entry ==="
echo "Work Package: $WORK_PACKAGE_ID"
echo "User: $USER_ID"
echo "Hours: $HOURS"
echo "Date: $DATE"
echo "Comment: $COMMENT"
echo ""

# Call the OpenProject API
docker exec -i openproject-mcp-server python3 << PYTHON
import asyncio
import sys
sys.path.insert(0, '/app/src')
from openproject_client import OpenProjectClient
from datetime import date

async def main():
    client = OpenProjectClient()
    try:
        result = await client.create_time_entry(
            work_package_id=${WORK_PACKAGE_ID},
            hours=${HOURS},
            spent_on='${DATE}',
            comment='${COMMENT}',
            activity_id=${ACTIVITY_ID}
        )
        print("✅ Time entry logged successfully!")
        print(f"Time Entry ID: {result.get('id')}")
        print(f"Hours: ${HOURS}")
        print(f"Date: ${DATE}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        await client.close()

asyncio.run(main())
PYTHON
