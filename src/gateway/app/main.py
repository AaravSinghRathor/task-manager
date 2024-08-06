import json
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from httpx import AsyncClient
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logger import logger
from app.utils.middleware import middleware_logger

app = FastAPI()
app.add_middleware(BaseHTTPMiddleware, dispatch=middleware_logger)

# Define your service URLs
AUTH_SERVICE_URL = "http://auth-service:8000/auth"
USER_SERVICE_URL = "http://auth-service:8000/users"
TASK_SERVICE_URL = "http://task-service:8000/tasks"


@app.post("/login")
async def forward_login(request: Request) -> Any:
    async with AsyncClient() as client:
        # Capture the incoming request method, headers, and body
        headers = dict(request.headers)
        body = await request.body()  # Capture request body as bytes

        # Forward the request to the Auth Service
        response = await client.post(
            f"{AUTH_SERVICE_URL}/login", headers=headers, content=body
        )

        # Return the Auth Service's response
        return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/signup")
async def forward_signup(request: Request) -> Any:
    async with AsyncClient() as client:
        # Capture the incoming request method, headers, and body
        headers = dict(request.headers)
        body = await request.body()  # Capture request body as bytes

        # Forward the request to the Auth Service
        response = await client.post(
            f"{AUTH_SERVICE_URL}/signup", headers=headers, content=body
        )

        # Return the Auth Service's response
        return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/users/me")
async def fetch_user_info(request: Request) -> Any:
    async with AsyncClient() as client:

        # Forward the request to the Auth Service
        response = await client.get(f"{USER_SERVICE_URL}/me", headers=request.headers)

        # Return the Auth Service's response
        return JSONResponse(content=response.json(), status_code=response.status_code)


@app.api_route("/tasks/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_tasks(path: str, request: Request) -> Any:
    token = request.headers.get("authorization")
    if token:
        token = token.split(" ")[1]  # Remove "Bearer" prefix
    else:
        return HTTPException(403, "unauthorized")

    async with AsyncClient() as client:

        try:
            # Forward the request to the Auth Service
            token_header = {"authorization": request.headers["authorization"]}
            response = await client.get(f"{USER_SERVICE_URL}/me", headers=token_header)

            if not response.is_success:
                raise HTTPException(response.status_code, response.json())

            # Return the Auth Service's response
            response_json = response.json()
            user_info = {
                "id": response_json.get("id"),
                "email": response_json.get("email"),
            }

            method = request.method
            # Extract the query parameters
            query_params = request.query_params
            url = f"{TASK_SERVICE_URL}/{path}"
            if query_params:
                url += f"?{query_params}"
            headers = dict(request.headers)
            headers.pop("authorization", None)
            headers.update({"X-User-Info": json.dumps(user_info)})

            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                body = await request.body()
                response = await client.post(url, headers=headers, content=body)
            elif method == "PUT":
                body = await request.body()
                response = await client.put(url, headers=headers, content=body)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            elif method == "PATCH":
                response = await client.patch(url, headers=headers)
        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            raise HTTPException(500, "Internal server error")

        return (
            JSONResponse(content=response.json(), status_code=response.status_code)
            if response.content
            else Response(status_code=response.status_code)
        )


# if __name__ == "__main__":
#     uvicorn.run(
#         "app.main:app",
#         host="0.0.0.0",
#         port=8000,
#         log_level="debug",
#         reload=True,
#     )
