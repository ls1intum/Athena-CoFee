class TextBlock:
    __last_id = 0

    def __init__(self, text, id=None):
        self.text = text
        if id is None:
            __last_id = TextBlock.__last_id + 1
            self.id = __last_id
        else:
            self.id = id
            TextBlock.__last_id = id

    def __str__(self):
        self.text.__str__()

    def json_rep(self):
        return {
            'id': self.id,
            'text': self.text
        }

    @staticmethod
    def from_sentences(sentences):
        return [TextBlock(sentence) for sentence in sentences]
