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


def load_keywords_from_json(input_json):
    """Converts keywords from json to python

    :param input_json: json input with "keywords" array
    :return: keywords converted to python
    """
    return input_json["keywords"]
