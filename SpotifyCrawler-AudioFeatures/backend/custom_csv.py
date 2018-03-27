# -*- coding: utf-8 -*-
"""
This is a helper script I wrote to perform special csv operations. 

generate_header() and add_entry() simple take lists and write them to a file.

export_as_dict("key") and export_as_list() read a csv file and return it in
the corresponding data structure. 

"""
import csv

def write_line(filename, string):
    file = open(filename, "a")
    try:
        file.write(string + '\n')
    except:
        print("Write error writing: " + string)
    file.close()
    
    return

def generate_header(filename, column_names):
    
    header_string = ""
    column_count = len(column_names)
    
    for x in range(0,column_count-1):
        header_string += '"' + str(column_names[x]) + '",'
    header_string += '"' + str(column_names[column_count-1]) + '"'
    
    write_line(filename, header_string)
    
    return    

def add_entry(filename, values):
    
    entry_string = ""
    column_count = len(values)
    
    for x in range(0,column_count-1):
        entry_string += '"' + str(values[x]) + '",'
    entry_string += '"' + str(values[column_count-1]) + '"'
    
    write_line(filename, entry_string)
    
    return 

def read_csv(filename):
    
    result = []
    
    with open(filename) as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        for row in csvReader: result.append(row)

    return result

def export_as_dict(key_name, filename):
    
    result_list = read_csv(filename)
    result_dict = {}
    
    header = result_list.pop(0)
    if key_name not in header: return 0
    
    key_index = header.index(key_name)
    
    for row in result_list:
        key = row[key_index]
        values = {}
        
        for column in row: 
            # if data stored as dict or JSON, eval to store
            if '{' in column: values[header[row.index(column)]] = eval(column)
            else: values[header[row.index(column)]] = column
            
        result_dict[key] = values
        
    return result_dict

def export_as_list(filename):
    
    return read_csv(filename)