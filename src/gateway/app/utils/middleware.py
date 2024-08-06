import time
from typing import Any

from fastapi import Request

from app.utils.logger import logger


async def middleware_logger(request: Request, call_next: Any) -> Any:
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    api_info = {
        "url": str(request.url),
        "method": request.method,
        "query": dict(request.query_params),
        "process_time": process_time
    }
    logger.info(api_info, extra=api_info)
    return response
