import json
from logging import getLogger
from fastapi import APIRouter, Request
from src.errors import invalidJson, requireFeedbackWithTextBlock, requireExerciseId
from src.entities import FeedbackWithTextBlock, Feedback
from src.feedback.FeedbackConsistency import FeedbackConsistency

logger = getLogger(name="FeedbackCommentRequest")
router = APIRouter()

@router.post("/feedback_consistency")
async def feedback(request: Request):
    logger.debug("-" * 80)
    logger.info("Start processing Feedback Comment Request:")

    # Parse json
    try:
        doc = await request.json()
    except Exception as e:
        logger.error("Exception while parsing json: {}".format(str(e)))
        raise invalidJson

    logger.info("Request: {}".format(doc))
    if "feedbackWithTextBlock" not in doc:
        logger.error("{}".format(requireFeedbackWithTextBlock.detail))
        raise requireFeedbackWithTextBlock

    if "exerciseId" not in doc:
        logger.error("{}".format(requireExerciseId.detail))
        raise requireExerciseId

    blocks: list[FeedbackWithTextBlock] = []

    for fwt in doc['feedbackWithTextBlock']:
        blocks.append(FeedbackWithTextBlock(fwt['textBlockId'], fwt['clusterId'], fwt['text'], Feedback(fwt['feedbackId'], fwt['feedbackText'], fwt['credits'])))

    __fc = FeedbackConsistency(doc['exerciseId'])
    response = __fc.check_consistency(feedback_with_text_blocks=blocks)
    logger.info("Response {}".format(response))
    __fc.store_feedback()

    logger.info("Completed Feedback Comment Embedding Request.")
    logger.debug("-" * 80)
    return response
