from numpy import array

Word = str
Sentence = str
ElmoVector = array

class TextBlock:
    id: str
    text: Sentence

    def __init__(self, id: str, text: Sentence = None):
        self.id = id
        if text is not None:
            self.text = text
    
    @classmethod
    def from_dict(cls, dict: dict) -> 'TextBlock':
        return cls(dict['id'], dict['text'])

class Embedding:
    id: str
    vector: ElmoVector

    def __init__(self, id: str, vector: ElmoVector):
        self.id = id
        self.vector = vector
    
    @classmethod
    def from_dict(cls, dict: dict) -> 'Embedding':
        return cls(dict['id'], dict['vector'])
