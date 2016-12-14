#from sqlalchemy.sql.expression import text 
#from pyramid.view import view_config
from hashlib import md5
from datetime import datetime
from ..models import (
    DBSession, 
    User,
    )

import hmac
import hashlib
import base64
#import json
#import requests
from ..tools import (
    get_settings,
    )
    
LIMIT = 1000
CODE_OK = 0
CODE_NOT_FOUND = -1
CODE_DATA_INVALID = -2
CODE_INVALID_LOGIN = -10
CODE_NETWORK_ERROR = -11

########        
# Auth #
########
def auth(username, signature, fkey):
    user = User.get_by_name(username)
    if not user:
        return
    
    value = "%s&%s" % (username,fkey); 
    
    key = str(user.user_password)
    lsignature = hmac.new(key, msg=value, digestmod=hashlib.sha256).digest()
    encodedSignature = base64.encodestring(lsignature).replace('\n', '')
    if encodedSignature==signature:
       return user

def auth_from_rpc(request):
    print request.environ
    user = auth(request.environ['HTTP_USERID'], request.environ['HTTP_SIGNATURE'], 
                request.environ['HTTP_KEY'])
    if user:
        return dict(code=CODE_OK, message='OK'), user
    return dict(code=CODE_INVALID_LOGIN, message='Gagal login'), user
    
def get_rpc_header(userid,password):
    utc_date = datetime.utcnow()
    tStamp = int((utc_date-datetime.strptime('1970-01-01 00:00:00','%Y-%m-%d %H:%M:%S')).total_seconds())
    value = "%s&%s" % (str(userid),tStamp)
    key = str(password) 
    signature = hmac.new(key, msg=value, digestmod=hashlib.sha256).digest() 
    encodedSignature = base64.encodestring(signature).replace('\n', '')
    headers = {'userid':userid,
               'signature':encodedSignature,
               'key':tStamp}
    return headers
