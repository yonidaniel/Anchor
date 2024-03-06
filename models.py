from sqlalchemy.orm import declarative_base
from typing import Dict, Union
from sqlalchemy import Column, Integer, JSON

Base = declarative_base()


def extract_ref_col_row(value: str) -> list[str]:
    if not value.startswith("lookup("):
        raise ValueError("Invalid formula format")

    # Split by comma, handling spaces around the comma
    parts = value[7:-1].strip().split(",")

    if len(parts) != 2:
        raise ValueError("Invalid number of arguments in formula")

    # Remove any leading/trailing spaces from extracted parts
    for i in range(len(parts)):
        parts[i] = parts[i].strip()

    return parts


class Spreadsheet(Base):
    __tablename__ = "spreadsheets"

    id = Column(Integer, primary_key=True)
    schema = Column(JSON)  # Store column definitions
    data = Column(JSON)  # Store cell values in a nested dictionary format

    def get_sheet(self) -> Dict[tuple[str, int], Union[str, bool]]:
        sheet = {}
        for col, row_values in self.data.items():
            for row, value in row_values.items():
                sheet[col, row] = value
        return sheet

    def get_deep_sheet(self) -> Dict[tuple[str, int], Union[str, bool]]:
        sheet = {}
        for col, row_values in self.data.items():
            for row, value in row_values.items():
                sheet[col, row] = self.get_endpoint_cell_value(col, row)
        return sheet

    def set_cell(self, col: str, row: int, value: Union[str, bool, float, int]):
        if not self.__is_column_exist(col):
            raise ValueError(f"Invalid column name {col}")

        col_type = self.get_column_type(col)

        supported_type_map = {
            "int": int,
            "float": float,
            "string": str,
            "bool": bool,
        }

        # Check if the type string exists in the mapping
        if col_type not in supported_type_map:
            raise ValueError(f"Invalid type name: {col_type}")

        if supported_type_map[col_type] != type(value):
            raise ValueError(f"Invalid value type for type {col_type} column: {value} is type of {type(value)}")

        match value:
            case str():
                if value.startswith("lookup"):

                    # Extract referenced column and row from formula
                    ref_col, ref_row = extract_ref_col_row(value)

                    # Validate referenced column and row
                    column_exists = any(d['name'] == ref_col for d in self.schema["columns"])
                    if not column_exists:
                        raise ValueError(f"Missing column {ref_col}")

                    if ref_row not in self.data[ref_col]:
                        raise ValueError(f"Missing value {ref_row} in column {ref_col}")

                    if int(ref_row) == row and ref_col == col:
                        raise ValueError("Formula cannot reference the same cell")

                    if str(ref_row) not in self.data[ref_col]:
                        raise ValueError(f"Missing value {ref_row} in column {ref_col}")

                    ref_col_type = self.get_column_type(ref_col)
                    if ref_col_type != "string":
                        raise ValueError(f"Column {ref_col} is type: ({ref_col_type}), but only string refs allowed")

                    cell_value = self.get_cell_value(ref_col, ref_row)
                    while cell_value.startswith("lookup"):
                        ref_col, ref_row = extract_ref_col_row(cell_value)
                        if ref_col == col and ref_row == str(row):
                            raise ValueError("Cyclic ref detected: can't add")
                        cell_value = self.get_cell_value(ref_col, ref_row)

        self.__update(col, row, value)

    def get_cell_value(self, col, row) -> str:
        if not self.__is_column_exist(col):
            raise ValueError(f"Invalid column name {col}")

        if row not in self.data[col]:
            raise ValueError(f"Invalid row index {row}")

        return str(self.data[col][row])

    def get_endpoint_cell_value(self, col, row) -> str:
        cell_value = self.get_cell_value(col, row)
        while cell_value.startswith("lookup"):
            col, row = extract_ref_col_row(self.get_cell_value(col, row))
            cell_value = self.get_cell_value(col, row)
        return cell_value

    def get_column_type(self, column_name) -> str:
        column_schema_data = [column for column in self.schema['columns'] if column['name'] == column_name]
        return str(column_schema_data[0]['type'])

    def __update(self, col: str, row: int, value: Union[str, bool, float, int]):
        if col not in self.data:
            self.data[col] = {}  # Create an empty dictionary for the new column

        self.data[col][str(row)] = value  # Update the value at the desired row

    def __is_column_exist(self, col: str) -> bool:
        # Check that the column exist in the spreadsheet
        if col not in [column['name'] for column in self.schema['columns']]:
            return False
        return True
