import mysql.connector
from mysql.connector import errorcode

#switcher dictionary for switching python types to valid MySql field types
typeSwitcher = {
        str: 'VARCHAR(2083)',
        float: 'FLOAT',
        int: 'FLOAT',
        bool: 'TINYINT'
    }

# TODO Change ProductDatabase to MySqlProductDatabase

class MySqlProductDatabase(object):

    db = mysql.connector
    cursor = None
    host = None
    user = None
    password = None
    databaseName = None
    tables = {}

    def __init__(self, host, user, password, buffered=True):
        '''
        On initialization, the credential information for connecting to the database are gathered
        and a connection is tried to be established to the MySql server
        Errors are raised if credentials are wrong or MySql server can't be connected to
        :param host: Host of the Database
        :param user: Username to use for connecting to database
        :param password: Password to use for connecting to database
        :param buffered: Specify if buffered or not. Defaulted to True
        '''
        try:
            self.db = mysql.connector.connect(
              host=host,
              user=user,
              password=password,
            )
            self.cursor = self.db.cursor(buffered=buffered)
            self.setDatabaseCredentials(host=host, user=user, password=password)
        except Exception as E:
            print(f"Connection could not be established. Error message: {E}")
            raise E

    def setDatabaseCredentials(self, host, user, password):
        '''
        Sets the database credentials, for further use
        :param host: host of the mySql database
        :param user: username
        :param password: password
        :return: void function
        '''
        self.host = host
        self.user = user
        self.password = password

    def connectToDb(self, databaseName, buffered=True):
        '''
        Connects to database and raises exception if for some reason connection
        can not be established
        :param databaseName: Name of the database
        :param buffered: Buffered or not
        :return: void function
        '''
        try:
            self.db = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=databaseName
            )
            self.cursor = self.db.cursor(buffered=buffered)
            self.databaseName = databaseName
            print(f"Succesfully established connection to {databaseName} on {self.host}")
            flag = True
        except Exception as E:
            print(f"Connection could not be established. Error message:\n{E}")
            raise E

    def createDatabaseIfNotExists(self, databaseName):
        '''
        Calls a query for creating databaseName database if not exists
        :param databaseName: Name of the database
        :return: void function
        '''
        #TODO: Handle the case when error is raised if the user does not have access
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {databaseName}")

    def createDatabase(self, databaseName):
        '''
        Calls a query to create a database using databaseName
        :param databaseName: Name of the database
        :return: void function
        '''
        self.cursor.execute(f"CREATE DATABASE {databaseName}")

    def createAndConnectToDb(self, databaseName, buffered):
        '''
        Attempts to connect to database (using connectToDb method)
        and if the connector raises the ER_BAD_DB_ERROR exception,
        creates the database and connects to it
        :param databaseName: Name of the database
        :param buffered: Buffered or not
        :return: void function
        '''
        try:
            self.connectToDb(databaseName, buffered=buffered)
        except mysql.connector.Error as err:
            if (err.errno == errorcode.ER_BAD_DB_ERROR):
                print("Database does not exist. Creating it..")
                self.createDatabase(databaseName)
                self.connectToDb(databaseName, buffered=buffered)
            else:
                print("Unexpected error occured while creating the database. ")
                raise

    def createTable(self, tableName, listOfFields):
        '''
        Creates a new table whose fields and fields type are containted in the additional argv
        :param tableName: Name of the table
        :param listOfFields: List of tuples that contains (name, type) values
        :return: void function
        '''
        #TODO: Check if table exists before creating
        # Create table customers
        self.cursor.execute(f"SHOW TABLES LIKE '{tableName}'")
        result = self.cursor.fetchone()
        if result:
            print("Table exists")
            self.tables[tableName] = listOfFields
        else:
            tableVars = ""
            for fieldTuple in listOfFields:
                fieldDict = dict(fieldTuple)
                tableVars += f"{fieldDict.get('NAME')} {fieldDict.get('TYPE')},"
            #get rid of last comma
            tableVars = tableVars[:-1]
            query = f"CREATE TABLE {tableName} ({tableVars})"
            self.cursor.execute(query)
            self.tables[tableName] = listOfFields

    def getDbFieldsFromObj(self, obj, *argv):
        '''
        Iterates over the attributes of an objects and extracts the attributes names and types
        Each attribute type is converted to a valid MySql field type
        str <-> VARCHAR(2083)
        (float || int) <-> FLOAT
        bool <-> TINYINT ( 0 or 1 )
        :param obj: Object from which the fields and fields types are wanted to be extracted
        :param argv: List of fields to exclude
        :return: List of tuples that contains (('NAME',name),('TYPE',type)) pairs where:
                    -> name -> Field Name
                    -> type -> Field Type
        '''
        fields=[]
        for k, v in obj.__dict__.items():
            if k in argv:
                continue
            varType = typeSwitcher.get(type(v), "str")
            fields.append((
                    ('NAME', k),
                    ('TYPE', varType)
                 ))
        return fields

    def insertValuesIntoTable(self, tableName, listOfTupleValues):
        '''
        Insert the values from listOfTupleValues list into the tableName
        :param tableName: Name of the table
        :param listOfTupleValues: List of tuples that contains the
                                  values that are needed to be added
                                  in the database table
        :return: void function
        '''
        fields = ""
        values = ""
        if not self.tables.get(tableName):
            print(f"The specified tableName {tableName} does not exists in the list of tables. List of tables: {self.tables}")
            raise
        for fieldTuple in self.tables[tableName]:
            fieldDict = dict(fieldTuple)
            fields += f"{fieldDict.get('NAME')},"
            values += f"%s, "
        fields = fields[:-1]
        values = values[:-2]
        query = f"INSERT INTO {tableName} ({fields}) VALUES ({values})"
        try:
            self.cursor.executemany(query, listOfTupleValues)
            self.db.commit()
            print(self.cursor.rowcount, "was inserted.")
        except Exception as E:
            print(f"The following query has errored out: {query}\nWhile adding the values: {listOfTupleValues}")
            print(E)
            raise

    def getAllTableValues(self, tableName):
        '''
        Returns all the table values
        :param tableName: Name of the table
        :return: All the values from the table
        '''
        selectQuery = f"SELECT * FROM {tableName}"
        try:
            self.cursor.execute(selectQuery)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            if(err.errno == errorcode.ER_BAD_TABLE_ERROR):
                print(f"Table {tableName} does not exist in the DB ( DB_NAME : {self.databaseName} )")
                print(err)
                raise
            else:
                print("Unknown error encountered.")
                print(err)
                raise
            return None
    def getTableValues(self, tableName, *argv):
        '''
        TODO: It should return the values from the table
        based on the *argv, somehow. Must decide exactly how
        :param tableName:
        :param argv:
        :return:
        '''
        pass

    def dropTableIfExits(self, tableName):
        '''
        Deletes the table if it exists
        :param tableName: Name of the table
        :return: void function
        '''
        self.cursor.execute(f"DROP TABLE IF EXISTS {tableName}")

    def dropDatabaseIfExits(self, dbName):
        '''
        Deletes the database if it exists
        :param dbName: Name of the database
        :return: void function
        '''
        self.cursor.execute(f"DROP DATABASE IF EXISTS {dbName}")
