# "http": "socks5://uopggzje-rotate:h4oypfcg1fq7@p.webshare.io:80/",        
# "https": "socks5://uopggzje-rotate:h4oypfcg1fq7@p.webshare.io:80/"
'''
from ensta import Guest
import re
import json
def extract_emails(text):
    # Regex pattern for extracting email addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)

guest = Guest()
profile = guest.profile("physicswallah")
emails = extract_emails(profile.biography)
print(emails)
print(profile.is_business_account)
print(profile.is_professional_account)
print(profile.is_private)'''

# type 1 = personal account [ bussiness=F, professional=F]
# type 2 = bussiness account [ bussiness=T, professional=T]
# type 3 = professional account [ bussiness=F, professional=T]

from aiograpi import Client
import asyncio
cl = Client()
async def main():
    await cl.login("thecreators782", "TheCreators12345")
    
    user_id = (await cl.user_info_by_username('empretiendaok')).model_dump()
    print(type(user_id))
    print(user_id.keys())

asyncio.run(main())