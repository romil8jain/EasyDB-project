#!/usr/bin/python3
#
# fields.py
#
# Definitions for all the fields in ORM layer
#
from collections.abc import Iterable

class Integer:   
    def __init__(self, blank=False, default=None, choices=None): 
         
        self.blank = blank

        if default is not None:
            self.blank = True
            self.default = default
        
        if(default == None):
            self.default = 0 # if default not specified, it should be 0
        

        if default is not None and not isinstance(default, int):
            raise TypeError                 #default is wrong type

        if choices is not None:

            if not isinstance(choices, Iterable):
                raise ValueError("Choices not Iterable")

            for i in choices:
                if not isinstance(i, int):
                    raise TypeError         #at least one choice is wrong type

            if default is not None and choices is not None and default not in choices:
                raise TypeError
    
        self.choices = choices  

    def setname(self, name):
        self.name = "_" + name

    def __get__(self, inst, cls):
        return getattr(inst, self.name)

    def __set__(self, inst, value):

        if value is None and self.blank is False: # setattr in Table send a value of None here
            raise AttributeError("Specify the value of the field integer")
        
        if value is None and self.blank is True:
            value = self.default
        
        if not isinstance(value, int):
            raise TypeError("Not an integer")

        if self.choices is not None and value not in self.choices:
            raise ValueError("Value not in choices")

        setattr(inst, self.name, value)


class Float: 
    def __init__(self, blank=False, default=None, choices=None):

        self.blank = blank

        if default is not None:
            self.blank = True
            self.default = default
        
        if(default == None):
            self.default = 0.0 # if default not specified, it should be 0
        
        if default is not None and not (isinstance(default, float) or isinstance(default, int)):
            raise TypeError                 #default is wrong type
        else:
            self.default = float(default)

        if choices is not None:

            if not isinstance(choices, Iterable):
                raise ValueError("Choices not Iterable")

            for i in choices:
                if not (isinstance(i, int) or isinstance(default, float)):
                    raise TypeError         #at least one choice is wrong type

            if default is not None and choices is not None and default not in choices:
                raise TypeError
    
        self.choices = choices  
    
    def setname(self, name):
        self.name = "_" + name

    def __get__(self, inst, cls):
        return getattr(inst, self.name)

    def __set__(self, inst, value):
        
        if value is None and self.blank is False: # setattr in Table send a value of None here
            raise AttributeError("Specify the value of the field float")
        
        if value is None and self.blank is True:
            value = self.default
        
        if not (isinstance(value, float) or isinstance(value, int)):
            raise TypeError("Not a float")

        if self.choices is not None and value not in self.choices:
            raise ValueError("Value not in choices")
        value = float(value)
        setattr(inst, self.name, value)

class String:
    def __init__(self, blank=False, default=None, choices=None):

        self.blank = blank

        if default is not None:
            self.blank = True
            self.default = default
        
        if(default == None):
            self.default = "" # if default not specified, it should be 0

        if default is not None and not isinstance(default, str):
            raise TypeError                 #default is wrong type

        if choices is not None:

            if not isinstance(choices, Iterable):
                raise ValueError("Choices not Iterable")

            for i in choices:
                if not isinstance(i, str):
                    raise TypeError         #at least one choice is wrong type

            if default is not None and choices is not None and default not in choices:
                raise TypeError
    
        self.choices = choices  

    def setname(self, name):
        self.name = "_" + name

    def __get__(self, inst, cls):
        return getattr(inst, self.name)

    def __set__(self, inst, value):
        
        if value is None and self.blank is False: # setattr in Table send a value of None here
            raise AttributeError("Specify the value of the field string")
        
        if value is None and self.blank is True:
            value = self.default
        
        if not isinstance(value, str):
            raise TypeError("Not a string")

        if self.choices is not None and value not in self.choices:
            raise ValueError("Value not in choices")

        setattr(inst, self.name, value)

class Foreign:
    def __init__(self, table, blank=False):

        if blank == True: 
            self.table = None
        else:
            self.table = table

    def setname(self, name):
        self.name = "_" + name
    
    def __get__(self, inst, cls):
        return getattr(inst, self.name)

    def __set__(self, inst, value):
        
        if (isinstance(value, int) or isinstance(value, str) or isinstance(value, float)):
            raise TypeError("Wrong type")

        elif(not isinstance(value, self.table)):
            raise TypeError("Table type and object provided mismatch")

        else:
            setattr(inst, self.name, value)
        


            
        

class DateTime:
    implemented = False

    def __init__(self, blank=False, default=None, choices=None):
        pass

    def setname(self, name):
        self.name = "_" + name

class Coordinate:
    implemented = False

    def __init__(self, blank=False, default=None, choices=None):
        pass

    def setname(self, name):
        self.name = "_" + name
