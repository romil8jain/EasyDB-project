#!/usr/bin/python3
#
# fields.py
#
# Definitions for all the fields in ORM layer
#

class Integer:   
    def __init__(self, blank=False, default=None, choices=None):        
        if default is not None and not isinstance(default, int):
            raise TypeError                 #default is wrong type
        if choices is not None:
#            if not (hasattr(choices, '__iter__') or hasattr(choices, '__getitem__')):
#                raise ValueError            #choices not iterable
            for i in choices:
                if not isinstance(i, int):
                    raise TypeError         #at least one choice is wrong type
            if default is not None and choices is not None and default not in choices:
                raise TypeError

    def setname(self, name):
        self.name = "_" + name

    def __get__(self, inst, cls):
        return getattr(inst, self.name)

    def __set__(self, inst, value):
        if not isinstance(value, int):
            raise TypeError
        setattr(inst, self.name, value)


class Float: 
    def __init__(self, blank=False, default=None, choices=None):
        if default is not None and not isinstance(default, (float, int)):
            raise TypeError                 #default is wrong type
        if choices is not None:
#            if not (hasattr(choices, '__iter__') or hasattr(choices, '__getitem__')):
#                raise ValueError            #choices not iterable
            for i in choices:
                if not isinstance(i, (float, int)):
                    raise TypeError         #at least one choice is wrong type
            if default is not None and default not in choices:
                raise TypeError

    def setname(self, name):
        self.name = "_" + name

    def __get__(self, inst, cls):
        return getattr(inst, self.name)

    def __set__(self, inst, value):
        if not isinstance(value, (float, int)):
            raise TypeError
        setattr(inst, self.name, value)


class String:
    def __init__(self, blank=False, default=None, choices=None):
        if default is not None and not isinstance(default, str):
            raise TypeError                 #default is wrong type
        if choices is not None:
#            if not (hasattr(choices, '__iter__') or hasattr(choices, '__getitem__')):
#                raise ValueError            #choices not iterable
            for i in choices:
                if not isinstance(i, str):
                    raise TypeError         #at least one choice is wrong type
            if default is not None and default not in choices:
                raise TypeError

    def setname(self, name):
        self.name = "_" + name

    def __get__(self, inst, cls):
        return getattr(inst, self.name)

    def __set__(self, inst, value):
        if not isinstance(value, str):
            raise TypeError
        setattr(inst, self.name, value)
        
class Foreign:
    def __init__(self, table, blank=False):
#        if blank == True: #make sure there is table and save field blank
#            self = None
        self.table = table
        self.blank = blank

    def setname(self, name):
        self.name = "_" + name

    def __get__(self, inst, cls):
        return getattr(inst, self.name)

    def __set__(self, inst, value):
        if not isinstance(value, int):
            raise TypeError
        setattr(inst, self.name, value)
        

class DateTime:
    implemented = False

    def __init__(self, blank=False, default=None, choices=None):
        pass

class Coordinate:
    implemented = False

    def __init__(self, blank=False, default=None, choices=None):
        pass
