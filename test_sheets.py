import gspread

gc = gspread.service_account(filename="service_account.json")
sheet = gc.open_by_key("1m6WKFC3Zb1RnYCCddzPWFS-YHEzfrBcQH-j4PklLKWg")
worksheet = sheet.worksheet("Blad1")

worksheet.append_row(["✅ Sheet connection successful!", "Test from Ghost Employee"])
