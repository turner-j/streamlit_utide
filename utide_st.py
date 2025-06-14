import pandas as pd
from datetime import datetime, timedelta, time
from utide import solve, reconstruct
from matplotlib.dates import date2num
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from io import StringIO

url = "https://cims.coastal.louisiana.gov/DataDownload/DataDownload.aspx?type=hydro_hourly"

st.write("*Retrieve hourly hydrographic data from the [CIMS database](%s).*" % url)
st.write("*Filter data by CRMS site. For example: CRMS0479 for Wax Lake Delta.*")
st.write("*Choose the most recent month of data. Download and unzip the folder.*")

uploaded_file = st.file_uploader("Choose a csv file.")

if uploaded_file is not None:
	# Can be used wherever a "file-like" object is accepted:
	dff = pd.read_csv(uploaded_file,encoding='ISO-8859-1')
	dff['DateTime'] = pd.to_datetime(dff['Date (mm/dd/yyyy)'] + ' ' + dff['Time (hh:mm:ss)'], format='%m/%d/%Y %H:%M:%S')
	df = dff[["DateTime","Adjusted Water Level (ft)"]].copy()
	st.write(df)
	
	lat = -29
	dt = df["DateTime"].values
	
	coef = solve(dt,df['Adjusted Water Level (ft)'].values,lat=lat,method='harmonic',conf_int='linear')
	today = datetime.now()- timedelta(days=5)
	future = datetime.now() + timedelta(days=9)
	
	d = st.date_input("Choose a range of dates to forecast",value = (today, future),format="MM/DD/YYYY")
	
	start = d[0]
	start_date = datetime.combine(start, time(0,0))
	end_dt = d[1]
	end_date = datetime.combine(end_dt, time(0,0))
	
	# Generate list of hourly datetime objects
	hourly_datetimes = []
	current_time = start_date
	
	while current_time <= end_date:
		hourly_datetimes.append(current_time)
		current_time += timedelta(hours=1)
	
	tide = reconstruct(hourly_datetimes, coef)

	T = pd.DataFrame({'date': hourly_datetimes, 'predicted tide ht': tide.h})

	st.line_chart(T, x="date", y="predicted tide ht", x_label=None, y_label="Predicted tide ht (ft)")
