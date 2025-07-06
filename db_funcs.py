import pyodbc
import pandas as pd 
from dotenv import load_dotenv
import os

class managedConnection():
    def __init__(self):
        self.cnxn = self.connect()

    def execute(self, query, returnType = 'df'):
        cursor = self.cnxn.cursor()
        cursor.execute(query)
        cols = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        match(returnType):
            case 'df':
                df = pd.DataFrame.from_records(data = rows, columns=cols)
                df.set_index(cols[0], inplace = True)
                returnVal = df
            case 'plain':
                returnVal = rows
            case 'None':
                returnVal = None
            case _:
                raise ValueError("Your query passed to execute (in db_funcs) does not match any of the valid cases {'df', 'plain', 'None'}")
        
        cursor.close()
        del(cursor)
        return returnVal

    def connect(self):
        load_dotenv()
        USER = os.getenv("DB_USER")
        PASSWORD = os.getenv("DB_PASSWORD")
        DB_NAME = os.getenv("DB_NAME")

        cnxn = pyodbc.connect("DRIVER={MySQL ODBC 9.3 Unicode Driver};"
                                "SERVER=localhost;" 
                                f"DATABASE={DB_NAME};"
                                f"USER={USER};"
                                f"PASSWORD={PASSWORD};"
                                "PORT=3306;"
                                "OPTION=3;")

        self.cnxn = cnxn
        return cnxn

class autoQuery():
    def __init__(self):
        self.mC = managedConnection()

    def getWalls(self, args = {}):
        baseQuery = """
        SELECT 
               walls.id AS wall_id,
               gyms.name AS gym_name,
               walls.name AS name,
               walls.rating,
               walls.difficulty
        FROM walls
        INNER JOIN gyms ON walls.gym = gyms.id
        ORDER BY walls.rating DESC, gyms.name, walls.id
        """
        walls = self.mC.execute(baseQuery)
        return walls

    def getHolds(self):
        query = "SELECT * FROM holds"
        holds = self.mC.execute(query)
        return holds