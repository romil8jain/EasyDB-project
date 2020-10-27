#!/usr/bin/python3
#
# table.py
#
# Definition for an ORM database table and its metaclass
#

import collections
import orm.field as field
from .easydb import exception
# metaclass of table
# Implement me or change me. (e.g. use class decorator instead)
# When you import schema, the metatable is automatically created
class MetaTable(type):

    my_classes= []
    class_var_list = dict()
    def __init__(cls, name, bases, attrs):

        if cls not in MetaTable.my_classes and cls.__name__ is not "Table":
            MetaTable.my_classes.append(cls)
            class_name = cls.__name__
            MetaTable.class_var_list[class_name] = [attr for attr in attrs if not attr.startswith("__")] # deleted from line: not callable(getattr(cls, attr)) and
            for col,val in attrs.items():
                if (not callable(val) and not col.startswith("__")):
                    val.setname(col)


    # Returns an existing object from the table, if it exists.
    #   db: database object, the database to get the object from
    #   pk: int, primary key (ID)
    def get(cls, db, pk):
        # help(cls)
        
        table_name = cls.__name__
        objValues, objVersion = db.get(table_name, pk)

        if objValues is not None:
            columns = {}
            index_attr = 0
            for attr in MetaTable.class_var_list[table_name]:

                if(isinstance(cls.__dict__[attr], field.Foreign)):

                    the_foreign_class = cls # Initial value never used

                    # Find the foreign class in list of foreign classes of table
                    # Will not work if one class has multiple foreign classes
                    for a_foreign_class_type in cls.foreign_classes: 
                        for a_class in MetaTable.my_classes:
                            if(a_foreign_class_type == a_class):
                                the_foreign_class = a_class

                    foreign_obj = the_foreign_class.get(db=db, pk=objValues[index_attr])
                    columns[attr] = foreign_obj
                elif(isinstance(cls.__dict__[attr], field.Coordinate)):
                    lat_val = objValues[index_attr]
                    lon_val = objValues[index_attr+1]
                    columns[attr] = (lat_val, lon_val)
                    index_attr+=1
                else:
                    columns[attr] = objValues[index_attr] # datetime is probably wrong because it will now be a string

                index_attr+=1
                    
            return_obj = cls(db, **columns)
            return_obj.pk = pk
            return_obj.version = objVersion
            return return_obj
        else:
            return None

    # Returns a list of objects that matches the query. If no argument is given,
    # returns all objects in the table.
    # db: database object, the database to get the object from
    # kwarg: the query argument for comparing
    def filter(cls, db, **kwarg):
        table_name = cls.__name__
        matches = list()
        objectList = list()
        value = 0
        columnName = 0
        operator = 0

        if not kwarg == {}:
            key, value = kwarg.popitem()
            
            if "_" in key:
                if not (key.endswith("_ne") or key.endswith("_gt") or key.endswith("_lt")):
                    raise AttributeError
                else:
                    queryArgs = key.split('_', 1)
                    columnName, operator = tuple(queryArgs)
            else:
                columnName = key
                operator = 2
            if operator == 'ne':
                operator = 3
            elif operator == 'lt':
                operator = 4
            else:
                operator = 5

            if columnName not in cls.__dict__:
                raise AttributeError
            
            matches = db.scan(table_name, operator, columnName, value)
            print(matches)
        else:
            operator = 1
            matches = db.scan(table_name, operator)
            print(matches)
        
        for pk in matches:
            obj = self.get(cls, db, pk)
            objectList.append(obj)

        return objectList


    # Returns the number of matches given the query. If no argument is given, 
    # return the number of rows in the table.
    # db: database object, the database to get the object from
    # kwarg: the query argument for comparing
    def count(cls, db, **kwarg):
        table_name = cls.__name__
        matches = list()
        columnName = 0
        operator = 0
        print("check")
        if not kwarg == {}:
            key, value = kwarg.popitem()
            
            if "_" in key:
                if not (key.endswith("_ne") or key.endswith("_gt") or key.endswith("_lt")):
                    raise AttributeError
                else:
                    queryArgs = key.split('_', 1)
                    columnName, operator = tuple(queryArgs)

            else:
                columnName = key
                operator = 2
            if operator == '_ne':
                operator = 3
            elif operator == '_lt':
                operator = 4
            elif operator == '_gt':
                operator = 5

            #check for field which DNE (case 8), currently buggy
            #if columnName not in cls.__dict__:
             #   raise AttributeError


            matches = db.scan(table_name, operator, columnName, value)

        else:
            operator = 1
            matches = db.scan(table_name, operator)

        return len(matches)



    # @classmethod
    # def __prepare__(mcs, name, bases, **kwargs):
    #     return collections.OrderedDict()

# table class
# Implement me.
# Every record of any table is also a table type of object.
class Table(object, metaclass=MetaTable):
    foreign_classes = list()
    def __init__(self, db, **kwargs):
        self.pk = None      # id (primary key)
        self.version = None # version
        self.db = db
        self.class_name = self.__class__.__name__

        # Setting default values is done in descriptor classes as default is known

        # set the value of attributes of that instance of the record
        for a_class in MetaTable.my_classes:
            a_class_name = a_class.__name__
            if(a_class_name == self.class_name):  # find the child class of Table

                for attr in MetaTable.class_var_list[a_class_name]:

                    if(attr in kwargs.keys()):
                        if(isinstance(a_class.__dict__[attr], field.Foreign)):
                            Table.foreign_classes.append(type(kwargs[attr]))
                        setattr(self, attr, kwargs[attr])
                    else:
                        setattr(self, attr, None) # as None value is passed, __set__ sets to default value or raises error



    # Save the row by calling insert or update commands.
    # atomic: bool, True for atomic update or False for non-atomic update
    def save(self, atomic=True):
        
        values = []
        for a_class in MetaTable.my_classes:
            a_class_name = a_class.__name__
            if(a_class_name == self.class_name):  # find the child class of Table
                for attr in MetaTable.class_var_list[a_class_name]:

                    if(isinstance(a_class.__dict__[attr], field.Foreign)):
                        foreign_obj = getattr(self, attr, None)
                        if(foreign_obj.pk is None):
                            foreign_obj.save()
                        values.append(foreign_obj.pk)
                    elif(isinstance(a_class.__dict__[attr], field.DateTime)):
                        values.append(str(getattr(self, attr, None)))
                    elif(isinstance(a_class.__dict__[attr], field.Coordinate)):
                        coordinate = getattr(self, attr, None)
                        values.append(coordinate[0]) # attr_lat
                        values.append(coordinate[1]) # attr_lon
                    else:
                        values.append(getattr(self, attr, None))
        
        if self.pk is None:
            self.pk, self.version = self.db.insert(self.class_name, values)
        else:
            self.version = self.db.update(self.class_name, self.pk, values)
            
    

    # Delete the row from the database.
    def delete(self):
        self.db.drop(self.class_name, self.pk)
        self.pk = None
        self.version = None




