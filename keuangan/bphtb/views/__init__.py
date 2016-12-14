from datetime import datetime
#import re
from ...bphtb import BaseView
BPHTB_SELF = ('1')

class BphtbView(BaseView):
    def __init__(self, request):
            super(BphtbView, self).__init__(request)
