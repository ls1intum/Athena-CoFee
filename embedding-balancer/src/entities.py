from numpy import array

Word = str
Sentence = str
ElmoVector = array

class Embedding:
    id: str
    vector: ElmoVector

    def __init__(self, id: str, vector: ElmoVector):
        self.id = id
        self.vector = vector
    
    @classmethod
    def from_dict(cls, dict: dict) -> 'Embedding':
        return cls(dict['id'], dict['vector'])

class ComputeNode:
    name: str                       # Can be chosen freely (Appears in log)
    url: str                        # URL of the embedding-API
    chunk_size: int                 # Maximum supported chunk size (normally limited by RAM/GPU-Memory)
    chunk_quantity: int             # Amount of blocks being assigned to the compute node
    blocks: []                      # Specific blocks which should be processed by the compute node
    compute_power: float            # Influences the distribution of blocks (affecting calculation part)
    communication_cost: float       # Influences the distribution of blocks (affecting overhead for computation)

    def __init__(self, name: str, url: str, chunk_size: int, compute_power: float, communication_cost: float):
        self.name = name
        self.url = url
        self.compute_power = compute_power
        self.chunk_size = chunk_size
        self.communication_cost = communication_cost

    def __str__(self):
        return "Name: " + self.name + ", URL: " + self.url + ", Chunk Size: " + str(self.chunk_size) + ", Compute Power: " + str(self.compute_power) + ", Communication Cost: " + str(self.communication_cost)
