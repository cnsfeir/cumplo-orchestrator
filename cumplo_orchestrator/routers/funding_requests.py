# pylint: disable=no-member

from http import HTTPStatus
from logging import getLogger

from cumplo_common.database import firestore
from cumplo_common.integrations.cloud_pubsub import CloudPubSub
from cumplo_common.models.funding_request import FundingRequest
from fastapi import APIRouter, Request

from cumplo_orchestrator.utils.constants import USER_FUNDING_REQUESTS_TOPIC

logger = getLogger(__name__)

router = APIRouter(prefix="/funding-requests")


@router.post(path="/distribute", status_code=HTTPStatus.NO_CONTENT)
def _filter_funding_requests(_request: Request, payload: list[FundingRequest]) -> None:
    """
    Distributes the available funding requests event among the users who have configured channels
    """
    logger.info(f"Distributing {len(payload)} available funding requests")
    for user in firestore.client.users.get_all():
        if not user.channels:
            logger.info(f"User {user.id} has no channels configured. Skipping")
            continue

        logger.info(f"Emiting event for user {user.id} about available funding requests")
        content = [funding_request.json() for funding_request in payload]
        CloudPubSub.publish(content, USER_FUNDING_REQUESTS_TOPIC, id_user=str(user.id))
