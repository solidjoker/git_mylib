
# coding: utf-8

# # Aiohttp_Config

# In[1]:


"""
support tools for aiohttpframe, including chrome_path, cookies_jsonfile, defaultEncoding, headers 
    - tool_name: Aiohttp_Config
    - version: 0.0.2
    - update date: 2019-05-15
    - import: from mytools_aiohttpframe import AiohttpFrame_Config
    - need fill the chrome_path
"""
import os


# In[2]:


if os.path.exists('C:'):
    # windows
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe'
else:
    # linux
    chrome_path = '/usr/bin/chromedriver'
    
cookies_jsonfile = 'cookie.json'
defaultEncoding = 'utf-8'
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'            ' (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36'}

