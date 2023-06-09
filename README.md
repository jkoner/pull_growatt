# Overview
This little script pulls data from the growatt inverter and writes it to influx
I call it regularly via cron

# Dependencies
https://github.com/otti/Growatt_ShineWiFi-S.git is used to read data from the inverter.

# Function
1. Read the fields from the CSV file and store them in a list.
2. Create a dictionary called store, which will be used to store the values of the fields.
3. For every field in the list, do the following:
    a. Read the value from the register via HTTP.
    b. Store the value in the dictionary.
4. Create a timestamp.
5. Create a client for InfluxDB.
6. Write the data to InfluxDB.
7. Log that the data has been written to InfluxDB.