"""
HOW TO RUN:
To run execute the function: main().
This is done by execiting the script of "GH Database.py"

IMPORTANT:
"GitHub_numpy_database.csv" must already exist before running. Execute GitHub v3 to create this file.
Before running ensure "GH_Database.csv" does not already exist.
"""
import requests
import csv
from bs4 import BeautifulSoup
from urllib import request


# Desc: Appends a list as a new row to an existing CSV document. In case the filename passed does not already exist, a new file is created with the given filename
# Input: A string containing the path of the CSV file being updated.
# Output: No returns. CSV file is updated with new row
# Exception: UnicodeEncodeError - accounts for characters requiring explicit encoding
def updateCSV(file_name, row):  # appends row passed to it to the csv file whose name is passed to it
    try:
        with open(file_name, 'a', newline='') as f:
            obj = csv.writer(f)
            obj.writerow(row)
            print(row)
    except UnicodeEncodeError:
        with open(file_name, 'a', newline='') as f:
            obj = csv.writer(f)
            obj.writerow(['UnicodeEncodeError was encountered here while crawling'])
            print('UnicodeEncodeError was encountered here while crawling')


# Desc: Visits the numpy libraries at GitHub.com and searches for all .py files and returns a list of links to each of the .py files
# Input: A list to which the .py files found are to be added. The url at which the numpy library is located in GitHub
# Output: Returns a list updated with the URLs of all the .py files located
# Exception: None
def list_updater(pylist, url):  # recurses till it acquires list of all .py files in directory

    # updateCSV('GitHub_numpy_database.csv',['NAME','DESCRIPTION','PARAMETERS','RETURNS'])

    page1_source_code = requests.get(url)
    plain = page1_source_code.text

    soup = BeautifulSoup(plain, "html.parser")

    for all_links in soup.findAll('a', {'class': 'js-navigation-open'}):

        links = all_links.get('href')
        title = all_links.get('title')

        if title != "Go to parent directory" and links.endswith('.py'):
            links = 'https://github.com/' + links
            pylist.append(links)
            print(links)

        elif title != "Go to parent directory" and "." not in links:
            print('Checking link:' + links)
            links = 'https://github.com/' + links
            pylist = list_updater(pylist, links)


        else:
            print('Not .py file or folder')

    return pylist


def main():
    pylist = []  # list of .py files

    pylist = list_updater(pylist, 'https://github.com/numpy/numpy/tree/master/numpy')  # returns list of all .py files in directory

    with open(r'C:\Users\rishi\PycharmProjects\numpy_crawler\venv\GitHub_numpy_database.csv','rt') as f:
        reader = csv.reader(f)
        func_list = []              #list of all the functions defined in the numpy libraries
        for row in reader:

            if row[0]=='' or row[0]== None or row[0] == 'NAME':
                pass
            else:
                f_name = row[0]

                #need to remove the args and just keep name...
                brace_position = f_name.find('(')
                f_name = f_name[:brace_position]
                func_list.append(f_name)

        for name in func_list:
            print(name)

    openWrite(pylist, func_list)


# Desc: The code fo each .py file in the list of URLs is copied to a CSV file called "numpy2.csv" and "GitHub_numpy_database.csv" is populated with relevant fields
# Input: A list of URLs leading to the .py files in GitHub that define various numpy functions
# Output: None.  CSV files "numpy2.csv" and "GitHub_numpy_database.csv" are created
# Exception: IndexError - Accounts for empty rows or rows that are limited to one column
def openWrite(url_list, func_list):

    updateCSV(r'C:\Users\rishi\PycharmProjects\numpy_crawler\venv\GH_Database3.csv',
              ['NAME', 'FUNCTION LOCATION', 'DESCRIPTION', 'PARAMETERS', 'RETURNS','DEPENDANCY','DEPENDANCY LOCATION'])

    for url in url_list:
        source = requests.get(url)
        txt = source.text

        soup = BeautifulSoup(txt)

        table = soup.find('table')
        table_rows = table.findAll('tr')
        line = 1



        dflag = 0
        pflag = 0
        rflag = 0
        comment = 0
        name_str = '' #stores name of the function
        desc_str = ''#stores the descripton of the function
        param_str = ''#stores the parameters of the function
        ret_str = '' # stores the returns of the function
        dep = []# stores functions that the functions is dependant on
        dep_loc = [] # stores if dependancy is an argument, in the body or in the return statement
        try:
            for tr in table_rows:
                td = tr.findAll('td')
                row = [i.text for i in td]
                row[0] = line

                line += 1

                loc_str = url

                for f_name in func_list:
                    if f_name in row[1] and not 'def '+f_name in row[1]: #if function name is present in string and it is not the function definition itself
                        dep.append(f_name)

                        if row[1].startswith('def '): #if some other function is being defined
                            dep_loc.append('Argument')

                        elif 'return' in row[1]:
                            dep_loc.append('Return')

                        else:
                            dep_loc.append('Body')

                if row[1].startswith('def '):
                    newfunc = 1
                    dflag = 0
                    pflag = 0
                    rflag = 0
                    #comment = 0
                    name_str = name_str.replace('def ', '')
                    desc_str = desc_str.replace('"""', '')
                    param_str = param_str.replace('    Parameters    ----------    ', '')
                    ret_str = ret_str.replace('    Returns    -------    ', '')

                    for dependant,dependant_location,count in zip(dep,dep_loc,range(1,10000)):
                        if count == 1:
                            updateCSV(r'C:\Users\rishi\PycharmProjects\numpy_crawler\venv\GH_Database3.csv',[name_str, loc_str, desc_str, param_str, ret_str,dependant,dependant_location])
                        else:
                            updateCSV(r'C:\Users\rishi\PycharmProjects\numpy_crawler\venv\GH_Database3.csv',['"', '"', '"', '"', '"', dependant, dependant_location])

                    name_str = ''
                    desc_str = ''
                    param_str = ''
                    ret_str = ''
                    dep_str = ''
                    dep_loc_str = ''
                    print(row[1])
                    name_str = name_str + row[1]

                if ' """' in row[1] or '"""' in row[1]:


                    if dflag == 0 and newfunc == 1:
                        dflag += 1
                        newfunc = 0
                    else:
                        dflag = 0

                if '    Parameters' == row[1]:
                    pflag += 1
                    dflag = 0

                if '    Returns' == row[1]:
                    rflag += 1
                    dflag = 0

                if dflag != 0:
                    desc_str = desc_str + row[1]
                    print(row[1])

                if pflag != 0:
                    param_str = param_str + row[1]
                    print(row[1])

                if rflag != 0:
                    ret_str = ret_str + row[1]
                    print(row[1])

                if '' == row[1] and pflag == 1:
                    pflag = 0

                if '' == row[1] and rflag == 1:
                    rflag = 0
        except IndexError:
            pass



main()
