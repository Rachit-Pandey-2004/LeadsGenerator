# from ensta import Mobile

# mobile = Mobile("thecreators782", "TheCreators12345")

# profile = mobile.profile("leomessi")

# print(profile.full_name)
# print(profile.biography)
# print(profile.profile_pic_url)
# import aiohttp


username = "thecreators782"
password = "TheCreators12345"
import os
import asyncio
import pickle
import aiohttp
from aiograpi import Client  # adjust this import if your aiograpi version differs

SESSION_DIR = "sessions"
status = os.makedirs(SESSION_DIR, exist_ok=True)
print(status)