from datetime import datetime
class BaseView(object):
    def __init__(self, request):
        self.req = request
        self.ses = self.req.session
        self.params = self.req.params
        
        self.tahun = 'tahun' in self.ses and self.ses['tahun'] or datetime.now().strftime('%Y')
        self.tahun = 'tahun' in self.params and self.params['tahun'] or self.tahun
                    
        self.posted = 'posted' in self.ses and self.ses['posted'] or 0
        if 'posted' in self.params and self.params['posted']:
             self.posted = self.params['posted']=='true' and 1 or 0
        
        self.awal   = 'awal' in self.ses and self.ses['awal'] or datetime.now().strftime('%d-%m-%Y')
        self.awal   = 'awal' in self.params and self.params['awal'] or self.awal
        
        self.akhir  = 'akhir' in self.ses and self.ses['akhir'] or datetime.now().strftime('%d-%m-%Y')
        self.akhir  = 'akhir' in self.params and self.params['akhir'] or self.akhir
        
        self.dt_awal  = datetime.strptime(self.awal,'%d-%m-%Y')
        self.dt_akhir = datetime.strptime(self.akhir,'%d-%m-%Y')
        
        self.ses['tahun'] = self.tahun
        self.ses['posted'] = self.posted
        self.ses['awal'] = self.awal
        self.ses['akhir'] = self.akhir
        self.ses['dt_akhir'] = self.dt_akhir
        self.ses['dt_awal'] = self.dt_awal
            