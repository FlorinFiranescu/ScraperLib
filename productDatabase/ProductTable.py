from MySqlProductDatabase import *
from Product import *

class ProductTable(object):
    productDb = None
    productClass = None
    productType = None
    listOfProducts = None
    #TODO: Use tableName to define the ProductTable
    # Have a MySqlProductDatabase that contains multiple ProductTables
    tableName = ""
    #TODO More doc needed, explanations of the functions
    def __init__(self):
        #self.tableName = tableName
        self.listOfProducts = []

    def establishMySqlConnection(self, host, user, password, buffered=True, databaseName = None):
        '''

        :param host: Host of the Database
        :param user: Username to use for connecting to database
        :param password: Password to use for connecting to database
        :param buffered: Specify if buffered or not. Defaulted to True
        :return: void function
        '''
        self.productDb = MySqlProductDatabase(host, user, password, buffered)
        if (databaseName):
            self.productDb.createAndConnectToDb(databaseName, buffered)

    def connectToDb(self, databaseName, buffered=True):
        '''

        :param databaseName: database name
        :param buffered: Specify if buffered or not. Defaulted to True
        :return: void function
        '''
        self.productDb.connectToDb(databaseName, buffered)

    def setProductClass(self, obj):
        '''
        Set the product object and class for getting the attributes of it
        :param obj: Object instance of the product class
        :return: void function
        '''
        self.productClass = obj
        self.productType = type(obj)

    def addProduct(self, obj):
        '''
        Adds a product to the list of products
        :param obj: Product to add
        :return: void function
        '''
        if not(isinstance(obj, self.productType)):
            print(f"The item {obj} is type {type(obj)}. Expected type {self.productType}")
            raise
        self.listOfProducts.append(obj)

    def createTable(self, tableName):
        '''
        Create a new table and sets the cursor to it
        :param tableName: Name of the new table
        :return: void function
        '''
        self.productDb.createTable(tableName, self.productDb.getDbFieldsFromObj(self.productClass, "productDb"))

    def getObjFields(self):
        '''
        Get the object fields
        :return: void funtcion
        '''
        return self.productDb.getDbFieldsFromObj(self.productClass, "productDb")

    def getExcelColumns(self):
        '''
        Get the column for excel, uses the productClass variable
        :return: void function
        '''
        listOfFields = []
        for fieldTuple in self.getObjFields():
            field = dict(fieldTuple)
            listOfFields.append(field.get("NAME"))
        return listOfFields

    def getProductAttributeValues(self, *argv):
        '''
        Gets the product values
        :param argv: Attribute values to skip
        :return:void function
        '''
        listOfAttributeValues = []
        for productItem in self.listOfProducts:
            listOfItemAttributeValues = []
            for attributeName in self.getExcelColumns():
                if(attributeName in argv):
                    continue
                listOfItemAttributeValues.append(getattr(productItem, attributeName))
            listOfAttributeValues.append(listOfItemAttributeValues)
        return listOfAttributeValues

    def setProductListFromTable(self, tableName):
        '''
        Set the product list based on the provided table found in the MySQL db
        :param tableName: name of the table
        :return:void function
        '''
        fieldNamesTuple = self.getObjFields()
        for tupleItem in self.productDb.getAllTableValues(tableName):
            prod = self.productClass
            for it in range(0, len(fieldNamesTuple)):
                attrName = dict(fieldNamesTuple[it]).get('NAME')
                attrVal  = tupleItem[it]
                setattr(prod, attrName, attrVal)
            print(prod)
            self.listOfProducts.append(prod)