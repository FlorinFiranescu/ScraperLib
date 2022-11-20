# productDatabase
This repo will be used as a submodule. It will be a library that will let users attach products to a MySql database through queries 
It contains all the needed functions for CRUD ( creating, reading, updating, deleting) an object to a MySQL database.
It contains:
-> Product.py class 
-> ProductTable.py ( implements all the needed methods for creating/inserting/updating/deleting a specific table that contains Product instances )
-> ProductDatabase.py ( implements all the needed methods for creating/inserting/updating/deleting databases that contains ProductTable instances )
-> MySqlDatabase.py (connects to a mySql database, contains all the queries that care called by the other classes)

