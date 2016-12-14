from datetime import datetime
#import re
from ...views.base_views import BaseView
BPHTB_SELF = ('1')

class PbbView(BaseView):
    def __init__(self, request):
            super(PbbView, self).__init__(request)
