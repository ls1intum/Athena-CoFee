import re
import nltk
from nltk.stem.porter import PorterStemmer


def __segmentation_helper(sentences, sentences_index):
    """Split sentences on newline and long (>20 words) sentences on connector word

    :param sentences: sentences to be split
    :return: new_sentences: newly found sentences
    """
    new_sentences = sentences

    # \n new_sentences counter
    # different from i because newlines are skipped
    segment_counter = 0

    for i in range(len(sentences)):

        if ("\n" in sentences[i]) or (len(sentences[i].split()) > 20):
            current_sentence = sentences[i]
            if (len(sentences[i].split()) > 20) and (
                    re.search(r" (?P<connector>while|however|but|whereas|such as|for example)", sentences[i])):
                current_sentence = re.sub(r" (?P<connector>while|however|but|whereas|such as|for example)",
                                          lambda m: " ⇥" + m.group("connector"),
                                          current_sentence)
            split_on_connector = current_sentence.split("⇥")
            split_on_newline = [re.split("(\n)", part_sentence) for part_sentence in split_on_connector]

            flattened_result = [y for x in split_on_newline for y in x]
            split_result = list(filter(None, flattened_result))

            # count offset if new lines precede
            newlines_preceded = 0

            # insert the new sentences, add the indices
            for part_sentence_index in range(len(split_result)):
                part_sentence = split_result[part_sentence_index]

                # replace the sentences and the indices if it's the first split result
                # insert sentence and indices else
                if part_sentence != "\n":
                    if part_sentence_index == 0 or newlines_preceded == part_sentence_index:
                        new_sentences[segment_counter] = part_sentence
                        sentences_index[segment_counter] = (
                            sentences_index[segment_counter][0] + newlines_preceded,
                            sentences_index[segment_counter][0] + len(part_sentence) + newlines_preceded)
                    else:
                        new_sentences.insert(segment_counter, part_sentence)
                        sentences_index.insert(
                            segment_counter,
                            (sentences_index[segment_counter - 1][1] + newlines_preceded,
                             sentences_index[segment_counter - 1][1] + len(part_sentence) + newlines_preceded))
                    newlines_preceded = 0
                    segment_counter += 1
                else:
                    newlines_preceded += 1

        else:
            if sentences[i] != "\n":
                segment_counter += 1

    return new_sentences, sentences_index


def segment_data(dataset, keywords):
    """Splits documents in dataset into text blocks

    :param dataset: documents (answers) to be split
    :param keywords: keywords extracted from a preprocessed corpus
    :return: dictionary of id: startIndex, endIndex
    """
    punkt_param = nltk.tokenize.punkt.PunktParameters()
    abbreviation = ['etc', 'e.g', 'fig', 'i.e', 'ex']
    punkt_param.abbrev_types = set(abbreviation)
    tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer(punkt_param)
    segmentation_result = {}

    # Stemming the keywords to find "similarit" instead of "similarity"
    ps = PorterStemmer()
    keywords = [ps.stem(k) for k in keywords]
    # remove duplicates
    keywords = list(set(keywords))

    for submission_id, submission_text in dataset.items():

        # fetch document for which keywords need to be extracted
        original_doc = submission_text

        # delete point after enumeration or a. b. c., instead )
        original_doc = re.sub(r"(\n|^)(\s*)([a-zA-Z1-9)])(\.)", r"\1\2\3)", original_doc)

        sentences = list(tokenizer.tokenize(original_doc))
        sentences_index = list(tokenizer.span_tokenize(original_doc))

        sentences, sentences_index = __segmentation_helper(sentences, sentences_index)

        segment_index = []
        first_text_block_found = False
        keywords_found = ""

        # merge on topic shifts: search for keywords and compare them
        for i in range(len(sentences)):
            keywords_of_previous_segment = keywords_found
            keywords_found = ""

            for key in keywords:
                # if a new keyword is found or it's the first sentence
                # Do not consider a one- or two-word block as a text block,
                # as these are usually "headings" and often contain
                # the subject of the next sentence (-> part of the next segment)
                # skip the \n lines
                keyword_flag = re.search(r"(\n| |^|-|>|\)|\.)(?i)" + key, sentences[i])

                if keyword_flag and (len(sentences[i].split()) > 2):
                    if keyword_flag:
                        keywords_found += " " + key

            # start a text block if new keywords are found or no textblock was started yet
            if (keywords_of_previous_segment != keywords_found and keywords_of_previous_segment != "") \
                    or not first_text_block_found:
                if first_text_block_found:
                    segment_index.append(sentences_index[i - 1][1])
                segment_index.append(sentences_index[i][0])
                first_text_block_found = True

        if segment_index:
            segment_index.append(sentences_index[len(sentences) - 1][1])
            tuple_segmentation_result = []
            i = 0
            while i < len(segment_index) - 1:
                tuple_segmentation_result.append((segment_index[i], segment_index[i + 1]))
                i = i + 2
            segmentation_result[submission_id] = tuple_segmentation_result
        else:
            segmentation_result[submission_id] = [(0, 0)]

    return segmentation_result


def segment_feedback_data(dataset):
    """Splits documents in dataset into text blocks

    :param dataset: documents (answers) to be split
    :param keywords: keywords extracted from a preprocessed corpus
    :return: dictionary of id: startIndex, endIndex
    """
    punkt_param = nltk.tokenize.punkt.PunktParameters()
    abbreviation = ['etc', 'e.g', 'fig', 'i.e', 'ex']
    punkt_param.abbrev_types = set(abbreviation)
    tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer(punkt_param)
    segmentation_result = {}

    for feedback_id, feedback_text in dataset.items():

        # fetch document for which keywords need to be extracted
        original_doc = feedback_text

        # delete point after enumeration or a. b. c., instead )
        original_doc = re.sub(r"(\n|^)(\s*)([a-zA-Z1-9)])(\.)", r"\1\2\3)", original_doc)

        sentences = list(tokenizer.tokenize(original_doc))
        sentences_index = list(tokenizer.span_tokenize(original_doc))
        sentences, sentences_index = __segmentation_helper(sentences, sentences_index)

        tuple_segmentation_result = []
        for index in sentences_index:
            tuple_segmentation_result.append((index[0], index[1]))
        segmentation_result[feedback_id] = tuple_segmentation_result

    return segmentation_result
