def load_result_to_json(keywords, segmentation_result):
    """Function that converts the segmentation results (keywords and text blocks) into json

    :param keywords: resulting or put keywords
    :param segmentation_result: resulting text blocks
    :return: result in json
    """
    id_segment = []
    for id, segments in segmentation_result.items():
        for segment in segments:
            id_segment.append({"id": id, "startIndex": segment[0], "endIndex": segment[1]})
    output = {
        "keywords": keywords,
        "textBlocks": id_segment
    }
    return output
