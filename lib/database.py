import sqlite3


class Database:
    def __init__(self, table_name="test", db_name="translation_memory.db"):
        try:
            self.db = sqlite3.connect(db_name)
            self.query_cursor = self.db.cursor()
            create_table_query = (
                "CREATE TABLE IF NOT EXISTS "
                + table_name
                + "(id TEXT NOT NULL, locale TEXT, project TEXT NOT NULL, translation TEXT, PRIMARY KEY(id, locale, project))"
            )
            self.create_table(create_table_query)
        except Exception as e:
            print(e)

    # Create table
    def create_table(self, query_string=None):
        try:
            if query_string:
                # CREATE TABLE IF NOT EXISTS stuffTOPlot(unix REAL,datestamp TEXT,keywork TEXT,value REAL
                self.query_cursor.execute(query_string)
            else:
                print("NO query string passed to create_table function.")
                return False

            return True
        except Exception as e:
            print(e)

    # Insert data into table
    def insert_into_table(self, query_string=None, params=None):
        try:
            if query_string:
                self.query_cursor.execute(query_string, params)
            else:
                print("No query string passed to read_from_table function.")
                return False
            self.db.commit()
            return True
        except Exception as e:
            print(e)

    # select query
    def read_from_table(self, query_string=None):
        try:
            if query_string:
                self.query_cursor.execute(query_string)
                return self.query_cursor.fetchall()
            else:
                print("No query string passed to read_from_table function.")
                return False
        except Exception as e:
            print(e)

    # # Example for input data using placeholders
    # def dynamic_data_entry(self):
    #     import time
    #     import datetime
    #     import random
    #
    #     unix = time.time()
    #     date = str(datetime.datetime.fromtimestamp(unix).strftime("%Y-%m-%d %H:%M:%S"))
    #     keyword = "Python"
    #     value = random.randrange(0, 10)
    #     self.query_cursor.execute("INSERT INTO stuffTOPlot(unix,datestamp,keywork,value) VALUES(?,?,?,?)",(unix, date, keyword, value))
    #     self.db.commit()

    def __del__(self):
        try:
            self.query_cursor.close()
            self.db.close()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    obj = Database()
    # obj.create_table()
    # obj.insert_into_table("INSERT INTO stuffTOPlot VALUES(145232323,'2016-01-10','Vishal VVR',2)")

    # obj.data_entry()
    # obj.dynamic_data_entry()
    data = obj.read_from_table("select * from stuffTOPlot")
    for i in data:
        print("{} :: {} :: {} :: {}".format(i[0], i[1], i[2], i[3]))
