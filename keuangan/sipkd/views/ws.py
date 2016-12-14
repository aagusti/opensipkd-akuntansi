from ...views.ws import (auth_from_rpc, LIMIT, CODE_OK, CODE_NOT_FOUND, CODE_DATA_INVALID, 
                   CODE_INVALID_LOGIN, CODE_NETWORK_ERROR)
from pyramid_rpc.jsonrpc import jsonrpc_method
from ..models import sipkdDBSession
from ..models.sipkd import SipkdSkp, SipkdSkpDet, SipkdUnit, SipkdRek4
from ..models.sipkd import SipkdTbp, SipkdTbpDet, SipkdBkuTbp
from datetime import datetime
@jsonrpc_method(method='post_ketetapan', endpoint='ws_keuangan')
def post_ketetapan(request, data):
    #Digunakan untuk menerima data ketetapan
    """ 
      Parameter Data
      unit_kd   : kode_unit
      kode      : no_spt/no_kohir,
      npwpd     : npwpd/nopd:
      tgl_tetap : tgl kohir or tgl_spt
      nama      : nama wp/op
      alamat    : alamat wp/op
      rekening_nm: Nama Rekening
      jth_tempo : Tanggal Jatuh Tempo
      pokok     : pokok
      denda     : denda
      bunga     : bunga
      rekening_kd: Kode Rekening 4.1.1.01.01. ditambahkan titik di ujung 
      source    : PBB BPHTB PDL 
      rekening_denda_kd    : Kode Rekening Denda 
      return 
      
      data array(kode:
                        error:0 sukses posting data
                              1 data sudah ada
                              2 Data Gagal Posting)
    """
    resp = {}
    resp['code'] = CODE_OK
    #resp,user = auth_from_rpc(request)
    if resp['code'] != CODE_OK:
        return resp
    
    resp['message'] = 'DATA PROSESSED'
    ret_data =[]
    for row in data:
        try:
        #if 1=1:
            #CHECK DULU DI SIPKD
            keykode = "%s-%s" %(row["source"],get_kode(row["kode"]))
            rows = sipkdDBSession.query(SipkdSkp).\
                      filter(SipkdSkp.unitkey == SipkdUnit.get_key_by_kode(row["unit_kd"]),
                             SipkdSkp.noskp == keykode,
                             ).first()
            if rows:
                ret_data.append({"kode": row["kode"],
                                 "error":1,
                                 "message":"Data Sudah Ada",
                                 }) # data sudah ada dalam keuangan
                resp['code'] = CODE_DATA_INVALID
                resp['message'] = 'DATA SUDAH ADA'
                continue
                
            row_skp = SipkdSkp()
            row_skp.unitkey  = SipkdUnit.get_key_by_kode(row["unit_kd"])
            row_skp.noskp    = keykode
            row_skp.kdstatus = '70'
            row_skp.keybend  = '1797_'
            row_skp.idxkode  = '1' #pendapatan
            row_skp.kenaikan = 0
            row_skp.npwpd    = row["npwpd"][-10:]
            row_skp.tglskp   = datetime.strptime(row["tgl_tetap"], "%Y-%m-%d")
            row_skp.penyetor = row["nama"]
            row_skp.alamat   = row["alamat"]
            row_skp.uraiskp  = row["rekening_nm"]
            row_skp.tgltempo = datetime.strptime(row["jth_tempo"], "%Y-%m-%d")
            #row_skp.tglvalid = datetime.now() diset setelah item di post
            row_skp.bunga    = row["denda"]+row["bunga"]
            sipkdDBSession.add(row_skp)
            sipkdDBSession.flush()

            if row["pokok"]>0:
                row_skpdet = SipkdSkpDet()
                row_skpdet.unitkey = row_skp.unitkey
                row_skpdet.noskp   = row_skp.noskp
                row_skpdet.nilai   = row["pokok"]
                row_skpdet.mtgkey  = SipkdRek4.get_key_by_kode(row["rekening_kd"])
                row_skpdet.nojetra = '11' 
                sipkdDBSession.add(row_skpdet)
                sipkdDBSession.flush()
            if row["denda"]+row["bunga"]>0:
                row_skpdet = SipkdSkpDet()
                row_skpdet.unitkey = row_skp.unitkey
                row_skpdet.noskp   = row_skp.noskp
                row_skpdet.nilai   = row["denda"]+row["bunga"]
                row_skpdet.mtgkey  = SipkdRek4.get_key_by_kode(row["rekening_denda_kd"])
                row_skpdet.nojetra = '11'
                sipkdDBSession.add(row_skpdet)
                sipkdDBSession.flush()
                

            row_skp.tglvalid = row_skp.tglskp
            sipkdDBSession.add(row_skp)
            sipkdDBSession.flush()
            ret_data.append({"kode": row["kode"],
                             "error":0,
                             "message":'Sukses'}) # data sukses di posting
        except Exception, e:
            ret_data.append({"kode": row["kode"],
                             "error":2,
                             "message":str(e)}) # data tidak berhasil diposting
            resp['code'] = CODE_DATA_INVALID
            resp['message'] = 'INVALID DATA'
        
    resp['params'] = dict(data=ret_data)
    return resp
    
@jsonrpc_method(method='unpost_ketetapan', endpoint='ws_keuangan')
def unpost_ketetapan(request, data):
    #Digunakan untuk unposting ketetapan pajak/retribusi
    """ 
      Parameter Data
      unit_kd   : kode_unit
      kode      : no_spt/no_kohir,
      source    : no_spt/no_kohir,
    
    return data array(kode:
                      error:0 sukses unposting
                            1 tidak ditemukan)
    """
    
    resp = {}
    resp['code'] = CODE_OK
    #resp,user = auth_from_rpc(request)
    if resp['code'] != CODE_OK:
        return resp
    ret_data=[]
    resp['message'] = 'DATA PROSESSED'
    for row in data:
        try:
        #if 1==1:
            kodekey = "%s-%s" %(row["source"],get_kode(row["kode"]))
            query = sipkdDBSession.query(SipkdSkp).\
                      filter(SipkdSkp.unitkey == SipkdUnit.get_key_by_kode(row["unit_kd"]),
                             SipkdSkp.noskp == kodekey,
                             )
            rows = query.first()
            if not rows:
                ret_data.append({"kode": row["kode"],
                                 "error":1,
                                 "message":"Data Tidak Ditemukan"}) # data tidak ada dalam keuangan
                resp['code'] = CODE_DATA_INVALID
                resp['message'] = 'DATA INVALID'
                continue
                
            row_skpdet = sipkdDBSession.query(SipkdSkpDet).\
                                     filter_by(unitkey = rows.unitkey,
                                               noskp   = rows.noskp).delete()
            sipkdDBSession.flush()
            row_skp = query.delete()
            ret_data.append({"kode": row["kode"],
                             "error":0,
                             "message":"Sukses"})
        except Exception, e:
            ret_data.append({"kode": row["kode"],
                             "error":2,
                             "message":str(e)}) # data gagal di unpost
            resp['code'] = CODE_DATA_INVALID
            resp['message'] = 'DATA INVALID'
            
    resp['params'] = dict(data=ret_data)
    return resp    

def get_kode(kode):
    xs = kode.split('/')
    import re
    xd = ''
    for x in xs:
        if xd:
            xd +='/'
        xd += x[2:]
    return re.sub('-','',xd)


"""
"""
@jsonrpc_method(method='post_realisasi', endpoint='ws_keuangan')
def post_realisasi(request, data):
    #Digunakan untuk memposting data penerimaan
    #paramter 
    """  unit_kd   : kode_unit
      kode      : no_spt/no_kohir,
      tgl_trans : tgl pembayaran
      nama      : nama wp/op
      alamat    : alamat wp/op
      rekening_nm: Nama Rekening
      pokok     : pokok
      denda     : denda
      bunga     : bunga
      rekening_kd: Kode Rekening 4.1.1.01.01. ditambahkan titik di ujung 
      source    : PBB BPHTB PDL 
      rekening_denda_kd    : Kode Rekening Denda 
    """
    resp = {}
    resp['code'] = CODE_OK
    #resp,user = auth_from_rpc(request)
    if resp['code'] != CODE_OK:
        return resp
    ret_data=[]
    resp['message'] = 'DATA PROSESSED'
    for row in data:
        try:
        #if 1==1:
            tanggal = datetime.strptime(row["tgl_trans"], "%Y-%m-%d")

            unitkey = SipkdUnit.get_key_by_kode(row["unit_kd"])
            kodekey = "%s-%s-%s" % (row["source"],get_kode(row["kode"]),tanggal.strftime('%d%m'))
            
            rows = sipkdDBSession.query(SipkdTbp).\
                    filter(SipkdTbp.unitkey == SipkdUnit.get_key_by_kode(row["unit_kd"]),
                           SipkdTbp.notbp == kodekey,
                          ).first()
            if rows:
                ret_data.append({"kode": row["kode"],
                                 "error":1,
                                 "message":"Data Sudah Ada"}) # data gagal di post
                resp['code'] = CODE_DATA_INVALID
                resp['message'] = 'DATA SUDAH ADA'
                continue
                
            if kodekey.find("/")>0:
                statuskd = '64' #Penerimaan (Rek.Bend)-Penetapan
            else:
                statuskd = '63' #Penerimaan (Rek.Bend)-Tanpa Penetapan
             
            row_tbp = SipkdTbp()
            row_tbp.unitkey  = unitkey
            row_tbp.notbp    = kodekey 
            row_tbp.keybend1 = '1797_'

            row_tbp.kdstatus = statuskd
            row_tbp.keybend2 = '1797_'
            row_tbp.idxkode  = '1' #pendapatan
            row_tbp.tgltbp   = tanggal
            row_tbp.penyetor = row["nama"]
            row_tbp.alamat   = row["alamat"]
            row_tbp.uraitbp  = row["rekening_nm"]
            row_tbp.tglvalid = tanggal
            sipkdDBSession.add(row_tbp)
            sipkdDBSession.flush()
            
            if row["pokok"]>0:  
                row_tbpdet = SipkdTbpDet()
                row_tbpdet.unitkey = unitkey
                row_tbpdet.notbp   = kodekey
                row_tbpdet.nilai   = row["pokok"]
                row_tbpdet.mtgkey  = SipkdRek4.get_key_by_kode(row["rekening_kd"])
                row_tbpdet.nojetra = '11' #Penerimaan STS/TBP
                sipkdDBSession.add(row_tbpdet)
                sipkdDBSession.flush()
                
            if row["denda"]+row["bunga"]>0:
                row_tbpdet = SipkdTbpDet()
                row_tbpdet.unitkey = unitkey
                row_tbpdet.notbp   = kodekey
                row_tbpdet.nilai   = row["denda"]+row["bunga"]
                row_tbpdet.mtgkey  = SipkdRek4.get_key_by_kode(row["rekening_denda_kd"])
                row_tbpdet.nojetra = '11' #Penerimaan STS/TBP
                sipkdDBSession.add(row_tbpdet)
                sipkdDBSession.flush()
            
            row_bku = SipkdBkuTbp()
            row_bku.unitkey     = unitkey
            row_bku.nobkuskpd   = kodekey
            row_bku.notbp       = kodekey
            row_bku.idxttd      = '1797_'
            row_bku.tglbkuskpd  = tanggal
            row_bku.uraian      = row["nama"]
            row_bku.tglvalid    = tanggal
            row_bku.keybend     = '1797_'
            sipkdDBSession.add(row_bku)
            sipkdDBSession.flush()
            row_bku.tglvalid    = tanggal
            sipkdDBSession.add(row_bku)
            sipkdDBSession.flush()
            ret_data.append({"kode": row["kode"],
                             "error":0,
                             "message":"Sukses"}) # data gagal di unpost
        except Exception, e:
            ret_data.append({"kode": row["kode"],
                             "error":2,
                             "message":str(e)}) # data gagal di unpost
            resp['code'] = CODE_DATA_INVALID
            resp['message'] = 'Data Invalid'
    resp['params'] = dict(data=ret_data)
    return resp
    
@jsonrpc_method(method='unpost_realisasi', endpoint='ws_keuangan')
def unpost_realisasi(request, data):
    #Digunakan untuk melakukan unposting pendapatan
    """ 
      Parameter Data
      unit_kd   : kode_unit
      kode      : no_spt/no_kohir,
      source    : no_spt/no_kohir,
    
    return data array(kode:
                      error:0 sukses unposting
                            1 tidak ditemukan)
    """
    
    resp = {}
    resp['code'] = CODE_OK
    #resp,user = auth_from_rpc(request)
    if resp['code'] != CODE_OK:
        return resp
    ret_data=[]
    resp['message'] = 'DATA PROSESSED'
    for row in data:
        try:
        #if 1==1:
            tanggal = datetime.strptime(row["tgl_trans"], "%Y-%m-%d")

            unitkey = SipkdUnit.get_key_by_kode(row["unit_kd"])
            kodekey = "%s-%s-%s" % (row["source"],get_kode(row["kode"]),tanggal.strftime('%d%m'))
            row_tbp = sipkdDBSession.query(SipkdTbp).\
                    filter_by(unitkey = unitkey,
                            notbp   = kodekey)
            if not row_tbp.first():
                 kodekey = "%s-%s" % (row["source"],row["kode"])

                                                                                                         #kodekey = "%s-%s" % (row["source"],row["kode"])
            row_bku = sipkdDBSession.query(SipkdBkuTbp).\
                                     filter_by(unitkey = unitkey,
                                               notbp   = kodekey,
                                               ).delete()
                                               
            row_tbpdet = sipkdDBSession.query(SipkdTbpDet).\
                                     filter_by(unitkey = unitkey,
                                               notbp   = kodekey).delete()
                                               
            # row_skptbp = sipkdDBSession.query(SipkdSkpTbp).\
                                     # filter_by(unitkey = unitkey,
                                               # notbp   = notbp).delete()
            row_tbp = sipkdDBSession.query(SipkdTbp).\
                                     filter_by(unitkey = unitkey,
                                               notbp   = kodekey).delete()
            sipkdDBSession.flush()
            #sipkdDBSession.commit()
            ret_data.append({"kode": row["kode"],
                             "error":0,
                             "message":'Sukses'}) # data sukses di posting
        except Exception,e:
            #sipkdDBSession.rollback()
            ret_data.append({"kode": row["kode"],
                             "error":2,
                             "message":str(e)}) # data gagal di unpost
            resp['code'] = CODE_DATA_INVALID
            resp['message'] = "DATA INVALID"
            
    resp['params'] = dict(data=ret_data)
    return resp    
    
