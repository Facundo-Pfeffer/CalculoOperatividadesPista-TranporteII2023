import openpyxl


class ExcelManager:
    default_columns_range_value = tuple([chr(x) for x in range(65, 91)])  # Tupla de mayusculas de la A a la Z
    default_rows_range_value = tuple(range(1, 400))

    def __init__(self, file_name, sheet_name):
        wb = openpyxl.load_workbook(file_name, data_only=True)
        self.sh = wb[sheet_name]

    def get_value(self, column, row):
        return self.sh[f"{column}{row}"].value
