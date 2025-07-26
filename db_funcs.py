import pyodbc
import pandas as pd 
from dotenv import load_dotenv
import os
from textwrap import dedent as dd


# A connection manager which centralizes the logic to pass queries to the SQL db through one connection
class managedConnection():
    # Track last query, and hook to a potential tracker (In our case see app_views.sql_viewer, but this could be logging or a meta class which further disseminates the query)
    def __init__(self, cmdTracker = None):
        self.cnxn = self.connect()
        self.lastquery = None
        self.cmdTracker = cmdTracker

    # Execute a query, allows you to select how you would like to recieve the SQL output, each query is given it's own single use cursor. Passes the query to the tracker.
    def execute(self, query, returnType = 'df'):
        # Generate cursor, execute query, get results.
        cursor = self.cnxn.cursor()
        cursor.execute(query)

        cols = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        # Return the results in favored format, dataframe, raw text or no return.
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
        
        # Clear cursor
        cursor.close()
        del(cursor)

        # Track
        if not self.cmdTracker is None:
            self.cmdTracker.track(query)
        
        # Return
        return returnVal

    # Connect to a database, using the credentials and databse name stored in the .env file.
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
    
    # Post creation, set or change the tracker.
    def setTracker(self, cmdTracker):
        self.cmdTracker = cmdTracker


# Automatic query generation for the SQL frontend. In a full implementation this would likely be broken down into subclasses by query type, and feature more helper methods.
class autoQuery():
    # We want all of our queries for a run to go through one connection to save resources and centralize tracking
    singleConnect = managedConnection()

    # Initialize
    def __init__(self):
        self.mC = self.singleConnect

    # Wall query generation, takes args from app_views in form of a dict. Optionally returns query.
    def getWalls(self, args = {}, returnQuery = False):
        # Generate query stem, getting the desired info on a wall from the join of the gyms table and the walls table
        query = dd("""\
        SELECT 
               walls.id AS wall_id,
               gyms.name AS gym_name,
               gyms.id AS gym_id,
               walls.name AS name,
               walls.rating,
               walls.difficulty
        FROM walls
        INNER JOIN 
            gyms 
        ON 
            walls.gym = gyms.id
        """)

        # Generate additional query specification based on the dictionary, by case matching the dict keys.
        andWhere = 'WHERE'  # Make the first specification use the WHERE keyword, but allow all later specifications to use AND
        for key, value in args.items():
            match key:
                # If the dict entry specifies hold types, check for each wall, using a correlated subquery, if a link exists between that wall_id and the hold_id in the wall_holds junction table
                case 'holdCons':
                    for idx, (hold, state) in enumerate(value.items()):
                        match state:
                            case 'HAS':
                                yesNo = ''
                            case '!HAS':
                                yesNo = ' NOT'
                            case _:
                                yesNo = ''
                        query = query + dd(f"""\

                                            {andWhere}{yesNo} EXISTS (
                                                SELECT 1 FROM
                                                    wall_holds
                                                INNER JOIN 
                                                    holds 
                                                ON 
                                                    wall_holds.hold_id = holds.id
                                                WHERE
                                                    walls.id = wall_holds.wall_id
                                                AND
                                                    holds.name = '{hold}'
                                            )
                                            """)
                        # Force any future query specifications in the same query to use AND instead of where
                        andWhere = 'AND'
                
                # If the dict entry specifies difficulties use a correlated subquery to check if each walls difficulty is in the acceptable list 
                case 'difficulties':
                    # Generate a string in SQL format that lists acceptable difficulties from the list
                    innerstring = "','".join(value)
                    diffString = f"('{innerstring}')"
                
                    # create query specification
                    query = query + f"{andWhere} walls.difficulty IN {diffString} \n"

                    # Force any future query specifications in the same query to use AND instead of where
                    andWhere = 'AND' 
                
                # Simply check if the walls gym foreign key links to the specified gym
                case 'gym_id':
                    query = query + f"{andWhere} gyms.id = {value} \n"

                    # Force any future query specifications in the same query to use AND instead of where
                    andWhere = 'AND' 

        # Finally add ordering logic which comes at the bottom of the page, ordering primarily by rating                
        query = query + """ORDER BY walls.rating DESC, gyms.name, walls.id"""

        # Execute the query using the managedConnection, and return the relevant dataframe. (dataframe, string) tuple if query return is on
        walls = self.mC.execute(query)

        returnVal = walls
        if returnQuery:
            returnVal = (walls, query)
        return returnVal

    # Get the id and name for each hold
    def getHolds(self):
        query = "SELECT id, name FROM holds"
        holds = self.mC.execute(query)
        return holds
    
    # Get info on each gym
    def getGyms(self):
        query = "SELECT id, name, state, city, zipcode, address FROM gyms"
        gyms = self.mC.execute(query)
        return gyms
    
    # Static method which returns the shared managedConnection
    @classmethod
    def getMC(cls):
        return cls.singleConnect