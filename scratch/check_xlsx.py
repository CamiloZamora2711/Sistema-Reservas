import openpyxl

wb = openpyxl.load_workbook('usuarios.xlsx')
ws = wb.active

for row in ws.iter_rows(min_row=1, max_row=5, values_only=True):
    print(row)
