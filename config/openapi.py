"""
OpenAPI configuration for FastAPI documentation.

IMPROVEMENTS:
- Enhanced tag descriptions
- Added additional metadata tags
"""

tags_metadata = [
    {
        "name": "users",
        "description": "User management operations. Create, read, update, and delete users.",
    },
    {
        "name": "health",
        "description": "Health check endpoints for monitoring and Kubernetes probes.",
    },
    {
        "name": "root",
        "description": "Root endpoint and API information.",
    },
]