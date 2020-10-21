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
            if not (hasattr(choices, '__iter__') or hasattr(choices, '__getitem__')):
                raise ValueError            #choices not iterable
            for i in choices:
                if not isinstance(i, int):
                    raise TypeError         #at least one choice is wrong type
            if self is not None and self not in choices:
                raise ValueError            #field has value not in choices
        if default is None:
            if blank == False:
                raise AttributeError
            else:                           #blank true
                if choices is not None and 0 not in choices:
                     raise TypeError        #base default not in choices
                else:
                    self = 0                #set base default
        else:                               #default given
            blank = True
            if choices is not None and default not in choices:
                raise TypeError
            else:
                self = default

class Float: 
    def __init__(self, blank=False, default=None, choices=None):
        if default is not None and not isinstance(default, (float, int)):
            raise TypeError                 #default is wrong type
        if choices is not None:
            if not (hasattr(choices, '__iter__') or hasattr(choices, '__getitem__')):
                raise ValueError            #choices not iterable
            for i in choices:
                if not isinstance(i, (float, int)):
                    raise TypeError         #at least one choice is wrong type
            if self is not None and self not in choices:
                raise ValueError            #field has value not in choices
        if default is None:
            if blank == False:
                raise AttributeError
            else:                           #blank true
                if choices is not None and 0.0 not in choices:
                     raise TypeError        #base default not in choices
                else:
                    self = 0.0              #set base default
        else:                               #default given
            blank = True
            if choices is not None and default not in choices:
                raise TypeError
            else:
                self = default



class String:
    def __init__(self, blank=False, default=None, choices=None):
        if default is not None and not isinstance(default, str):
            raise TypeError                 #default is wrong type
        if choices is not None:
            if not (hasattr(choices, '__iter__') or hasattr(choices, '__getitem__')):
                raise ValueError            #choices not iterable
            for i in choices:
                if not isinstance(i, str):
                    raise TypeError         #at least one choice is wrong type
            if self is not None and self not in choices:
                raise ValueError            #field has value not in choices
        if default is None:
            if blank == False:
                raise AttributeError
            else:                           #blank true
                if choices is not None and '' not in choices:
                     raise TypeError        #base default not in choices
                else:
                    self = ''               #set base default
        else:                               #default given
            blank = True
            if choices is not None and default not in choices:
                raise TypeError
            else:
                self = default

        
class Foreign:
    def __init__(self, table, blank=False):
        if blank == True:
            self = None

class DateTime:
    implemented = False

    def __init__(self, blank=False, default=None, choices=None):
        pass

class Coordinate:
    implemented = False

    def __init__(self, blank=False, default=None, choices=None):
        pass
