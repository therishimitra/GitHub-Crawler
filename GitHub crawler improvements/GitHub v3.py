"""
HOW TO RUN:
To run execute the function: main().
This is done by execiting the script of "GitHub v3.py"

IMPORTANT:
Before running ensure GitHub_numpy_database.csv and numpy2.csv do not already exist.
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


# Desc: Main function that controls the flow of contorl of the data retrieval and database creation processes.
# Input: None
# Output: None
# Exception: None
def main():
    pylist = []  # list of .py files

    pylist = list_updater(pylist,
                          'https://github.com/numpy/numpy/tree/master/numpy')  # returns list of all .py files in directory
    # print(pylist)
    # print(len(pylist) , '.py files found')

    openWrite(pylist)


# Desc: The code fo each .py file in the list of URLs is copied to a CSV file called "numpy2.csv" and "GitHub_numpy_database.csv" is populated with relevant fields
# Input: A list of URLs leading to the .py files in GitHub that define various numpy functions
# Output: None.  CSV files "numpy2.csv" and "GitHub_numpy_database.csv" are created
# Exception: IndexError - Accounts for empty rows or rows that are limited to one column
def openWrite(url_list):

    updateCSV(r'C:\Users\rishi\PycharmProjects\numpy_crawler\venv\GitHub_numpy_database.csv',
              ['NAME', 'LOCATION', 'DESCRIPTION', 'PARAMETERS', 'RETURNS'])

    for url in url_list:
        source = requests.get(url)
        txt = source.text

        soup = BeautifulSoup(txt)

        table = soup.find('table')
        table_rows = table.findAll('tr')
        line = 1

        updateCSV(r'C:\Users\rishi\PycharmProjects\numpy_crawler\venv\numpy2.csv', ['Function:', url])

        dflag = 0
        pflag = 0
        rflag = 0
        name_str = ''
        desc_str = ''
        param_str = ''
        ret_str = ''

        try:
            for tr in table_rows:
                td = tr.findAll('td')
                row = [i.text for i in td]
                row[0] = line

                updateCSV(r'C:\Users\rishi\PycharmProjects\numpy_crawler\venv\numpy2.csv', row)
                line += 1

                loc_str = url

                if row[1].startswith('def '):
                    newfunc = 1
                    dflag = 0
                    pflag = 0
                    rflag = 0
                    name_str = name_str.replace('def ', '')
                    desc_str = desc_str.replace('"""', '')
                    param_str = param_str.replace('    Parameters    ----------    ', '')
                    ret_str = ret_str.replace('    Returns    -------    ', '')

                    updateCSV(r'C:\Users\rishi\PycharmProjects\numpy_crawler\venv\GitHub_numpy_database.csv',
                              [name_str, loc_str, desc_str, param_str, ret_str])

                    name_str = ''
                    desc_str = ''
                    param_str = ''
                    ret_str = ''
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
