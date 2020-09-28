import pymongo


# this class contains most of the important collection level pymongo operations but not all of them
# for the whole list and detailed explanations - https://api.mongodb.com/python/current/api/pymongo/collection.html
class Connection:

    def __init__(self):
        self.client = pymongo.MongoClient('database', 27017, username='embedding', password='embedding_password',
                                          authSource='athene_db')
        self.db = self.client["athene_db"]
        self.collection = None

    # inserts one document to a collection
    # collection {string} - collection name to store the document
    # document {field-value pairs} - e.g. {'x': 1, 'y': "apples"}
    def insert_document(self, collection, document):
        try:
            self.collection = self.db[collection]
            self.collection.insert_one(document)
        except Exception as e:
            raise e

    # inserts an array of documents to a collection
    # collection {string} - collection name to store the document
    # document {array} - e.g. [{'x': 1, 'y': "apples"}, {'x': 15, 'y': "oranges", 'z': 40.5}]
    def insert_documents(self, collection, documents: []):
        try:
            self.collection = self.db[collection]
            self.collection.insert_many(documents)
        except Exception as e:
            raise e

    # query database and returns results
    # filter_dict {field-value pairs} - specifies elements which must be present in the resulting set
    # projection {field-value pairs} - list of field names should be included or excluded in the resulting set. e.g. {‘_id’: False} _id values will be excluded in the resulting set
    # skip {int} - number of documents to omit (from the start of the result set) when returning the results
    # limit {int} - max number of results to return
    # max_time_ms {int} - Specifies a time limit for a query operation. If the specified time is exceeded, the operation will be aborted
    def find_documents(self, collection, filter_dict, projection=None, skip=0, limit=0, max_time_ms=None):
        try:
            self.collection = self.db[collection]
            docs = self.collection.find(filter=filter_dict, projection=projection, skip=skip, limit=limit,
                                        max_time_ms=max_time_ms)
        except Exception as e:
            raise e
        else:
            return docs

    # update a document matching the filter
    # filter_dict {field-value pairs} - find the document to update e.g. {'x': 1}
    # update_dict {field-value pairs} - modifications to apply e.g. {'$set': {'x': 3}}
    # upsert {boolean} - if true performs insert when no documents match the filter
    # Note: For the full list of update parameters https://docs.mongodb.com/manual/reference/operator/update/
    def update_document(self, collection, filter_dict, update_dict, upsert=False):
        try:
            self.collection = self.db[collection]
            result = self.collection.update_one(filter_dict, update_dict, upsert)
        except Exception as e:
            raise e
        else:
            return result

    # updates one or more documents matching the filter
    def update_documents(self, collection, filter_dict, update_dict, upsert=False):
        try:
            self.collection = self.db[collection]
            result = self.collection.update_many(filter_dict, update_dict, upsert)
        except Exception as e:
            raise e
        else:
            return result

    def replace_document(self, collection, filter_dict, replacement_dict, upsert=False):
        try:
            self.collection = self.db[collection]
            result = self.collection.replace_one(filter_dict, replacement_dict, upsert)
        except Exception as e:
            raise e
        else:
            return result

    # deletes one document matching the filter
    def delete_document(self, collection, filter_dict):
        try:
            self.collection = self.db[collection]
            result = self.collection.delete_one(filter_dict)
        except Exception as e:
            raise e
        else:
            return result

    # deletes one or more documents matching the filter
    def delete_documents(self, collection, filter_dict):
        try:
            self.collection = self.db[collection]
            result = self.collection.delete_many(filter_dict)
        except Exception as e:
            raise e
        else:
            return result

    # counts the number of documents in collection matching the filter
    def count_documents(self, collection, filter_dict):
        try:
            self.collection = self.db[collection]
            result = self.collection.count_documents(filter_dict)
        except Exception as e:
            raise e
        else:
            return result

    def get_collection_names(self):
        return self.db.collection_names()
