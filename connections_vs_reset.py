import datetime as dt

import requests
import json
import base64
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
import time
import matplotlib.ticker as mtick
from operator import itemgetter
import os
import PySimpleGUI as sg
import sys

#  API_ADDRESS = "https://api.smartsensor.abb.com"
from docx import *
from docx.shared import Inches


def authenticate(api_key, addr):
    # Returns authentication token for the given API Key
    url = f"{addr}/Auth/Key"
    body = {'apiKey': api_key, 'deviceUID': "string"}
    # Making a request
    r = requests.post(url, json=body)
    if r.status_code == 200:
        # Converting json response to dictionary
        result = json.loads(r.text)
        # Getting the token from the dictionary
        token = result["authToken"]
        return token
    else:
        return ""


def collect_latest_raw_data(api_key, addr, sn, id):
    token = authenticate(api_key, addr)
    url = f"{addr}/Sensor/Feature/Value/{sn}"
    params = {'sensorTypeID': id, 'featureTypes': "RawDataCollectionCSV", 'complexObject': True}
    header = {'Authorization': f'Bearer {token}'}

    r = requests.get(url, params=params, headers=header)
    if r.status_code == 200:
        result = json.loads(r.text)
        # Getting the file name and content from the response
        file_name = result[0]["featureValue"][0]['fileName']
        content_encoded = result[0]["featureValue"][0]['fileContent']
        # Decoding base64 content
        content_bytes = content_encoded.encode('ascii')
        file_bytes = base64.b64decode(content_bytes)
        file_content = file_bytes.decode('ascii')
        # Writing csv file
        with open(file_name, 'w') as f:
            f.write(file_content)
        print(f"File {file_name} successfully written")


def get_sensor_feature(api_key, addr, sn, id, feature_types):
    token = authenticate(api_key, addr)
    url = f"{addr}/Sensor/Feature/{sn}"
    params = {'sensorTypeID': id, 'featureTypes': "SensorSelfTest", }
    header = {'Authorization': f'Bearer {token}'}

    response = requests.get(url, params=params, headers=header)

    if response.content is b'':
        return None
    response_json = json.loads(response.content)

    # Return None if the response code indicates an error
    if response.status_code != 200:
        # self._logger.debug('Error: Response Code ' + str(response.status_code) + " " + response_json)
        return None
    return response_json


def collect_all_raw_data(api_key, addr , sn, id, start_date, end_date):
    token = authenticate(api_key, addr)
    url = f"{adde}/Sensor/Feature/{sn}"
    params = {'sensorTypeID': id, 'featureTypes': "RawDataCollectionCSV", 'from': start_date, 'to': end_date,
        'complexObject': True}
    header = {'Authorization': f'Bearer {token}'}

    r = requests.get(url, params=params, headers=header)
    if r.status_code == 200:
        result = json.loads(r.text)
        # Getting the file name and content from the response
        for res in result:
            file_name = res["featureValue"][0]['fileName']
            content_encoded = res["featureValue"][0]['fileContent']
            # Decoding base64 content
            content_bytes = content_encoded.encode('ascii')
            file_bytes = base64.b64decode(content_bytes)
            file_content = file_bytes.decode('ascii')
            # Writing csv file
            with open(file_name, 'w') as f:
                f.write(file_content)
            print(f"File {file_name} successfully written")


def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

# removes invalid date entries
def sort_vals(lst1, lst2, x_val):

    idx = 0
    trim_lst = []
    for z in x_val:
        if z < 1514768400:
            trim_lst.append(idx)
        idx = idx + 1

    idx = 0
    for t in trim_lst:
        lst1.pop(t-idx)
        lst2.pop(t-idx)
        x_val.pop(t-idx)
        idx = idx + 1
    return lst1, lst2, x_val


def main():

    # User input:
    #   api_key - key obtained from portal,
    #   sensor_serial_number - sensor that
    #                          we want to read raw data from
    #   sensor_type_id - the id of the sensor type.
    #                    For mounted bearigs the type is 3

    # user menu
    layout = [  [sg.Text("Sensor Serial Number")],
                [sg.Input(key = 'sensor_num')],
                [sg.Text("Graph Type")],
                [sg.Radio('Connections', "RADIO1", key = 'conn'), sg.Radio('Resets', "RADIO1", key = 'res'), sg.Radio('Both', "RADIO1", key = 'both')],
                [sg.Button('Graph', bind_return_key=True), sg.Button('Exit')]
    ]

    window = sg.Window('Sensor Battery Check', layout)
    while True:
        event, values = window.read()

        if event == 'Graph':

            prod_key = "WkdKaE9XVmtZemt0WTJSbE5pMDBObVk0TFdJd09UTXRObUl3WWpjMVpETXlORE5s"
            beta_key = "TjJFek1UUm1ZamN0TkdGa01TMDBaamxtTFRrNVpEQXRNamN5WVdFeFpXSm1OekU1"

            api_add = "https://api.smartsensor.abb.com"
            api_key = prod_key

            api_add = "https://api.smartsensor.abb.com"
            api_key = prod_key
            print(api_add)
            print(api_key)

            # change to sn[1] if you are using MAC address in sensor list
            sensor_serial_number = values['sensor_num']
            sensor_type_id = 3
            start_date = "2020.05.13"
            end_date = "2020.06.16"
            feature_values = get_sensor_feature(api_key, api_add, sensor_serial_number, 3, 'SensorSelfTest')
            f_sort = sorted(feature_values, key=itemgetter('featureKeySequenceNo'))
            lst = []

            # csv = open("test_csv.csv", "w")  # "w" indicates that you're writing strings to the file
            for f in f_sort:
                lst.append(flatten_json(f['featureValue']))
            lst_sorted = sorted(lst, key=itemgetter('timestamp'))
            print(lst)

            x_val = [x['timestamp'] for x in lst_sorted]
            y1_temp = [x['numberOfConnections'] for x in lst_sorted]
            y2_temp = [x['numberOfActivations'] for x in lst_sorted]

            # remove invalid number of conn entries
            y1 = [0 if x is None else x for x in y1_temp] # replace none with 0
            y2 = [0 if x is None else x for x in y2_temp] # replace none with 0
            y1, y2, x = sort_vals(y1, y2, x_val)

            # convert timestamps to date objects
            dates = [dt.datetime.fromtimestamp(ts) for ts in x]
            print(dates)

            # used for x axis range
            start = dates[0]
            end = dates[-1]

            # plot only connections
            if values['conn'] == True:
                if len(y1) > 2:
                    # new subplot figure
                    fig, ax = plt.subplots()

                    if x[len(x) - 1] < (time.time() - 604800):  # if last entry more than a week ago sensor is probably dead
                        fig.suptitle("SN " + sensor_serial_number + " DEAD!!")
                    else:
                        fig.suptitle("SN " + sensor_serial_number)

                    # only show valid dates on x axis
                    ax.set_xlim([start, end])

                    # convert from timestamp to standard date format
                    fmt = mdates.DateFormatter('%m-%d-%Y')
                    ax.xaxis.set_major_formatter(fmt)

                    ax.plot(dates, y1)

                    ax.set_ylabel('Connections')

                    # rotate labels 
                    plt.gcf().autofmt_xdate()
                    plt.tight_layout()

                    # need block = False so that pysimpleGUI can run
                    plt.show(block = False)
                else:
                    sys.exit('Not enough data to graph.')

            # plot connections and resets
            elif values['both'] == True:
                if (len(y1) and len(y2)) > 2:
                    # new subplot figure
                    fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True)

                    if x[len(x) - 1] < (time.time() - 604800):  # if last entry more than a week ago sensor is probably dead
                        fig.suptitle("SN " + sensor_serial_number + " DEAD!!")
                    else:
                        fig.suptitle("SN " + sensor_serial_number)

                    # only show valid dates on x axis
                    ax[0].set_xlim([start, end])

                    # convert from timestamp to standard date format
                    fmt = mdates.DateFormatter('%m-%d-%Y')
                    ax[0].xaxis.set_major_formatter(fmt)
                    ax[1].xaxis.set_major_formatter(fmt)

                    ax[0].plot(dates, y1)
                    ax[1].plot(dates, y2)

                    ax[0].set_ylabel('Connections')
                    ax[1].set_ylabel('Resets')

                    # rotate labels
                    plt.gcf().autofmt_xdate()
                    plt.tight_layout()

                    # need block = False so that pysimpleGUI can run
                    plt.show(block = False)
                else:
                    sys.exit('Not enough data to graph.')

            # plot only resets
            elif values['res'] == True:
                if len(y1) > 2:
                    # new subplot figure
                    fig, ax = plt.subplots()

                    if x[len(x) - 1] < (time.time() - 604800):  # if last entry more than a week ago sensor is probably dead
                        fig.suptitle("SN " + sensor_serial_number + " DEAD!!")
                    else:
                        fig.suptitle("SN " + sensor_serial_number)

                    # only show valid dates on x axis
                    ax.set_xlim([start, end])

                    # convert from timestamp to standard date format
                    fmt = mdates.DateFormatter('%m-%d-%Y')
                    ax.xaxis.set_major_formatter(fmt)

                    ax.plot(dates, y2)

                    ax.set_ylabel('Resets')

                    # rotate labels
                    plt.gcf().autofmt_xdate()
                    plt.tight_layout()

                    # need block = False so that pysimpleGUI can run
                    plt.show(block = False)
                else:
                    sys.exit('Not enough data to graph.')
            else:
                sys.exit("No selection was made.")

        if event == sg.WIN_CLOSED or event == "Exit":
            sys.exit()
    # close pysimpleGUI window and now matploblib GUI can be shown
    window.close()
    plt.show()

if __name__ == "__main__":
    main()
    sys.exit()