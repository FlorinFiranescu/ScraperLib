from MySqlProductDatabase import *
from ProductTable import *
class ProductDatabase(object):
    productDb = None
    host = None
    user = None
    password = None

    listOfProductTables = []
    #TODO: Use tableName to define the ProductTable
    # Have a MySqlProductDatabase that contains multiple ProductTables
    tableName = ""
    #TODO More doc needed, explanations of the functions
    def __init__(self):
        #self.tableName = tableName
        self.listOfProducts = []

    def setCredentials(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def establishMySqlConnection(self, host, user, password, buffered=True, databaseName = None):
        self.productDb = MySqlProductDatabase(host, user, password, buffered)
        if (databaseName):
            self.productDb.createAndConnectToDb(databaseName, buffered)
            self.setCredentials(host, user, password)

    def createTable(self, tableName, obj, buffered=True):
        prod = ProductTable()
        prod.establishMySqlConnection(self.host, self.user, self.password, buffered)
        prod.setProductClass(obj)
        prod.productDb.createTable(tableName, self.productDb.getDbFieldsFromObj(self.productClass, "productDb"))
        self.listOfProductTables.append(prod)