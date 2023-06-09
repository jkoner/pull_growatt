import datetime
from time import sleep
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import requests
import csv
import logging
import configparser as configparser
import os

path = os.path.dirname(os.path.abspath(__file__))   #get path of this file

configparser = configparser.ConfigParser()
configparser.read(path + '/config.ini')


FORMAT = ('%(asctime)-15s %(levelname)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)

#write log to file
fh = logging.FileHandler(path + "/" + configparser['Logging']['LogFile'])
configparser['Logging']['LogLevel'] = configparser['Logging']['LogLevel'].upper()
if configparser['Logging']['LogLevel'] == 'DEBUG':
    fh.setLevel(logging.DEBUG)
elif configparser['Logging']['LogLevel'] == 'INFO':
    fh.setLevel(logging.INFO)
elif configparser['Logging']['LogLevel'] == 'WARNING':
    fh.setLevel(logging.WARNING)
elif configparser['Logging']['LogLevel'] == 'ERROR':
    fh.setLevel(logging.ERROR)
elif configparser['Logging']['LogLevel'] == 'CRITICAL':
    fh.setLevel(logging.CRITICAL)
else:
    fh.setLevel(logging.INFO)

fh.setFormatter(logging.Formatter(FORMAT))
log.addHandler(fh)



# read fields from csv file with structure name, offset, type, factor
fields = []
with open(path + "/" + configparser['Growatt']['FieldFile'], 'r') as csvfile:
    filereader = csv.reader(csvfile, delimiter=';')
    for row in filereader:
        fields.append({'offset': row[0], 'name': row[1], 'type': row[2], 'factor': row[3], 'destType': row[4]})

store = {}

for field in fields:
    i=0
    while i<3:
        try:
            # query post data via http from http:// 
            response = requests.post(configparser['Growatt']['ServerURL'], data={'reg': field['offset'], 'val': '', 'type': field['type'], 'operation': 'R', 'registerType': 'I'})
            if field['destType'].strip() == 'float':
                store[field['name']] = int(response.text)* float(field['factor']) 
            else:
                store[field['name']] = int(int(response.text)* float(field['factor']))

            log.debug(field['name'] + ': ' + str(store[field['name']]))
            break
        except:
            log.warning('Retry reading ' + field['name'] + ' from growatt.lan. Try ' + str(i+1) + ' of 3')
            sleep(1)
            i=i+1
        finally:
            if i==3:
                log.error('Failed reading ' + field['name'] + ' from growatt.lan. Giving up.')
                
# create timestamp in format 2021-01-01T00:00:00Z
timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

client = InfluxDBClient(url=configparser['Influx']['ServerURL'], token=configparser['Influx']['Token'], org=configparser['Influx']['Org'])
write_api = client.write_api(write_options=SYNCHRONOUS)

# write to influxdb
write_api.write(bucket=configparser['Influx']['Bucket'], record=[{"measurement": "tlx_detail", "fields": store, "time": timestamp}])
log.info('Data written to influxdb')