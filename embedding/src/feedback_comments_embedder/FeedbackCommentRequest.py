import json
from logging import getLogger
from falcon import Request, Response, HTTP_200
from src.elmo import ELMo
from src.errors import emptyBody, requireTextBlocks, requireFeedback
from src.entities import FeedbackWithTextBlock, Feedback
from src.feedback_comments_embedder.FeedbackCommentResource import FeedbackCommentResource


class FeedbackCommentRequest:
    __elmo: ELMo = None
    __fcr = FeedbackCommentResource()
    __logger = getLogger(__name__)

    def on_post(self, req: Request, resp: Response) -> None:
        self.__logger.debug("-" * 80)
        self.__logger.info("Start processing Feedback Comment Embedding Request:")
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

        response = "success" if self.__fcr.store_feedback(feedback_with_tb=blocks) else "failure"

        resp.body = json.dumps(response, ensure_ascii=False)

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = HTTP_200
        self.__logger.info("Completed Embedding Request.")
        self.__logger.debug("-" * 80)
