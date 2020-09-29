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
   
     # Check if table name is blank or starts with illegal character
     if(tableName == "" or not tableName[0].isalpha()):
       raise ValueError
 
     # Check for duplicate tables
     if tableName not in self.tableNamesList:
       self.tableNamesList.append(tableName)
     else:
       raise ValueError
 
     columnNamesList = list() # for duplicate column check, new created for every table
 
     for j in range(len(tables[i][1])):
 
       columnName = tables[i][1][j][0]
 
       # Check if column name is a string
       if not isinstance(columnName,str):
         raise TypeError
         
       # Check if column name is blank or starts with illegal character
       if(columnName == "" or columnName == "id" or not columnName[0].isalpha()):
         raise ValueError
 
       # Check if column name is not duplicate
       if columnName not in columnNamesList:
         columnNamesList.append(columnName)
       else:
         raise ValueError
     
       checkType = tables[i][1][j][1] # type of column
 
       # Check if table is referencing itself, if not, make dictionary of tables referenced by it
       if isinstance(checkType,str):
         if checkType == tableName:
           raise IntegrityError()
         elif(checkType not in self.tableNamesList):
            raise IntegrityError()
          
 
       # Check if type of value is str, int or float, these are arbitrary values
       elif not (checkType == int or checkType == float or checkType == str):
         raise ValueError
 def connect(self, host, port):
     ADDR = (host, port)
     self.client.connect(ADDR)
     time.sleep(1)
     intial_message = self.client.recv(4096)
     return True
 def close(self):
     exit_message = pack(">i", EXIT)
     self.client.send(exit_message)
     self.client.close()
 def insert(self, table_name, values):
  
   if(type(table_name) == int or table_name not in self.tableNamesList):
     raise PacketError()
     print("Invalid or illegal table_name")
 
   tableNumber = self.tableNamesList.index(table_name) + 1
 
   request = pack('>ii', 1, tableNumber)
 
   count = pack('>i', len(values))
 
   row = bytes()
 
   if(not len(values) == len(self.schema[tableNumber-1][1])):
     print(f"Packet error: length of values was {len(values)} but inputs desired were {len(self.schema[tableNumber-1][1])}")
     raise PacketError()
 
   for i in range(len(values)):
 
     valType = str()
     valTypeByte = bytes()
     valTypeSize = bytes()
 
     checkType = self.schema[tableNumber-1][1][i][1]
     
     if(type(checkType) == str and type(values[i])!=int):
        raise InvalidReference()

     #Check if the type is correct based on schema
     if(type(values[i]) != checkType):
       if (type(values[i]) == int and type(checkType)!=str):
         raise PacketError() 
      
 
     if type(values[i]) == int:
       valType = '>q'
       valTypeByte = pack('>i', INTEGER)
       valTypeSize = pack('>i', 8)
 
       # check if line exists first, self.schema[tableNumber-1][1][i][1] and
       if type(checkType) == str: # type of string, then it is foreign
         valTypeByte = pack('>i', FOREIGN)
         
   
     elif type(values[i]) == str:
       if len(values[i]) % 4 == 0:
         valType = '>' + str(len(values[i])) + 's'
         valTypeSize = pack('>i', len(values[i]))
       else:
         valType = '>' + str(((len(values[i]) // 4) + 1) * 4 ) + 's'
         valTypeSize = pack('>i', ((len(values[i]) // 4) + 1) * 4)
 
       values[i] = bytes(values[i], 'utf-8')
       valTypeByte = pack('>i', STRING)
 
     elif type(values[i]) == float:
       valType = '>d'
       valTypeByte = pack('>i', FLOAT)
       valTypeSize = pack('>i', 8)
      
     else:
       raise PacketError()
   
 
     packetVal = pack(valType, values[i])
     row = row + valTypeByte + valTypeSize + packetVal
 
 
   sendVal = request + count + row
   self.client.send(sendVal)
   time.sleep(1)
   insert_message = self.client.recv(4096)

   code, = unpack_from(">l", insert_message)

   if(code == BAD_FOREIGN):
     raise InvalidReference()

   if(code == BAD_VALUE):
     raise PacketError()

   (code, pk, version) = unpack_from(">lqq", insert_message)

   

   return(pk,version)
   
   # print(self.client.recv(2048))
 def update(self, table_name, pk, values, version=None):
     if not type(pk) == int:
       raise PacketError()
 
     if not (type(version) == int or version == None):
       raise PacketError()
 
     if(type(table_name) == int or table_name not in self.tableNamesList):
       raise PacketError()
   
    
     tableNumber = self.tableNamesList.index(table_name) + 1
   
     request = pack('>ii', UPDATE, tableNumber)
 
     if(not len(values) == len(self.schema[tableNumber-1][1])):
       raise PacketError()
     
     # if version is none, it should be set to 0
     if(version == None):
       versionVal = pack('>q', 0)
     else:
       versionVal = pack('>q', version)
     pkVal = pack('>q', pk)
     count = pack('>i', len(values))
   
   
     sendVal = request + pkVal + versionVal + count
   
   
     row = bytes()
   
     for i in range(len(values)):
   
       checkType = self.schema[tableNumber-1][1][i][1]
       valType = str()
       valTypeByte = bytes()
       valTypeSize = bytes()
        
       if(type(checkType) == str and type(values[i])!=int):
         raise InvalidReference()

       if(type(values[i]) != checkType):
         if (type(values[i]) == int and type(checkType)!=str):
           raise PacketError() 
 
       if type(values[i]) == int:
         valType = '>q'
         valTypeByte = pack('>i', INTEGER)
         valTypeSize = pack('>i', 8)
   
         if type(checkType) == str: # type of string, then it is foreign
           valTypeByte = pack('>i', FOREIGN)
           
     
       elif type(values[i]) == str:
         if len(values[i]) % 4 == 0:
           valType = '>' + str(len(values[i])) + 's'
           valTypeSize = pack('>i', len(values[i]))
         else:
           valType = '>' + str(((len(values[i]) // 4) + 1) * 4 ) + 's'
           valTypeSize = pack('>i', ((len(values[i]) // 4) + 1) * 4)
   
         values[i] = bytes(values[i], 'utf-8')
         valTypeByte = pack('>i', STRING)
   
       elif type(values[i]) == type (5.3):
         valType = '>d'
         valTypeByte = pack('>i', FLOAT)
         valTypeSize = pack('>i', 8)
         
       else:
         raise PacketError()
   
       packetVal = pack(valType, values[i])
       row = row + valTypeByte + valTypeSize + packetVal
   
   
     sendVal += row
     self.client.send(sendVal)
     time.sleep(1)
     update_message = self.client.recv(4096)
 
     code, = unpack_from(">l", update_message)
     if(code == TXN_ABORT):
       raise TransactionAbort()
 
     if(code == NOT_FOUND):
       raise ObjectDoesNotExist()

     if(code == BAD_FOREIGN):
       raise InvalidReference()
 
     code, version = unpack_from(">lq", update_message)
     return version
 def drop(self, table_name, pk):
     # TODO: implement me
     pass
   
 def get(self, table_name, pk):
     if not type(pk) == type(5):
       raise PacketError()
    
     if(not table_name in self.tableNamesList):
       raise PacketError()
    
     tableNumber = self.tableNamesList.index(table_name) + 1
  
     request = pack('>ii', GET, tableNumber)
     rowNum = pack('>q', pk)
  
     sendVal = request + rowNum
     self.client.send(sendVal)
     time.sleep(1)
     get_message = self.client.recv(4096)
  
     get_format=">iqi" # code, version, count, value type, value length
  
     code, = unpack_from(">i", get_message)
 
     if(code == NOT_FOUND):
       raise ObjectDoesNotExist()

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
                    
 
 
 


