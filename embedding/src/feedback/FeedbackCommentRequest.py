import json
from logging import getLogger
from falcon import Request, Response, HTTP_200
from src.errors import emptyBody, requireFeedbackWithTextBlock, requireExerciseId
from src.entities import FeedbackWithTextBlock, Feedback
from src.feedback.FeedbackConsistency import FeedbackConsistency


class FeedbackCommentRequest:
    __logger = getLogger(__name__)

    def on_post(self, req: Request, resp: Response) -> None:
        self.__logger.debug("-" * 80)
        self.__logger.info("Start processing Feedback Comment Request:")
        if req.content_length == 0:
            self.__logger.error("{} ({})".format(emptyBody.title, emptyBody.description))
            raise emptyBody

        doc = json.load(req.stream)
        self.__logger.info("Request: {}".format(doc))
        if "feedbackWithTextBlock" not in doc:
            self.__logger.error("{} ({})".format(requireFeedbackWithTextBlock.title, requireFeedbackWithTextBlock.description))
            raise requireFeedbackWithTextBlock

        if "exerciseId" not in doc:
            self.__logger.error("{} ({})".format(requireExerciseId.title, requireExerciseId.description))
            raise requireExerciseId

        blocks: list[FeedbackWithTextBlock] = []

        for fwt in doc['feedbackWithTextBlock']:
            blocks.append(FeedbackWithTextBlock(fwt['textBlockId'], fwt['clusterId'], fwt['text'], Feedback(fwt['feedbackId'], fwt['feedbackText'], fwt['credits'])))

        __fc = FeedbackConsistency(doc['exerciseId'])
        response = __fc.check_consistency(feedback_with_text_blocks=blocks)
        self.__logger.info("Response {}".format(response))
        resp.body = json.dumps(response, ensure_ascii=False)
        __fc.store_feedback()

        resp.status = HTTP_200
        self.__logger.info("Completed Feedback Comment Embedding Request.")
        self.__logger.debug("-" * 80)
