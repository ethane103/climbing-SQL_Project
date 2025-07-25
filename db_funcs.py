import pyodbc
import pandas as pd 
from dotenv import load_dotenv
import os

class managedConnection():
    def __init__(self):
        self.cnxn = self.connect()
        self.lastquery = None

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

        self.lastquery = query
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

    def getWalls(self, args = {}, returnQuery = False):
        query = """
        SELECT 
               walls.id AS wall_id,
               gyms.name AS gym_name,
               gyms.id AS gym_id,
               walls.name AS name,
               walls.rating,
               walls.difficulty
        FROM walls
        INNER JOIN gyms ON walls.gym = gyms.id
        """

        andWhere = 'WHERE'
        for key, value in args.items():
            match key:
                case 'holdCons':
                    for idx, (hold, state) in enumerate(value.items()):
                        match state:
                            case 'HAS':
                                yesNo = ''
                            case '!HAS':
                                yesNo = ' NOT'
                            case _:
                                yesNo = ''
                        query = query + f"""{andWhere}{yesNo} EXISTS (
                                            SELECT 1 FROM
                                                wall_holds
                                            INNER JOIN holds ON wall_holds.hold_id = holds.id
                                            WHERE
                                                walls.id = wall_holds.wall_id
                                            AND
                                                holds.name = '{hold}')
                                            """
                        andWhere = 'AND'
                        
                case 'difficulties':
                    innerstring = "','".join(value)
                    diffString = f"('{innerstring}')"
                
                    query = query + f"{andWhere} walls.difficulty IN {diffString} \n"
                    andWhere = 'AND' 
                
                case 'gym_id':
                    query = query + f"{andWhere} gyms.id = {value} \n"
                        
        query = query + """ORDER BY walls.rating DESC, gyms.name, walls.id"""
        print(query)
        walls = self.mC.execute(query)

        returnVal = walls
        if returnQuery:
            returnVal = (walls, query)
        return returnVal

    def getHolds(self):
        query = "SELECT id, name FROM holds"
        holds = self.mC.execute(query)
        return holds
    
    def getGyms(self):
        query = "SELECT id, name, state, city, zipcode, address FROM gyms"
        gyms = self.mC.execute(query)
        return gyms