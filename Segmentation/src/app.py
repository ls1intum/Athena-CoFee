from src.json_processor.serializer import load_result_to_json
from src.text_processor.data_cleaner import clean_data
from src.json_processor.deserialzer import load_submissions_from_json, load_keywords_from_json
from src.text_processor.keyword_extractor import get_top_n_words
from src.segmentor.segmentor import segment_data
import falcon
import json
import nltk


class ObjRequestClass:

    def on_post(self, req, resp):
        """Gets a POST request with TextSubmissions and optionally with keywords

        :param req: request with {"submissions":[{id:,text:}],"keywords":[]}
        :param resp: response with {"keywords":[],"textBlocks":[{id:,startIndex:,endIndex}]}
        :return:
        """
        data = json.load(req.stream)

        if "submissions" not in data:
            raise falcon.HTTPBadRequest("Submissions not found",
                                        "Provide an array \"submissions\" with {id.., text: ..}")
        else:
            if "keywords" not in data:
                submissions = load_submissions_from_json(data)
                if len(submissions) < 10:
                    raise falcon.HTTPBadRequest(
                        "Too few submissions",
                        "To calculate new keywords at least 10 submissions are expected")
                corpus = clean_data(submissions)
                keywords = get_top_n_words(corpus, 10)
                segmentation_result = segment_data(submissions, keywords)
                output = load_result_to_json(keywords, segmentation_result)
            else:
                keywords = load_keywords_from_json(data)
                submissions = load_submissions_from_json(data)
                segmentation_result = segment_data(submissions, keywords)
                output = load_result_to_json(keywords, segmentation_result)
        resp.body = json.dumps(output)


nltk.data.path.append('src/lib/nltk_data')
api = application = falcon.API()
api.add_route("/segment", ObjRequestClass())

