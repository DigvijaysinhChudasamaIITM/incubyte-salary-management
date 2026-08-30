from salary_management.main import create_app, health, readiness

app = create_app()
app.add_api_route("/api/health", health, methods=["GET"], tags=["system"])
app.add_api_route("/api/ready", readiness, methods=["GET"], tags=["system"])
