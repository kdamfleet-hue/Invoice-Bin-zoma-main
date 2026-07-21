import openpyxl

file_path = 'static/washing_template.xlsx'
try:
    wb = openpyxl.load_workbook(file_path)
    # openpyxl by default does not preserve images perfectly unless configured, 
    # saving it might rebuild the relationships/anchors to be compatible with exceljs!
    
    # Just in case, let's look for drawings and remove them to be absolutely sure
    for sheet in wb.worksheets:
        sheet._images = []
        sheet._drawings = []
        if hasattr(sheet, 'legacy_drawing'):
            sheet.legacy_drawing = None

    wb.save('static/washing_template_fixed.xlsx')
    print("Fixed excel saved to static/washing_template_fixed.xlsx")
except Exception as e:
    print(f"Error: {e}")
