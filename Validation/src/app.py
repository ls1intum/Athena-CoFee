import falcon
import json
from src.validator.confidence_calculator import calculate_confidence


class Resource:

    def on_post(self, request, response):
        """
        POST request for calculating the confidence of an automatic feedback
        :param request: request containg a candidate and the references
        :param response: response containg the confidence as number between 0 and 100
        """
        data = json.load(request.stream)

        if 'candidate' not in data:
            raise falcon.HTTPBadRequest('Candidate not in data')
        elif 'references' not in data:
            raise falcon.HTTPBadRequest('References not in data')
        else:
            candidate = data['candidate']
            references = data['references']
            if len(references) < 2:
                raise falcon.HTTPBadRequest('Need at least 2 references')
            else:
                confidence = calculate_confidence(candidate, references)
                result = {
                    "confidence": confidence
                }
                response.body = json.dumps(result)


app = application = falcon.API()
app.add_route('/validate', Resource())
