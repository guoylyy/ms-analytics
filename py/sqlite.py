import sqlite3

class SqliteService:
    """Persistent data of ms analysis tool
    Author:
        Yiliangg(Guo.Yiliang@morganstanley.com) 
    Update:
        2014-07-20
    """
    db_name = "ms.db"
    conn = None
    def __init__(self):
        """Initial the connect required object"""
        self.conn = sqlite3.connect(self.db_name)
        self.__create_tables()
        print("start to initalize database")
    
    def __check_tables(self):
        return True

    def __create_tables(self):
        cursor = self.conn.cursor()
        print(cursor.execute('create table user (id varchar(20) primary key, name varchar(20))'))
        return True 

    def store_middle_data(self):
        cursor = self.conn.cursor()
        return True

    def store_raw_data(self):
        return True

    def check_data_comsistence(self):
        return True    

if __name__ == '__main__':
    print("start script") 
    service = SqliteService();
    

class RawData:
    def __init___(self):
        self.date = ""
        self.me = ""
        self.transaction = ""
        self.memos = ""

    def geter(self,para):
        return self.date
    
    def seter(self,para,val):
        self.para = val


