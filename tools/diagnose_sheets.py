import traceback
from utils import data_manager as dm
import streamlit as st

print('st.secrets has gcp_service_account:', 'gcp_service_account' in st.secrets)
try:
    ss = dm.conectar_sheets()
    print('conectar_sheets returned:', type(ss))
    if ss:
        try:
            print('Spreadsheet title:', ss.title)
        except Exception as e:
            print('Could not read spreadsheet title:', e)
    else:
        print('conectar_sheets returned None')
except Exception as e:
    print('conectar_sheets raised exception:')
    traceback.print_exc()
