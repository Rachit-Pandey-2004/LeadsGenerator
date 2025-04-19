'''
This is specifically design for forget and fire activity
'''
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import nUser

async def search_entries(raw_data:dict,session_id):
    try:
        for section in raw_data['media_grid']['sections']:
            for medias in section['layout_content']['medias']:
                data = medias['media']['owner']
                username= data['username']
                fullname= data['full_name']
                isprivate= data['is_private']
                acc_type = data['account_type']
                # type 1 = personal account [ bussiness=F, professional=F]
                # type 2 = bussiness account [ bussiness=T, professional=T]
                # type 3 = professional account [ bussiness=F, professional=T]
                if acc_type == 1:
                    is_professional_account = False
                    is_business_account = False
                elif acc_type == 2:
                    is_professional_account = True
                    is_business_account = True
                elif acc_type == 3:
                    is_professional_account = True
                    is_business_account = False
                profile_pic_url=data['hd_profile_pic_url_info']['url']
                
                user = nUser(username=username, search_id=session_id,fullname=fullname, profile_pic_url=profile_pic_url, account_type=acc_type ,is_business_account=is_business_account,is_professional_account=is_professional_account, isprivate=isprivate)
                await user.starts()
                await user.save()
    except Exception as e:
        print(e)