"""OpenProject API client for MCP server."""
import json
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import settings
from models import Project, WorkPackage, ProjectCreateRequest, WorkPackageCreateRequest
from utils.logging import get_logger, log_api_request, log_api_response, log_error

logger = get_logger(__name__)


class OpenProjectAPIError(Exception):
    """Exception raised for OpenProject API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        
        # Enhanced error handling for OpenProject-specific formats
        if response_data and "_embedded" in response_data:
            # Handle HAL+JSON error structures
            errors = response_data.get("_embedded", {}).get("errors", [])
            if errors:
                self.detailed_errors = errors
                # Extract more specific error messages from HAL structure
                error_messages = []
                for error in errors:
                    if isinstance(error, dict):
                        error_msg = error.get("message", "")
                        if error_msg:
                            error_messages.append(error_msg)
                if error_messages:
                    self.message = "; ".join(error_messages)
        
        # Add OpenProject-specific error codes
        self.openproject_error_code = response_data.get("error_code") if response_data else None
        
        # Extract validation errors if present
        if response_data and "errors" in response_data:
            validation_errors = response_data.get("errors", {})
            if isinstance(validation_errors, dict):
                self.validation_errors = validation_errors
                # Create more descriptive error message from validation errors
                error_details = []
                for field, field_errors in validation_errors.items():
                    if isinstance(field_errors, list):
                        for error in field_errors:
                            error_details.append(f"{field}: {error}")
                    else:
                        error_details.append(f"{field}: {field_errors}")
                if error_details:
                    self.message = f"{self.message}. Validation errors: {'; '.join(error_details)}"
        
        super().__init__(self.message)


class OpenProjectClient:
    """Client for interacting with OpenProject API."""
    
    def __init__(self):
        self.base_url = settings.openproject_url.rstrip('/')
        self.api_key = settings.openproject_api_key
        self.api_base = f"{self.base_url}/api/v3"
        
        # Initialize cache
        self._cache = {}
        self._cache_timeout = timedelta(minutes=5)
        
        # Encode API key for Basic authentication
        auth_string = base64.b64encode(f'apikey:{self.api_key}'.encode()).decode()
        
        # HTTP client configuration
        # Use OPENPROJECT_HOST if provided, otherwise extract from URL
        from urllib.parse import urlparse
        if settings.openproject_host:
            host_header = settings.openproject_host
        else:
            parsed_url = urlparse(self.base_url)
            host_header = parsed_url.netloc

        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            headers={
                "Authorization": f"Basic {auth_string}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Host": host_header,
                "X-Forwarded-Proto": "https"  # Prevent HTTP to HTTPS redirects
            },
            follow_redirects=True
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True
    )
    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to OpenProject API."""
        full_url = f"{self.api_base}{url}"
        
        # Log the request
        log_api_request(logger, method, full_url)
        
        try:
            response = await self.client.request(method, full_url, **kwargs)
            
            # Log the response
            log_api_response(logger, method, full_url, response.status_code)
            
            # Check for HTTP errors
            if response.status_code >= 400:
                error_data = {}
                try:
                    error_data = response.json()
                except json.JSONDecodeError:
                    pass
                
                error = OpenProjectAPIError(
                    f"API request failed: {response.status_code} {response.reason_phrase}",
                    status_code=response.status_code,
                    response_data=error_data
                )
                log_error(logger, error, {"url": full_url, "method": method, "status_code": response.status_code})
                raise error
            
            # Parse JSON response
            if response.content:
                return response.json()
            return {}
            
        except httpx.RequestError as e:
            error = OpenProjectAPIError(f"Request failed: {str(e)}")
            log_error(logger, error, {"url": full_url, "method": method})
            raise error
        except json.JSONDecodeError as e:
            error = OpenProjectAPIError(f"Invalid JSON response: {str(e)}")
            log_error(logger, error, {"url": full_url, "method": method})
            raise error
    
    async def get_projects(self, use_pagination: bool = False) -> List[Dict[str, Any]]:
        """Get list of projects."""
        if use_pagination:
            return await self.get_paginated_results("/projects")
        response = await self._make_request("GET", "/projects")
        return response.get("_embedded", {}).get("elements", [])
    
    async def create_project(self, project_data: ProjectCreateRequest) -> Dict[str, Any]:
        """Create a new project."""
        payload = {
            "name": project_data.name,
            "description": {
                "raw": project_data.description
            }
        }
        
        # Only add status if it's not the default
        if project_data.status and project_data.status != "active":
            payload["status"] = project_data.status
        
        return await self._make_request("POST", "/projects", json=payload)
    
    async def get_work_packages(self, project_id: int, use_pagination: bool = False) -> List[Dict[str, Any]]:
        """Get work packages for a project."""
        url = f"/projects/{project_id}/work_packages"
        if use_pagination:
            return await self.get_paginated_results(url)
        response = await self._make_request("GET", url)
        return response.get("_embedded", {}).get("elements", [])
    
    async def search_work_packages(self, query: str, project_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search work packages by subject or description.
        
        Args:
            query: Search query string
            project_id: Optional project ID to filter by project
        
        Returns:
            List of matching work packages
        """
        import urllib.parse
        
        # Build filter for subject containing query
        filters = [{"subject": {"operator": "~", "values": [query]}}]
        
        if project_id:
            filters.append({"project": {"operator": "=", "values": [str(project_id)]}})
        
        # Encode filters as JSON and use as query param
        filters_json = json.dumps(filters)
        url = f"/work_packages?filters={urllib.parse.quote(filters_json)}"
        
        response = await self._make_request("GET", url)
        return response.get("_embedded", {}).get("elements", [])
    
    async def create_work_package(self, work_package_data: WorkPackageCreateRequest) -> Dict[str, Any]:
        """Create a new work package."""
        payload = {
            "subject": work_package_data.subject,
            "_links": {
                "project": {
                    "href": f"/api/v3/projects/{work_package_data.project_id}"
                },
                "type": {
                    "href": f"/api/v3/types/{work_package_data.type_id}"
                },
                "status": {
                    "href": f"/api/v3/statuses/{work_package_data.status_id}"
                },
                "priority": {
                    "href": f"/api/v3/priorities/{work_package_data.priority_id}"
                }
            }
        }
        
        # Add optional fields
        if work_package_data.description:
            payload["description"] = {"raw": work_package_data.description}
        
        if work_package_data.assignee_id:
            payload["_links"]["assignee"] = {
                "href": f"/api/v3/users/{work_package_data.assignee_id}"
            }
        
        if work_package_data.parent_id:
            payload["_links"]["parent"] = {
                "href": f"/api/v3/work_packages/{work_package_data.parent_id}"
            }
        
        if work_package_data.start_date:
            payload["startDate"] = work_package_data.start_date
        
        if work_package_data.due_date:
            payload["dueDate"] = work_package_data.due_date
        
        if work_package_data.estimated_hours:
            payload["estimatedTime"] = f"PT{work_package_data.estimated_hours}H"
        
        return await self._make_request("POST", "/work_packages", json=payload)
    
    async def update_work_package(self, work_package_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing work package."""
        url = f"/work_packages/{work_package_id}"
        return await self._make_request("PATCH", url, json=updates)
    
    async def create_work_package_relation(
        self, 
        from_wp_id: int, 
        to_wp_id: int, 
        relation_type: str = "follows",
        description: str = "",
        lag: int = 0
    ) -> Dict[str, Any]:
        """Create a relation between two work packages.
        
        Args:
            from_wp_id: ID of the work package that will have the relation (the one making the request)
            to_wp_id: ID of the work package that is the target of the relation
            relation_type: Type of relation (follows, precedes, blocks, blocked, relates, duplicates, duplicated)
            description: Optional description of the relation
            lag: Number of working days between finish of predecessor and start of successor
        """
        # Build the URL for creating relation from the "from" work package
        url = f"/work_packages/{from_wp_id}/relations"
        
        payload = {
            "type": relation_type,
            "_links": {
                "to": {
                    "href": f"/api/v3/work_packages/{to_wp_id}"
                }
            }
        }
        
        # Add optional fields
        if description:
            payload["description"] = description
        
        if lag != 0:
            payload["lag"] = lag
        
        return await self._make_request("POST", url, json=payload)
    
    async def get_work_package_relations(self, work_package_id: int) -> List[Dict[str, Any]]:
        """Get all relations for a specific work package."""
        url = f"/work_packages/{work_package_id}/relations"
        response = await self._make_request("GET", url)
        return response.get("_embedded", {}).get("elements", [])
    
    async def delete_work_package_relation(self, relation_id: int) -> Dict[str, Any]:
        """Delete a work package relation by its ID."""
        url = f"/relations/{relation_id}"
        return await self._make_request("DELETE", url)
    
    async def get_work_package_by_id(self, work_package_id: int) -> Dict[str, Any]:
        """Get a specific work package by ID."""
        url = f"/work_packages/{work_package_id}"
        return await self._make_request("GET", url)
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to OpenProject API."""
        try:
            response = await self._make_request("GET", "/")
            return {
                "success": True,
                "message": "Connection successful",
                "openproject_version": response.get("coreVersion", "unknown")
            }
        except OpenProjectAPIError as e:
            return {
                "success": False,
                "message": f"Connection failed: {e.message}",
                "error": str(e)
            }
    
    async def get_users(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Get list of users with optional filtering."""
        url = "/users"
        if filters:
            params = "&".join([f"{k}={v}" for k, v in filters.items()])
            url += f"?{params}"
        response = await self._make_request("GET", url)
        return response.get("_embedded", {}).get("elements", [])

    async def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Get specific user by ID."""
        return await self._make_request("GET", f"/users/{user_id}")

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address."""
        try:
            # OpenProject API filter format for email search
            filters = f'[{{"email": {{"operator": "=", "values": ["{email}"]}}}}]'
            users = await self.get_users({"filters": filters})
            return users[0] if users else None
        except (OpenProjectAPIError, IndexError):
            return None

    async def get_work_package_types(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Get available work package types."""
        if use_cache:
            return await self.get_cached_or_fetch(
                "work_package_types",
                lambda: self._fetch_work_package_types()
            )
        return await self._fetch_work_package_types()

    async def _fetch_work_package_types(self) -> List[Dict[str, Any]]:
        """Internal method to fetch work package types from API."""
        response = await self._make_request("GET", "/types")
        return response.get("_embedded", {}).get("elements", [])

    async def get_work_package_statuses(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Get available work package statuses."""
        if use_cache:
            return await self.get_cached_or_fetch(
                "work_package_statuses",
                lambda: self._fetch_work_package_statuses()
            )
        return await self._fetch_work_package_statuses()

    async def _fetch_work_package_statuses(self) -> List[Dict[str, Any]]:
        """Internal method to fetch work package statuses from API."""
        response = await self._make_request("GET", "/statuses") 
        return response.get("_embedded", {}).get("elements", [])

    async def get_priorities(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Get available priorities."""
        if use_cache:
            return await self.get_cached_or_fetch(
                "priorities",
                lambda: self._fetch_priorities()
            )
        return await self._fetch_priorities()

    async def _fetch_priorities(self) -> List[Dict[str, Any]]:
        """Internal method to fetch priorities from API."""
        response = await self._make_request("GET", "/priorities")
        return response.get("_embedded", {}).get("elements", [])

    async def get_project_memberships(self, project_id: int) -> List[Dict[str, Any]]:
        """Get list of project members."""
        url = f"/projects/{project_id}/memberships"
        response = await self._make_request("GET", url)
        return response.get("_embedded", {}).get("elements", [])

    async def get_cached_or_fetch(self, cache_key: str, fetch_func):
        """Get cached result or fetch fresh data."""
        now = datetime.now()
        
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if now - timestamp < self._cache_timeout:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_data
        
        logger.debug(f"Cache miss for key: {cache_key}, fetching fresh data")
        fresh_data = await fetch_func()
        self._cache[cache_key] = (fresh_data, now)
        return fresh_data

    def _clear_cache_key(self, cache_key: str):
        """Clear specific cache key."""
        if cache_key in self._cache:
            del self._cache[cache_key]
            logger.debug(f"Cleared cache key: {cache_key}")

    def _clear_all_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        logger.debug("Cleared all cache data")

    async def get_paginated_results(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict]:
        """Handle paginated responses from OpenProject API."""
        all_results = []
        page_size = 100  # OpenProject default
        offset = 0
        
        while True:
            paginated_params = {"pageSize": page_size, "offset": offset}
            if params:
                paginated_params.update(params)
                
            response = await self._make_request("GET", endpoint, params=paginated_params)
            elements = response.get("_embedded", {}).get("elements", [])
            
            if not elements:
                break
                
            all_results.extend(elements)
            
            # Check if we have more pages
            total = response.get("total", 0)
            if offset + page_size >= total:
                break
                
            offset += page_size
        
        return all_results

    async def get_time_entries(
        self,
        work_package_id: Optional[int] = None,
        project_id: Optional[int] = None,
        user_id: Optional[int] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get time entries with optional filters.

        Args:
            work_package_id: Filter by work package ID
            project_id: Filter by project ID
            user_id: Filter by user ID
            from_date: Filter entries from this date (YYYY-MM-DD)
            to_date: Filter entries to this date (YYYY-MM-DD)
        """
        # Build filter query
        filters = []
        if work_package_id:
            filters.append(f'{{"work_package": {{"operator": "=", "values": ["{work_package_id}"]}}}}')
        if project_id:
            filters.append(f'{{"project": {{"operator": "=", "values": ["{project_id}"]}}}}')
        if user_id:
            filters.append(f'{{"user": {{"operator": "=", "values": ["{user_id}"]}}}}')
        if from_date:
            filters.append(f'{{"spent_on": {{"operator": ">=d", "values": ["{from_date}"]}}}}')
        if to_date:
            filters.append(f'{{"spent_on": {{"operator": "<=d", "values": ["{to_date}"]}}}}')

        url = "/time_entries"
        if filters:
            filter_str = "[" + ",".join(filters) + "]"
            response = await self._make_request("GET", url, params={"filters": filter_str})
        else:
            response = await self._make_request("GET", url)

        return response.get("_embedded", {}).get("elements", [])

    async def get_time_entry_by_id(self, time_entry_id: int) -> Dict[str, Any]:
        """Get a specific time entry by ID."""
        return await self._make_request("GET", f"/time_entries/{time_entry_id}")

    async def create_time_entry(
        self,
        work_package_id: int,
        hours: float,
        spent_on: str,
        comment: str = "",
        activity_id: int = 1
    ) -> Dict[str, Any]:
        """Create a new time entry.

        Args:
            work_package_id: ID of the work package to log time against
            hours: Hours spent (decimal, e.g., 2.5 for 2 hours 30 minutes)
            spent_on: Date when work was done (YYYY-MM-DD format)
            comment: Description of work done
            activity_id: Activity type ID (default: 1)
        """
        payload = {
            "hours": f"PT{hours}H",  # ISO 8601 duration format
            "spentOn": spent_on,
            "_links": {
                "workPackage": {
                    "href": f"/api/v3/work_packages/{work_package_id}"
                },
                "activity": {
                    "href": f"/api/v3/time_entries/activities/{activity_id}"
                }
            }
        }

        if comment:
            payload["comment"] = {"raw": comment}

        return await self._make_request("POST", "/time_entries", json=payload)

    async def update_time_entry(
        self,
        time_entry_id: int,
        hours: Optional[float] = None,
        spent_on: Optional[str] = None,
        comment: Optional[str] = None,
        activity_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update an existing time entry.

        Args:
            time_entry_id: ID of the time entry to update
            hours: New hours value
            spent_on: New date
            comment: New comment
            activity_id: New activity ID
        """
        payload = {}

        if hours is not None:
            payload["hours"] = f"PT{hours}H"

        if spent_on is not None:
            payload["spentOn"] = spent_on

        if comment is not None:
            payload["comment"] = {"raw": comment}

        if activity_id is not None:
            if "_links" not in payload:
                payload["_links"] = {}
            payload["_links"]["activity"] = {
                "href": f"/api/v3/time_entries/activities/{activity_id}"
            }

        return await self._make_request("PATCH", f"/time_entries/{time_entry_id}", json=payload)

    async def delete_time_entry(self, time_entry_id: int) -> Dict[str, Any]:
        """Delete a time entry."""
        return await self._make_request("DELETE", f"/time_entries/{time_entry_id}")

    async def get_time_activities(self) -> List[Dict[str, Any]]:
        """Get available time entry activities (e.g., Development, Testing, Management)."""
        response = await self._make_request("GET", "/time_entries/activities")
        return response.get("_embedded", {}).get("elements", [])

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
