import falcon
import json
from src.validator.confidence_calculator import calculate_confidence


class Resource:

    def on_post(self, request, response):
        data = json.load(request.stream)

        if 'candidate' not in data:
            raise falcon.HTTPBadRequest('Candidate not in data')
        elif 'references' not in data:
            raise falcon.HTTPBadRequest('References not in data')
        else:
            candidate = data['candidate']
            references = data['references']
            if len(references) < 2:
                raise falcon.HTTPBadRequest('Need at least 2 refeerences')
            else:
                confidence = calculate_confidence(candidate, references)
                result = {
                    "confidence": confidence
                }
                response.body = json.dumps(result)


app = application = falcon.API()
app.add_route('/validate', Resource())
