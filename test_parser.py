import unittest
import parser_api
import cantools
import os
class test_parser(unittest.TestCase):
    def test_dbc(self):
        db = parser_api.get_dbc_files('dbc-files')
        dbc_path = parser_api.os.listdir('dbc-files')
        print(dbc_path)
        print("test")
        test_db = parser_api.cantools.database.Database()
        for filename in dbc_path:
            if ".dbc" in filename or ".DBC" in filename:
                filename="dbc-files/"+filename
                print(filename)
                with open (str(os.path.join(os.getcwd(),filename)), 'r') as newdbc:
                    test_db.add_dbc(newdbc)
        print(newdbc)

        self.assertEqual(test_db.is_similar(db),True)
        
    def test_func(self):
        db = parser_api.get_dbc_files('dbc-files')
        os.chdir('test/raw-data')
        parser_api.parse_file(r'MDY_10-24-2023_HMS_22-40-38.CSV',dbc=db)
        
if __name__ == '__main__':
    unittest.main()