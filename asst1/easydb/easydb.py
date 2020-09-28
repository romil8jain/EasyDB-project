#!/usr/bin/python3
#
# easydb.py
#
# Definition for the Database class in EasyDB client
#
from collections.abc import Iterable
from struct import *
from .exception import *
from .packet import *
import socket
import time

class Database:
    def __repr__(self):
        return "<EasyDB Database object>"

    def __init__(self, tables):
       self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       referenced_tables = dict()
       self.tableNamesList = list()
       self.schema = tables
     
       try:
         iterator = iter(tables)
       except TypeError as t:
         print(t)
     
       # Iterate over all tables
       for i in range(len(tables)):
     
         tableName = tables[i][0]
     
         # Check if table name is a string
         if not isinstance(tableName,str):
           raise TypeError
        
         # Check for duplicate tables
         if tableName not in self.tableNamesList:
           self.tableNamesList.append(tableName)
         else:
           raise ValueError
     
         # Maintain list of referenced tables
         referenced_tables[tableName] = list()
     
         columnNamesList = list() # for duplicate column check, new created for every table
     
         for j in range(len(tables[i][1])):
     
           columnName = tables[i][1][j][0]
     
           # Check if column name is a string
           if not isinstance(columnName,str):
             raise TypeError
     
           # Check if column name is not duplicate
           if columnName not in columnNamesList:
             columnNamesList.append(columnName)
           else:
             raise ValueError
          
           checkType = tables[i][1][j][1] # type of column
     
           # Check if table is referencing itself, if not, make dictionary of tables referenced by it
           if isinstance(checkType,str):
             if checkType == tableName:
               raise ValueError
             else:
               referenced_tables[tableName].append(checkType)
     
           # Check if type of value is str, int or float, these are arbitrary values
           elif not (checkType == type(4) or checkType == type(1.3) or checkType == type("hello")):
             raise ValueError
     
       for k in referenced_tables.keys():
         for i in range(len(referenced_tables[k])):
     
           refer_table_name = referenced_tables[k][i]
     
           # Foreign key is invalid
           if refer_table_name not in referenced_tables.keys():
             raise IntegrityError()
     
           # Foreign key cycle
           elif k in referenced_tables[refer_table_name]:
             raise IntegrityError()
 


    def connect(self, host, port):
        ADDR = (host, port)
        self.client.connect(ADDR)
        time.sleep(1)
        intial_message = self.client.recv(4096)
        return True

    def close(self):
        self.client.close()

    def insert(self, table_name, values):

       tableNumber = self.tableNamesList.index(table_name) + 1 
       request = pack('>ii', 1, tableNumber)
     
       count = pack('>i', len(values))
     
       row = bytes()
     
       for i in range(len(values)):
     
         valType = str()
         valTypeByte = bytes()
         valTypeSize = bytes()
     
         if type(values[i]) == type(5): # arbitrary integer
           valType = '>q'
           valTypeByte = pack('>i', 1)
           valTypeSize = pack('>i', 8)
     
           # check if line exists first
           if self.schema[tableNumber-1][1][i][1] and type(self.schema[tableNumber-1][1][i][1]) == type ("hello"): # type of string, then it is foreign
             valTypeByte = pack('>i', 4)
        
         elif type(values[i]) == type('hello'):# arbitrary string
           if len(values[i]) % 4 == 0:
             valType = '>' + str(len(values[i])) + 's'
             valTypeSize = pack('>i', len(values[i]))
           else:
             valType = '>' + str(((len(values[i]) // 4) + 1) * 4 ) + 's'
             valTypeSize = pack('>i', ((len(values[i]) // 4) + 1) * 4)
     
           values[i] = bytes(values[i], 'utf-8')
           valTypeByte = pack('>i', 3)
     
         elif type(values[i]) == type (5.3):
           valType = '>d'
           valTypeByte = pack('>i', 2)
           valTypeSize = pack('>i', 8)
        
     
         packetVal = pack(valType, values[i])
         row = row + valTypeByte + valTypeSize + packetVal
     
     
       sendVal = request + count + row
       self.client.send(sendVal)
       time.sleep(1)
       insert_message = self.client.recv(4096)
       print(insert_message)
       (code, pk, version) = unpack_from(">lqq", insert_message)
       return(pk,version)
       

       # print(self.client.recv(2048))


    def update(self, table_name, pk, values, version=None):
        # TODO: implement me
        pass

    def drop(self, table_name, pk):
        # TODO: implement me
        pass
        
    def get(self, table_name, pk):
 
     if not type(pk) == type(5):
       raise PacketError()
      
     tableNumber = self.tableNamesList.index(table_name) + 1
  
     request = pack('>ii', GET, tableNumber)
     rowNum = pack('>q', pk)
  
     sendVal = request + rowNum
     self.client.send(sendVal)
     time.sleep(1)
     get_message = self.client.recv(4096)
 
     get_format=">iqi" # code, version, count, value type, value length
 
     code, version, numRows = unpack_from(get_format, get_message)
 
     offset = calcsize(get_format)
 
     numColumns = len(self.schema[tableNumber-1][1])
 
     # Initiate empty lists for values in each column
     valType = [None] * numColumns
     valSize = [None] * numColumns
     value = [None] * numColumns
 
     for i in range(numColumns):
 
       get_format = ">ii"  # unpack valType and valSize
 
       # Get type of value and its size to set value format string
       valType[i], valSize[i] = unpack_from(get_format, get_message, offset)
       checkType = self.schema[tableNumber-1][1][i][1]
 
       if(valType[i] == INTEGER):
         get_format = ">q"
 
       elif(valType[i] == FLOAT):
         get_format = ">d"
 
       elif(valType[i] == STRING):
         get_format = ">%ds"%valSize[i]
      
       else:
         get_format = ">q"
 
       offset+= calcsize(">ii") #increase offset to get value
       value[i], = unpack_from(get_format, get_message, offset=offset) # get the value
       if(valType[i] == STRING):
         value[i] = value[i].decode('utf-8')
         value[i] = value[i].strip('\x00')
       offset+= calcsize(get_format) # increase offset to get next value info
 
     return value, version

    def scan(self, table_name, op, column_name=None, value=None):
        # TODO: implement me
        pass
                        
