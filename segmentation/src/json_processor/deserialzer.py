from src.errors import typeError, keyError


def load_submissions_from_json(input_json):
    """Converts submissions from json to python

    :param input_json: input with submissions, optionally with keywords
    :return:
    """
    try:
        submissions_from_json = {}
        for submission in input_json['submissions']:
            submissions_from_json[submission["id"]] = submission["text"]
        return submissions_from_json
    except TypeError:
        raise typeError
    except KeyError:
        raise keyError


def load_feedback_from_json(input_json):
    """Converts feedback form json to python

    :param input_json: input with feedback
    :return:
    """
    try:
        feedback_from_json = {}
        for feedback in input_json['feedback']:
            feedback_from_json[feedback["id"]] = feedback["text"]
        return feedback_from_json
    except TypeError:
        raise falcon.HTTPBadRequest("TypeError: Could not deserialize to_segment",
                                    "Provide array to_segment with {\"id\": ..., \"text\": ...}")
    except KeyError:
        raise falcon.HTTPBadRequest("KeyError: Could not deserialize to_segment",
                                    "Provide array to_segment with {\"id\": ..., \"text\": ...}")


def load_keywords_from_json(input_json):
    """Converts keywords from json to python

    :param input_json: json input with "keywords" array
    :return: keywords converted to python
    """
    return input_json["keywords"]
