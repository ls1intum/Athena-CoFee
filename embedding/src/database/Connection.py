import pymongo


class Connection:

    def __init__(self):
        self.client = pymongo.MongoClient('database', 27017, username='embedding', password='embedding_password')
        # self.client = pymongo.MongoClient('localhost', 27017, username='user1', password='user1_password', authSource='athene_db')
        self.db = self.client["athene_db"]
        self.collection = None

    def insert_document(self, collection, document):
        try:
            self.collection = self.db[collection]
            self.collection.insert_one(document)
        except Exception as e:
            print(e)

    def insert_documents(self, collection, documents: []):
        try:
            self.collection = self.db[collection]
            self.collection.insert_many(documents)
        except Exception as e:
            print(e)

    def find_documents(self, collection, filter_dict, projection=None, skip=0, limit=0, max_time_ms=None):
        try:
            self.collection = self.db[collection]
            docs = self.collection.find(filter=filter_dict, projection=projection, skip=skip, limit=limit, max_time_ms=max_time_ms)
        except Exception as e:
            print(e)
        else:
            return docs

    def update_document(self, collection, filter_dict, update_dict, upsert=False):
        try:
            self.collection = self.db[collection]
            result = self.collection.update_one(filter_dict, update_dict, upsert)
        except Exception as e:
            print(e)
        else:
            return result

    def update_documents(self, collection, filter_dict, update_dict, upsert=False):
        try:
            self.collection = self.db[collection]
            result = self.collection.update_many(filter_dict, update_dict, upsert)
        except Exception as e:
            print(e)
        else:
            return result

    def delete_document(self, collection, filter_dict):
        try:
            self.collection = self.db[collection]
            result = self.collection.delete_one(filter_dict)
        except Exception as e:
            print(e)
        else:
            return result

    def delete_documents(self, collection, filter_dict):
        try:
            self.collection = self.db[collection]
            result = self.collection.delete_many(filter_dict)
        except Exception as e:
            print(e)
        else:
            return result

    def count_documents(self, collection, filter_dict):
        try:
            self.collection = self.db[collection]
            result = self.collection.count_documents(filter_dict)
        except Exception as e:
            print(e)
        else:
            return result

    def get_collection_names(self):
        return self.db.collection_names()
