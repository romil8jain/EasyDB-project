#!/usr/bin/python3
#
# fields.py
#
# Definitions for all the fields in ORM layer
#
from collections.abc import Iterable
from datetime import datetime

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
        elif isinstance(self.default,int) :
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
    implemented = True

    def __init__(self, blank=False, default=None, choices=None):
        self.blank = blank

        if default is not None:
            if(callable(default) and not isinstance(default(),datetime)):
                raise TypeError  
            elif (not callable(default) and not isinstance(default, datetime)) :
                raise TypeError
                     
        if default is not None:
            self.blank = True
            if(callable(default)):
                self.default = default()
            else:
                self.default = default
        
        if(default == None):
            self.default = datetime.fromtimestamp(0) # if default not specified, it should be 0

        if choices is not None:

            if not isinstance(choices, Iterable):
                raise ValueError("Choices not Iterable")

            for i in choices:
                if not isinstance(i, datetime): # Here I assume that choices dont pass a callable function as a choice
                    raise TypeError         #at least one choice is wrong type

            if default is not None and choices is not None and default not in choices:
                raise TypeError
    
        self.choices = choices  

    def setname(self, name):
        self.name = "_" + name

    def __get__(self, inst, cls):
        return getattr(inst, self.name)

    def __set__(self, inst, value):
        
        if value is not None:
            if(callable(value) and not isinstance(value(),datetime)):
                raise TypeError  
            elif (not callable(value) and not isinstance(value, datetime)) :
                raise TypeError
                     
        
        if value is None and self.blank is False: # setattr in Table send a value of None here
            raise AttributeError("Specify the value of the field datetime")
        
        if value is None and self.blank is True:
            value = self.default

        if self.choices is not None and value not in self.choices:
            raise ValueError("Value not in choices")

        if value is not None:
            if(callable(value)):
                setattr(inst, self.name, value()) # stored as string in the database
            else:
                setattr(inst, self.name, value)
        

    
class Coordinate:
    implemented = True

    def __init__(self, blank=False, default=None, choices=None):
        self.blank = blank

        if default is not None:
            self.blank = True
            self.default = default
        
        if(default == None):
            self.default = (0.0,0.0) # if default not specified, it should be 0

        if default is not None:
            if(not self.check_valid_coordinate(default)):
                if(not (isinstance(default, tuple) and len(default) == 2)):
                    raise TypeError("Invalid coordinates type")                 #default is wrong type
                else:
                    raise ValueError("Invalid coordinates value")

        if choices is not None:

            if not isinstance(choices, Iterable):
                raise ValueError("Choices not Iterable")

            for i in choices:
                if(not self.check_valid_coordinate(i)):
                    if(not (isinstance(i, tuple) and len(i) == 2)):
                        raise TypeError("Invalid coordinates type")                 #default is wrong type
                    else:
                        raise ValueError("Invalid coordinates value")        #at least one choice is wrong type

            if default is not None and choices is not None and default not in choices:
                raise TypeError
    
        self.choices = choices  

    def setname(self, name):
        self.name = "_" + name

    def __get__(self, inst, cls):
        return getattr(inst, self.name)

    def __set__(self, inst, value):
        
        if value is None and self.blank is False: # setattr in Table send a value of None here
            raise AttributeError("Specify the value of the field coordinate")
        
        if value is None and self.blank is True:
            value = self.default
        
        if(not self.check_valid_coordinate(value)):
            if(not (isinstance(value, tuple) and len(value) == 2)):
                raise TypeError("Invalid coordinates type")                 
            else:
                raise ValueError("Invalid coordinates value")  

        if self.choices is not None and value not in self.choices:
            raise ValueError("Value not in choices")
        
        value = list(value)
        value[0] = float(value[0])
        value[1] = float(value[1])
        value = tuple(value)
        setattr(inst, self.name, value)

    def check_valid_coordinate(self, coordinate):
        if (isinstance(coordinate, tuple) and len(coordinate) == 2 and 
            coordinate[0]>=-90 and coordinate[0]<=90 and 
            coordinate[1]>=-180 and coordinate[1]<=180 and 
            (isinstance(coordinate[0], int) or isinstance(coordinate[0], float)) and 
            (isinstance(coordinate[1], int) or isinstance(coordinate[1], float))): 
            return True
        else:
            return False
