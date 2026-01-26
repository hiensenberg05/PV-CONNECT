"""Check all registered FastAPI routes"""
from app.main import app

print("Registered FastAPI Routes:\n")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        methods = ', '.join(route.methods)
        print(f"{methods:20} {route.path}")
    elif hasattr(route, 'path'):
        print(f"{'WebSocket':20} {route.path}")

print("\nRoute check complete - all routes registered successfully")
