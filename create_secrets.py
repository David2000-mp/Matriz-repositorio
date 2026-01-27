#!/usr/bin/env python3
"""
Script para crear el archivo secrets.toml sin BOM
"""

content = '''google_sheets_id = "1FXoHqYH3TnesWAvYTWHnZ0LQyfc_E11zpFfL2b0nDGY"

[gcp_service_account]
type = "service_account"
project_id = "hybrid-shelter-426922-i8"
private_key_id = "9c6fc02fffb6dea31445a60a5b65e6457dbf4202"
private_key = """-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCexFiK/q0HoJbF\nKQxyuuYkvcqeOKAVoHHgBz7Y0kMzMHOQdbjUkdL9AW57jqzQpbxLSzCNhdT0Zd55\n7NpgNuGhfUm7lEQs4MROf+IFdZfux7ZL1VJJqBld6FpJrOP3ZYNdC14o8dwO95r/\nzNSz//xCQlDXlZ1eEAiOg+m7TmuO3Lbs8wNfzZKM9TV0I27VftOByYgYhgrBZSTW\nQt4ADDk2Qp9HbM0jTOZsBg5glEMv6zXz/QVXkJPLWSKV9/FvA2RPMPEaDhmpZt4E\nAbsvpepzvNock/ppsetw/TsN7GNJLaSkbPJMGHp2OLnA7hSEM20AKo1An/PD69bI\nZvLF/EPrAgMBAAECggEAExOPef/4xWJXy0/P1Zc8YOzHBDTUk1Soah0kwYOeHG/1\nasWiVDRDUDAUWNc/T4Cie7+IkXCjskvtK+Q4JvhhKvi1W8sIWAYXwEDgZPyIqWGo\ntzrl/MCsb5qkApc5+vdhDdR4V14cLVY18wdnBUu8QS/bq9OnyW4OwST7eAyHou4U\nh3E1jtmi5Ly/DUFAe1GSNfdU/0MMNOQyGKuZ9mi9a3Oc2b3wwy6jCJx9ga458Pxz\nUpfQR1Pfwse+usQ928f7KLqDTCLuiNjp64E7rBgSsJLOB3sYdpufItCEv/KxOdHC\n5swnpequO4SMIdk6gyGjskizJWg9TYJhJ+U78i1K0QKBgQDdz1AhSxTXK9u2muf5\nRzyJfDGrheLiarMltxioZhCRcyOeEIVypYwXj7iJaPB5V6Sl++5A5+PKARw4wPzg\nE68FiJjlW62XlxlGKy0wABb4lpm5PMJkqObZ624NmVHF90UJqhB6x/FFLCMLyRDD\numLNIYNh69wZf2AHved5cZoK+wKBgQC3PVeOtQWosK31kzZMdfS8Tz5D5xz1EoZm\nq6JYhFMlMiAd0/dhehUybj1LB2pz/smI/oGpbp0Ixen2vPDGObQEPq4m3k+EHE01\n6culffLB7E2l7a4eTgOQGfqKLNLiOXpO2pjbH+GyaffIIDruwkzZzhewSyVTt4+C\ncEIAsBpX0QKBgQDMWWS/Z4apvdRL5Wb197VEDNFN7qlaY2bsxkTHUFDPT75ur1Xi\ni7YHNveSUMXLZP1hljqoPXtU7bTsbJAMeNX0SSZjmBTT5fb4+GpHIK4JE+ZIDDwj\ntKAKAKaBjNETi31lK/LGy1HyonkfMHxrdln0Fn4ORted/gWg3EpXTlvW5QKBgC7V\n1/5a2JJwblZZhURv1dkX7BNRDD67uGyfrAQx9kqIkFrvZciderOEJ9h4kcYKNpr0\nalHTOwIWDCIL0wLnltKK7tpyciKTVUzVcD7hfV4BtysVIC8Qw6peaYJNyK0YAeIL\nz4wajwaaPUICsu157kixe66M1oKaZWzyonwohuMxAoGBAL9MfWvi838NuzIDqCNi\ncmSeeI1HfeJQLkF5nCwNEhPYuZOMI0An4mNEHFLxfjToFhTR97tZik7NpoG2xub8\ncGqAzOFHzldVwlkVADmVQIxWB3asSVSGzFvu7IwvEam+RziH0PlUkkNhx7cW+/TH\nW/l3OAoAvs6hJokZWyxw1NaX\n-----END PRIVATE KEY-----\n"""
client_email = "bot-matriz@hybrid-shelter-426922-i8.iam.gserviceaccount.com"
client_id = "117687675203601215901"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/bot-matriz%40hybrid-shelter-426922-i8.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
'''

with open('.streamlit/secrets.toml', 'w', encoding='utf-8') as f:
    f.write(content)

print('Archivo secrets.toml creado sin BOM')