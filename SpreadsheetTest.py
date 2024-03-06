import unittest

from models import Spreadsheet


class SpreadsheetTest(unittest.TestCase):

    def setUp(self) -> None:
        self.sheet = Spreadsheet()
        self.sheet.schema = {
            "columns": [
                {"name": "col1", "type": "string"},
                {"name": "col2", "type": "int"},
                {"name": "col3", "type": "bool"},
                {"name": "col4", "type": "string"}
            ]
        }
        self.sheet.data = {
            "col1": {"1": "value1", "2": "value2"},
            "col2": {"1": 10, "2": 20},
            "col3": {"1": True, "2": False},
            "col4": {"1": "value1", "2": "value2"},
        }

    def test_get_sheet(self):
        expected_sheet = {
            ("col1", "1"): "value1",
            ("col1", "2"): "value2",
            ("col2", "1"): 10,
            ("col2", "2"): 20,
            ("col3", "1"): True,
            ("col3", "2"): False,
            ("col4", "1"): "value1",
            ("col4", "2"): "value2"
        }
        self.assertEqual(self.sheet.get_sheet(), expected_sheet)

    def test_set_cell_valid_value(self):
        self.sheet.set_cell("col1", 3, "new_value")
        self.assertEqual(self.sheet.data["col1"]["3"], "new_value")

    def test_set_cell_invalid_column(self):
        with self.assertRaises(ValueError) as e:
            self.sheet.set_cell("invalid_col", 1, "value")
        self.assertEqual(str(e.exception), "Invalid column name invalid_col")

    def test_get_cell_value_invalid_column(self):
        with self.assertRaises(ValueError) as e:
            self.sheet.get_cell_value("invalid_col", 1)
        self.assertEqual(str(e.exception), "Invalid column name invalid_col")

    def test_get_cell_value_invalid_row(self):
        with self.assertRaises(ValueError) as e:
            self.sheet.get_cell_value("col1", 10)
        self.assertEqual(str(e.exception), "Invalid row index 10")

    def test_set_cell_invalid_type(self):
        with self.assertRaises(ValueError) as e:
            self.sheet.set_cell("col2", 1, "invalid_value")
        self.assertEqual(str(e.exception),
                         "Invalid value type for type int column: invalid_value is type of <class 'str'>")

    def test_set_cell_lookup_valid_reference(self):
        # Reference a valid cell with string type
        self.sheet.set_cell("col4", 4, f"lookup(col1,2)")
        self.assertEqual(self.sheet.get_endpoint_cell_value("col4", "4"), "value2")

    def test_set_cell_lookup_invalid_column_reference(self):
        with self.assertRaises(ValueError) as e:
            self.sheet.set_cell("col4", 3, f"lookup(invalid_col,2)")
        self.assertEqual(str(e.exception), "Missing column invalid_col")

    def test_set_cell_lookup_missing_row_reference(self):
        with self.assertRaises(ValueError) as e:
            self.sheet.set_cell("col4", 3, f"lookup(col1,10)")
        self.assertEqual(str(e.exception), "Missing value 10 in column col1")

    def test_set_cell_lookup_self_reference(self):
        with self.assertRaises(ValueError) as e:
            self.sheet.set_cell("col1", 2, f"lookup(col1,2)")
        self.assertEqual(str(e.exception), "Formula cannot reference the same cell")

    def test_set_cell_lookup_cyclic_reference(self):
        self.sheet.set_cell("col1", 3, f"lookup(col1,1)")
        self.sheet.set_cell("col4", 3, f"lookup(col1,3)")
        with self.assertRaises(ValueError) as e:
            self.sheet.set_cell("col1", 1, f"lookup(col4,3)")
        self.assertEqual(str(e.exception), "Cyclic ref detected: can't add")

    def test_set_cell_lookup_invalid_ref_type(self):
        # Reference a non-string type column
        with self.assertRaises(ValueError) as e:
            self.sheet.set_cell("col4", 3, f"lookup(col2,2)")
        self.assertEqual(str(e.exception),
                         f"Column col2 is type: ({self.sheet.get_column_type('col2')}), but only string refs allowed")

    def test_get_endpoint_cell_value_non_lookup(self):
        cell_value = self.sheet.get_endpoint_cell_value("col1", "1")
        self.assertEqual(cell_value, "value1")

    def test_set_cell_lookup_nested(self):
        # Set nested lookup formula
        self.sheet.set_cell("col4", 4, f"lookup(col1, 2)")
        self.sheet.set_cell("col4", 5, f"lookup(col4, 4)")
        cell_value = self.sheet.get_endpoint_cell_value("col4", "5")
        self.assertEqual(cell_value, "value2")

    def test_like_demo(self):
        self.sheet.schema = {
                "columns": [
                    {"name": "A", "type": "string"},
                    {"name": "B", "type": "bool"},
                    {"name": "C", "type": "string"}
                ]
            }
        self.sheet.data = {}

        self.sheet.set_cell("A", 10, "hello")
        self.sheet.set_cell("B", 11, True)
        self.sheet.set_cell("C", 1, "lookup(A,10)")

        v = self.sheet.get_deep_sheet()
        print(v)
