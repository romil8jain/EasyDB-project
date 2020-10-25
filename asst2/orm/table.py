#!/usr/bin/python3
#
# table.py
#
# Definition for an ORM database table and its metaclass
#

import collections
import orm.field
# metaclass of table
# Implement me or change me. (e.g. use class decorator instead)
# When you import schema, the metatable is automatically created
class MetaTable(type):

    my_classes= []
    class_var_list = dict()
    def __init__(cls, name, bases, attrs):

        if cls not in MetaTable.my_classes:
            MetaTable.my_classes.append(cls)
            class_name = cls.__name__
            # I think my code works better in this case,
            # I have kept your code in end of document  
            # Set the name of all class variables to _name
            MetaTable.class_var_list[class_name] = [attr for attr in attrs if not callable(getattr(cls, attr)) and not attr.startswith("__")]
            for attr in MetaTable.class_var_list[class_name]:
                getattr(cls,attr).setname(attr) # mostly works correctly


    # Returns an existing object from the table, if it exists.
    #   db: database object, the database to get the object from
    #   pk: int, primary key (ID)
    def get(cls, db, pk):
        return None

    # Returns a list of objects that matches the query. If no argument is given,
    # returns all objects in the table.
    # db: database object, the database to get the object from
    # kwarg: the query argument for comparing
    def filter(cls, db, **kwarg):
        return list()

    # Returns the number of matches given the query. If no argument is given, 
    # return the number of rows in the table.
    # db: database object, the database to get the object from
    # kwarg: the query argument for comparing
    def count(cls, db, **kwarg):
        return list()

    # @classmethod
    # def __prepare__(mcs, name, bases, **kwargs):
    #     return collections.OrderedDict()

# table class
# Implement me.
# Every record of any table is also a table type of object.
class Table(object, metaclass=MetaTable):

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

                for attr in MetaTable.class_var_list[a_class_name].items():

                    if(attr in kwargs.keys()):
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
                for attr in MetaTable.class_var_list[a_class_name].items():

                    if(isinstance(attr, field.Foreign)):
                        foreign_obj = getattr(self, attr, None)
                        if(foreign_obj.pk is None):
                            foreign_obj.save()
                        values.append(foreign_obj.pk)
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


# Potential problem lines:
 # metaclass init

# Unused code

        # metaclass has class information
        # for a_class in super().my_classes:
        #     if(self.__class__.__name__ == a_class):
        #         the_class = getattr(schema, )

        # for col, val in attrs.items():
        #     if isinstance(val, (Integer, Float, String, Foreign)):
        #         val.setname(col)
