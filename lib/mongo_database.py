from pymongo import MongoClient
import json


class MongoDatabase(json.JSONEncoder):
    def __init__(self, tablename=None, dbname="translation_memory"):
        self.connect(tablename=tablename, dbname=dbname)

    def connect(self, tablename=None, dbname="translation_memory"):
        self.client = MongoClient()
        self.db = self.client[dbname]
        if tablename:
            self.collection = self.db[tablename]

    # Module will insert documents into the collection
    def insert_document(self, document, collection=None):
        try:
            # collection selection
            if not collection:
                collection = self.collection
            else:
                collection = self.db[collection]

            # insert query depending on type passed
            if isinstance(document, list):
                collection.insert_many(document)
            elif isinstance(document, dict):
                collection.insert(document)
            else:
                print("invalid document type passed to insert function")

        except Exception as e:
            print(e)

    # Module will return list of all the documents in collection provided
    def list_all_documents(self, collection=None):
        try:
            if not collection:
                collection = self.collection
            else:
                collection = self.db[collection]

            cursor = list(collection.find({}))
            return cursor
        except Exception as e:
            print(e)

    def list_some_data(self, collection=None):
        try:
            pass
        except Exception as e:
            print(e)


if __name__ == "__main__":
    obj = MongoDatabase(tablename="test11111")
    obj.insert_document(
        collection="vishal", document=[{"name": "vishal"}, {"name2": "vvqeqwer"}]
    )
    print(obj.list_all_documents("vishal"))
