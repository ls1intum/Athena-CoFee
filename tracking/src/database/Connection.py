import os
import pymongo
import pandas as pd


# this class contains most of the important collection level pymongo operations but not all of them
# for the whole list and detailed explanations - https://api.mongodb.com/python/current/api/pymongo/collection.html
class Connection:

    def __init__(self):
        # Get container variables for datbase connection
        dbhost = str(os.environ['DATABASE_HOST']) if "DATABASE_HOST" in os.environ else "database"
        dbport = int(os.environ['DATABASE_PORT']) if "DATABASE_PORT" in os.environ else 27017
        dbname = str(os.environ['DATABASE_NAME']) if "DATABASE_NAME" in os.environ else "athene_db"
        dbuser = str(os.environ['TRACKING_DATABASE_USER']) if "TRACKING_DATABASE_USER" in os.environ else "tracking"
        dbpwd = str(os.environ['TRACKING_DATABASE_PWD']) if "TRACKING_DATABASE_PWD" in os.environ else "tracking_password"
        self.client = pymongo.MongoClient(host=dbhost, port=dbport, username=dbuser, password=dbpwd,
                                          authSource=dbname)
        self.db = self.client[dbname]
        self.collection = None

    # inserts one document to a collection
    # collection {string} - collection name to store the document
    # document {field-value pairs} - e.g. {'x': 1, 'y': "apples"}
    def insert_document(self, collection: str, document: dict):
        self.collection = self.db[collection]
        self.collection.insert_one(document)

    # inserts an array of documents to a collection
    # collection {string} - collection name to store the document
    # document {array} - e.g. [{'x': 1, 'y': "apples"}, {'x': 15, 'y': "oranges", 'z': 40.5}]
    def insert_documents(self, collection: str, documents: [dict]):
        try:
            self.collection = self.db[collection]
            self.collection.insert_many(documents)
        except Exception as e:
            print(e)

    # query database and returns results
    # filter_dict {field-value pairs} - specifies elements which must be present in the resulting set
    # projection {field-value pairs} - list of field names should be included or excluded in the resulting set. e.g. {‘_id’: False} _id values will be excluded in the resulting set
    # skip {int} - number of documents to omit (from the start of the result set) when returning the results
    # limit {int} - max number of results to return
    # max_time_ms {int} - Specifies a time limit for a query operation. If the specified time is exceeded, the operation will be aborted
    def find_documents(self, collection: str, filter_dict: dict, projection: dict = None, skip: int = 0, limit: int = 0,
                       max_time_ms: int = None):
        try:
            self.collection = self.db[collection]
            docs = self.collection.find(filter=filter_dict, projection=projection, skip=skip, limit=limit,
                                        max_time_ms=max_time_ms)
        except Exception as e:
            print(e)
        else:
            return docs

    # update a document matching the filter
    # filter_dict {field-value pairs} - find the document to update e.g. {'x': 1}
    # update_dict {field-value pairs} - modifications to apply e.g. {'$set': {'x': 3}}
    # upsert {boolean} - if true performs insert when no documents match the filter
    # Note: For the full list of update parameters https://docs.mongodb.com/manual/reference/operator/update/
    def update_document(self, collection: str, filter_dict: dict, update_dict: dict, upsert: bool = False):
        try:
            self.collection = self.db[collection]
            result = self.collection.update_one(filter_dict, update_dict, upsert)
        except Exception as e:
            print(e)
        else:
            return result

    # updates one or more documents matching the filter
    def update_documents(self, collection: str, filter_dict: dict, update_dict: dict, upsert: bool = False):
        try:
            self.collection = self.db[collection]
            result = self.collection.update_many(filter_dict, update_dict, upsert)
        except Exception as e:
            print(e)
        else:
            return result

    # deletes one document matching the filter
    def delete_document(self, collection: str, filter_dict: dict):
        try:
            self.collection = self.db[collection]
            result = self.collection.delete_one(filter_dict)
        except Exception as e:
            print(e)
        else:
            return result

    # deletes one or more documents matching the filter
    def delete_documents(self, collection: str, filter_dict: dict):
        try:
            self.collection = self.db[collection]
            result = self.collection.delete_many(filter_dict)
        except Exception as e:
            print(e)
        else:
            return result

    # counts the number of documents in collection matching the filter
    def count_documents(self, collection: str, filter_dict: dict):
        try:
            self.collection = self.db[collection]
            result = self.collection.count_documents(filter_dict)
        except Exception as e:
            print(e)
        else:
            return result

    def get_collection_names(self):
        return self.db.collection_names()

    def get_data_for_evaluation(self, exercise_id: int):
        try:
            self.collection = self.db.feedback
            pipeline = [
                {'$match': {"participation.exercise.id": exercise_id}},
                {"$unwind": {'path': '$participation.results', 'preserveNullAndEmptyArrays': True}},
                {'$unwind': {'path': '$participation.results.feedbacks', 'preserveNullAndEmptyArrays': True}},
                {'$project': {
                    'ID': '$ID',
                    'pID': '$participation.id',
                    'feedbacks': '$participation.results.feedbacks'
                }},
            ]

            # df = pd.json_normalize(collection.find({"participation.exercise.id": 1830}, {"participation.results": 1}))
            query_result = self.collection.aggregate(pipeline)
            query_result = list(query_result)
            df = pd.json_normalize(query_result)

            if len(df.index) == 0:
                print(f'Exercise {exercise_id} was not tracked!')
                return

            # sort feedback by textblock reference
            df = df.sort_values('feedbacks.reference')

            # remove newline characters from feedbacks to prevent csv from breaking
            df = df.replace('\n', ' ', regex=True)

            # write dataframe to csv
            pd.DataFrame.to_csv(df, './similarity.csv', ';')

            return df
        except Exception as e:
            print(e)
        else:
            return result
