from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import sys
import os

# Add the parent directory to the path so we can import the app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

def list_endpoints():
    """List all available endpoints in the FastAPI app"""
    print("Listing all available endpoints in the API:")
    
    for route in app.routes:
        print(f"{route.methods} {route.path}")
    
    # Generate OpenAPI schema to show all operations
    schema = get_openapi(
        title=app.title or "FastAPI",
        version=app.version or "0.1.0",
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes
    )
    
    print("\nDetailed endpoints with operation IDs:")
    if "paths" in schema:
        for path, operations in schema["paths"].items():
            for method, operation in operations.items():
                if "operationId" in operation:
                    print(f"{method.upper()} {path} -> {operation['operationId']}")
                    if "summary" in operation:
                        print(f"  Summary: {operation['summary']}")
                else:
                    print(f"{method.upper()} {path}")

if __name__ == "__main__":
    list_endpoints()
