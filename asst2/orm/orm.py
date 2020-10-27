#!/usr/bin/python3
#
# orm.py
#
# Definition for setup and export function
#

from .easydb import Database
from .table import MetaTable
import orm.field as field

# Return a database object that is initialized, but not yet connected.
#   database_name: str, database name
#   module: module, the module that contains the schema
def setup(database_name, module):
    # Check if the database name is "easydb".
    if database_name != "easydb":
        raise NotImplementedError("Support for %s has not implemented"%(
            str(database_name)))

    tb = list()
    for a_class in MetaTable.my_classes:
        class_name = a_class.__name__
        tb_class = list()
       # if class_name in tb_class:
       #     raise AttributeError
        tb_class.append(class_name)
        tb_class_var_list = list()

        for class_var in MetaTable.class_var_list[class_name]:
            # print(f"Class: {module.__dict__[class_name]}")
            class_attr = module.__dict__[class_name].__dict__[class_var]
            class_var_pair = tuple()
            # print(f"Class var type: {class_var_type}")

            if(isinstance(class_attr, field.Integer)):
                class_var_pair = (class_var, int)

            elif(isinstance(class_attr, field.Float)):
                class_var_pair = (class_var, float)

            elif(isinstance(class_attr, field.String)):
                class_var_pair = (class_var, str)
            
            elif(isinstance(class_attr, field.Foreign)):
                foreign_class_name = class_attr.table.__name__
                class_var_pair = (class_var, foreign_class_name)
            
            elif(isinstance(class_attr, field.DateTime)):
                class_var_pair = (class_var, str)

            elif(isinstance(class_attr, field.Coordinate)):
                class_var_lat = class_var + "_lat"
                class_var_pair = (class_var_lat, float)
                tb_class_var_list.append(class_var_pair)
                class_var_lon = class_var + "_lon"
                class_var_pair = (class_var_lon, float)
            
            tb_class_var_list.append(class_var_pair)
        
        tb_class_var_list = tuple(tb_class_var_list)
        tb_class.append(tb_class_var_list)
        tb_class = tuple(tb_class)
        tb.append(tb_class)
  
    
    tb = tuple(tb)
    
    # IMPLEMENT ME
    return Database(tb) 

# Return a string which can be read by the underlying database to create the 
# corresponding database tables.
#   database_name: str, database name
#   module: module, the module that contains the schema
def export(database_name, module):

    # Check if the database name is "easydb".
    if database_name != "easydb":
        raise NotImplementedError("Support for %s has not implemented"%(
            str(database_name)))

    tb = str()
    for a_class in MetaTable.my_classes:
        class_name = a_class.__name__
        tb += class_name + "{ \n"
        
        for class_var in MetaTable.class_var_list[class_name]:
            class_attr = module.__dict__[class_name].__dict__[class_var]

            if(isinstance(class_attr, field.Integer)):
                tb += class_var + ": integer; \n"

            elif(isinstance(class_attr, field.Float)):
                tb += class_var + ": float; \n"

            elif(isinstance(class_attr, field.String)):
                tb += class_var + ": string; \n"
            
            elif(isinstance(class_attr, field.Foreign)):
                foreign_class_name = class_attr.table.__name__
                tb += class_var + ": " + foreign_class_name + "; \n"

            elif(isinstance(class_attr, field.DateTime)):
                tb += class_var + ": string; \n"

            elif(isinstance(class_attr, field.Coordinate)):
                class_var_lat = class_var + "_lat"
                tb += class_var_lat + ": float; \n"
                class_var_lon = class_var + "_lon"
                tb += class_var_lon + ": float; \n"

        tb += "} \n"
    
    return tb

