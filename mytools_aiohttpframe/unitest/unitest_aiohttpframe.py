# coding=utf-8

import unittest

# 检查项目
from mytools_aiohttpframe import AiohttpFrame_Config,AiohttpFrame_Browser,AiohttpFrame_Login

class Test_sqlite3_tools(unittest.TestCase):
    
    def setUp(self):
        pass
        # self.browser = AiohttpFrame_Browser.AiohttpFrame_Browser()
    
    def test_AiohttpFrame_Config(self):
        datas = [AiohttpFrame_Config.chrome_path,
                 AiohttpFrame_Config.cookies_jsonfile,
                 AiohttpFrame_Config.defaultEncoding,
                 AiohttpFrame_Config.headers,
                ]
        checks = ['C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe',
                  'cookie.json',
                  'utf-8',
                  {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' \
                   ' (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36'}]
        self.assertEqual(datas, checks)  
        
        
       
#     def test_get_df_case1(self):
#         db = 'test_db.db'
#         table = 'AUTORUN_RECORD'
#         df = get_df(db=db,table=table)
#         self.assertIsInstance(df, pd.DataFrame)

        
if __name__ == '__main__':
    unittest.main()