import streamlit as st
import pandas as pd
import random
import traceback
from datetime import date
import datetime
from template import *
import os

import io

# buffer to use for excel writer
buffer = io.BytesIO()

DE_PATH = os.getcwd() + '/guest_app/'
# BU_PATH = ''

st.set_page_config(
	page_title="Dashboard", page_icon=None, layout="wide", initial_sidebar_state="auto"
)
st.markdown("##")

UI()
st.markdown("##")

todayDate = datetime.date.today()
# currentYear = date.today().year
rondomNumber = random.randint(0, 10000)

# load excel file
try:
	df = pd.read_excel(DE_PATH+"data.xlsx", sheet_name="Sheet1")
except Exception as e:
	df = pd.read_excel("data.xlsx", sheet_name="Sheet1")

exchange_rate = 0.00025 # usd/1khr

# top analytics
def Analytics():
	amount = float(df["amount"].sum())
	
	df_group_currency = df.groupby(['currency'])['amount'].agg('sum').reset_index(name="total")
	total = 0
	
	
		
	if 'USD' in df_group_currency['currency'].values:
		usd = df_group_currency[df_group_currency["currency"]=='USD']["total"].to_list()[0]

	else:
		usd = 0
	

	if 'total_usd' not in st.session_state:
		st.session_state['total_usd'] = usd
	
	total = st.session_state['total_usd']
	
	if 'KHR' in df_group_currency['currency'].values:
		khr = df_group_currency[df_group_currency["currency"]=='KHR']["total"].to_list()[0]
		usd_per_khr = khr * exchange_rate
	else:
		khr = 0
		usd_per_khr = 0
	
	if 'total_khr' not in st.session_state:
		st.session_state['total_khr'] = khr
	
	if 'usd_per_khr' not in st.session_state:
		st.session_state['usd_per_khr'] = usd_per_khr
	
	
	total = total + st.session_state['usd_per_khr']

	if 'total' not in st.session_state:
		st.session_state['total'] = total


	# 3. columns
	total1, total2, total3 = st.columns(3, gap="small")
	with total1:
		st.info("Currency USD")
		# st.metric(label="USD", value=f"{usd:,.0f} $")
		st.metric(label="USD", value=f"{st.session_state['total_usd']:,.0f} $")

	with total2:
		st.info("Currency KHR")
		st.metric(label="KHR", value=f"{st.session_state['total_khr']:,.0f} ៛")

	with total3:
		st.info("Total USD")
		st.metric(label="USD", value=f"{st.session_state['total']} $")



def my_callback():
	
	currency = st.session_state.Currency
	amount = st.session_state.Amount

	if currency=='USD':
		st.session_state['total_usd'] += amount
		st.session_state['total']+= amount
	elif currency=='KHR':
		st.session_state['total_khr'] += amount
		usd_per_khr = amount * exchange_rate
		st.session_state['total_usd'] += usd_per_khr
		st.session_state['total']+= usd_per_khr
	
	# st.session_state.Name = ""
	# st.session_state.Method = ""
	# st.session_state.Currency=""
	# st.session_state.Amount=0

# st.session_state['total_usd'] += 10

Analytics()
st.markdown("""---""")

# form
st.sidebar.header("Add New Product")

if 'error_form' in st.session_state:
	st.warning(st.session_state['error_form'])
	del st.session_state['error_form']

options_form = st.sidebar.form("Option Form")
name         = options_form.text_input("Name", key="Name")
method       = options_form.selectbox("Method", {"","ABA", "Acleda","Cash"}, key="Method")
currency     = options_form.selectbox("Currency", {"","USD", "KHR"}, key="Currency")
amount       = options_form.number_input("Amount", key="Amount")
added_date   = options_form.text_input("Added Date", value=todayDate, disabled=True, key="Added_Date")
add_data     = options_form.form_submit_button(label="Add new record", on_click=my_callback)
# add_data     = options_form.form_submit_button(label="Add new record")


# when button is clicked
if add_data:

	if name != "":
		# my_callback(amount, currency)

		# st.session_state['total_usd'] += amount
		# st.write("HELLO WORLD")

		df = pd.concat(
			[
				df,
				pd.DataFrame.from_records(
					[
						{
							"name": name,
							"method": method,
							"currency": currency,
							"amount": float(amount),
							"added_date": added_date,
						}
					]
				),
			]
		)
		try:
			try:
				df.to_excel(DE_PATH+"data.xlsx", index=False)
			except Exception as e:
				df.to_excel("data.xlsx", index=False)

			# df.to_excel(DE_PATH+"data.xlsx", index=False)
			# name.value = ""
		except Exception as e:
			traceback.print_exc()
			st.warning("Unable to write: "+str(e))

	else:
		st.sidebar.error("Name is required.")
		st.session_state['error_form'] = "Name is required"

show_column = 	[	"name",
					"method",
					"currency",
					"amount",
					"added_date"]


# download button 2 to download dataframe as xlsx
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
	# Write each dataframe to a different worksheet.

	df.to_excel(writer, sheet_name='Sheet1', index=False)
	
	try:
		writer.close()
	except Exception as e:
		pass

	download2 = st.download_button(
		label="Download data as Excel",
		data=buffer,
		file_name='data.xlsx',
		mime='application/vnd.ms-excel',
		key="export_excel"
	)

st.dataframe(df[show_column], use_container_width=True)


# print (df_group_)


with st.expander("Cross Tab"):
	tab = pd.crosstab([df.method], df.amount, margins=True)
	df_group = df.groupby(["method","currency"])["amount"].agg("sum").reset_index(name="total_amount")
	st.dataframe(df_group,use_container_width=True)

