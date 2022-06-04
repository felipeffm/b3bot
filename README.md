#### Script goal: 
Receive alerts of financial assets trend change in smartphone.

#### How it works: 
In a daily frequency, download data with Yahoo Finance API and detect trend changes by 3 moving averaging curves and send an alert by email

#### Why?
This project was build for my uncle, who wanted to receive alerts in real time when 
trend changes happened because it is very time consuming check assets along the day. 


##### Getting Started
######main.py
app.py-> download data, analyse data, store results in excel and send email.

#####utils
gera_banco.py -> generate sqlite with historical data
utils_mm.py -> functions
dag_airflow.py-> dag in airflow

##### Examples
###### Write here
