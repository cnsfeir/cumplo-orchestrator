# pylint: disable=no-member

import json
from http import HTTPStatus
from logging import CRITICAL, DEBUG, basicConfig, getLogger

import google.cloud.logging
from cumplo_common.middlewares import PubSubMiddleware
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from cumplo_orchestrator.routers import funding_requests
from cumplo_orchestrator.utils.constants import IS_TESTING, LOG_FORMAT

logger = getLogger(__name__)

# NOTE: Mute noisy third-party loggers
for module in ("google", "urllib3", "werkzeug"):
    getLogger(module).setLevel(CRITICAL)

if IS_TESTING:
    basicConfig(level=DEBUG, format=LOG_FORMAT)
else:
    client = google.cloud.logging.Client()
    client.setup_logging(log_level=DEBUG)

app = FastAPI()
app.add_middleware(PubSubMiddleware)


@app.exception_handler(ValidationError)
async def _validation_error_handler(_request: Request, error: ValidationError) -> JSONResponse:  # noqa: RUF029
    """Format ValidationError as a JSON response."""
    content = json.loads(jsonable_encoder(error.json()))
    logger.error(f"Validation error: {content}")
    return JSONResponse(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, content=content)


app.include_router(funding_requests.router)
