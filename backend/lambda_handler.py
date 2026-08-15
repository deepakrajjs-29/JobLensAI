"""AWS Lambda Entrypoint for JobLens AI FastAPI Application using Mangum adapter."""
from mangum import Mangum
from app.main import app

# Initialize Mangum ASGI adapter for AWS Lambda & Amazon API Gateway HTTP/REST APIs
# lifespan="off" is recommended for serverless execution to optimize cold starts
handler = Mangum(app, lifespan="off")
