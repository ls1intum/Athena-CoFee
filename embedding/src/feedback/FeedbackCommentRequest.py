import json
from logging import getLogger
from falcon import Request, Response, HTTP_200, HTTP_204
from src.errors import emptyBody, requireTextBlocks, requireFeedback
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
        if "text_blocks" not in doc:
            self.__logger.error("{} ({})".format(requireTextBlocks.title, requireTextBlocks.description))
            raise requireTextBlocks

        if "feedback" not in doc:
            self.__logger.error("{} ({})".format(requireFeedback.title, requireFeedback.description))
            raise requireFeedback

        blocks: list[FeedbackWithTextBlock] = []

        for f in doc['feedback']:
            for b in doc['text_blocks']:
                if f['reference'] == b['reference']:
                    blocks.append(FeedbackWithTextBlock.from_dict(b, Feedback.from_dict(f)))
                    break

        __fc = FeedbackConsistency()
        response = __fc.check_consistency(feedback_with_text_blocks=blocks)
        resp.body = json.dumps(response, ensure_ascii=False)
        __fc.store_feedback()

        resp.status = HTTP_200 if response else HTTP_204

        self.__logger.info("Completed Feedback Comment Embedding Request.")
        self.__logger.debug("-" * 80)
