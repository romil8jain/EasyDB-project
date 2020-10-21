#!/usr/bin/python3
#
# table.py
#
# Definition for an ORM database table and its metaclass
#

import collections

# metaclass of table
# Implement me or change me. (e.g. use class decorator instead)
class MetaTable(type):

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

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

    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        return collections.OrderedDict()

# table class
# Implement me.
class Table(object, metaclass=MetaTable):

    def __init__(self, db, **kwargs):
        self.pk = None      # id (primary key)
        self.version = None # version
        # FINISH ME

    # Save the row by calling insert or update commands.
    # atomic: bool, True for atomic update or False for non-atomic update
    def save(self, atomic=True):
        pass
        
    # Delete the row from the database.
    def delete(self):
        pass

