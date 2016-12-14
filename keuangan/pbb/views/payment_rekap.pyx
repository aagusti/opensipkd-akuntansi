import os
import uuid
#from ...tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func, between
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )

import colander
from deform import (Form, widget, ValidationFailure, )
from ...models import DBSession
from ...models.keuangan import SipkdDBSession
#from ...models.apbd_anggaran import Kegiatan, KegiatanSub, KegiatanItem, Pegawai, Pejabat, Jabatan

from ...models.ar import ARPaymentPbbRekap
from ...models.keuangan import SipkdUnit, SipkdRek4, SipkdTbp, SipkdTbpDet, SipkdBkuTbp # SipkdSkpTbp, SipkdSkp #, SipkdSkpDet, 
from ...tools import _DTstrftime, _DTnumber_format    
from datatables import ColumnDT, DataTables

SESS_ADD_FAILED  = 'Tambah Payment gagal'
SESS_EDIT_FAILED = 'Edit Payment gagal'

def deferred_jenis_id(node, kw):
    values = kw.get('jenis_id', [])
    return widget.SelectWidget(values=values)
    
JENIS_ID = (
    (1, 'Tagihan'),
    (2, 'Piutang'),
    (3, 'Ketetapan'))

def deferred_sumber_id(node, kw):
    values = kw.get('sumber_id', [])
    return widget.SelectWidget(values=values)
    
SUMBER_ID = (
    (4, 'Manual'),
    (1, 'PBB'),)
    
@view_config(route_name="ar-payment-pbb-rekap", renderer="templates/ar-payment-pbb-rekap/list.pt",
             permission="ar-payment-pbb-rekap")
def view_list(request):
    ses = request.session
    req = request
    if 'tahun' not in ses:
        ses['tahun'] = datetime.now().year
    if 'posted' not in ses:
        ses['posted'] = 0
    params   = dict(req.params)
    if 'btn-filter' in request.POST:
        controls = dict(request.POST.items())
        ses['tahun']=controls['tahun_fltr']
        ses['tanggal']=controls['tanggal_fltr']
        ses['tanggal_to']=controls['tanggal_to_fltr']
        if 'posted_fltr' in controls and controls['posted_fltr']:
            ses['posted'] = 1
        else:
            ses['posted'] = 0
    url_dict = req.matchdict
    return dict(project='EIS')
    
##########                    
# Action #
##########    
@view_config(route_name='ar-payment-pbb-rekap-act', renderer='json',
             permission='read')
def view_act(request):
    ses = request.session
    req = request
    params   = req.params
    url_dict = req.matchdict

    if url_dict['act']=='grid':
        pk_id = 'id' in params and params['id'] and int(params['id']) or 0
        if url_dict['act']=='grid':
            # defining columns
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('unit_kd'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('uraian'))
            columns.append(ColumnDT('rekening_kd'))
            columns.append(ColumnDT('rekening_nm'))
            columns.append(ColumnDT('tgl_trans', filter=_DTstrftime))
            columns.append(ColumnDT('pokok', filter=_DTnumber_format))
            columns.append(ColumnDT('denda', filter=_DTnumber_format))
            columns.append(ColumnDT('bunga', filter=_DTnumber_format))
            columns.append(ColumnDT('posted'))

            query = DBSession.query(ARPaymentPbbRekap.id,
                      ARPaymentPbbRekap.unit_kd,
                      ARPaymentPbbRekap.kode,
                      ARPaymentPbbRekap.uraian,
                      ARPaymentPbbRekap.rekening_kd,
                      ARPaymentPbbRekap.rekening_nm,
                      ARPaymentPbbRekap.pokok,
                      ARPaymentPbbRekap.denda,
                      ARPaymentPbbRekap.bunga,
                      ARPaymentPbbRekap.posted,
                      ARPaymentPbbRekap.tgl_trans,
                      ARPaymentPbbRekap.tgl_validasi,
                      ).filter(ARPaymentPbbRekap.tahun==ses['tahun'],
                               between(ARPaymentPbbRekap.tgl_trans, ses['tanggal'], ses['tanggal_to']),
                               ARPaymentPbbRekap.posted==ses['posted']
                      ) 
                    #).order_by(ARPaymentPbbRekap.kode.asc()
                    #)
            rowTable = DataTables(req, ARPaymentPbbRekap, query, columns)
            return rowTable.output_result()
                
  
#######    
# Add #
#######
def form_validator(form, value):
    def err_kegiatan():
        raise colander.Invalid(form,
            'Kegiatan dengan no urut tersebut sudah ada')      
                
class AddSchema(colander.Schema):
    unit_kd      = colander.SchemaNode(
                            colander.String(),
                            title = "SKPD")
    unit_nm      = colander.SchemaNode(
                            colander.String(),
                            missing = colander.drop)
    kode         = colander.SchemaNode(
                            colander.String(),
                            title = "No. SSPD")
    uraian         = colander.SchemaNode(
                            colander.String())
    alamat       = colander.SchemaNode(
                            colander.String())
    uraian       = colander.SchemaNode(
                            colander.String(),
                            missing = colander.drop)
    tgl_trans    = colander.SchemaNode(
                            colander.Date())
    rekening_kd  = colander.SchemaNode(
                            colander.String(),
                            title = "Rekening")
    rekening_nm  = colander.SchemaNode(
                            colander.String(),
                            missing = colander.drop)
    pokok        = colander.SchemaNode(
                            colander.String())
    denda        = colander.SchemaNode(
                            colander.String())
    bunga        = colander.SchemaNode(
                            colander.String())
    sumber_id    = colander.SchemaNode(
                            colander.String(),
                            widget=widget.SelectWidget(values=SUMBER_ID),
                            title = "Sumber")
    ref_kode     = colander.SchemaNode(
                            colander.String(),
                            title = "No Bayar")
    ref_nama     = colander.SchemaNode(
                            colander.String(),
                            title = "Uraian")
    # kecamatan_kd = colander.SchemaNode(
                            # colander.String(),
                            # title = "Kecamatan",
                            # missing = colander.drop)
    # kecamatan_nm = colander.SchemaNode(
                            # colander.String(),
                            # missing = colander.drop)
    # kelurahan_kd = colander.SchemaNode(
                            # colander.String(),
                            # title = "Kelurahan",
                            # missing = colander.drop)
    # kelurahan_nm = colander.SchemaNode(
                            # colander.String(),
                            # missing = colander.drop)
    # is_kota      = colander.SchemaNode(
                            # colander.Boolean(),
                            # title = "Kota")
    # npwpd        = colander.SchemaNode(
                            # colander.String(),
                            # missing = colander.drop)
    
    # jth_tempo    = colander.SchemaNode(
                            # colander.Date(),
                            # missing = colander.drop,
                            # oid = "jth_tempo")

class EditSchema(AddSchema):
    id             = colander.SchemaNode(
                          colander.Integer(),
                          oid="id")

def get_form(request, class_form):
    schema = class_form(validator=form_validator)
    schema = schema.bind(jenis_id=JENIS_ID,sumber_id=SUMBER_ID)
    schema.request = request
    return Form(schema, buttons=('simpan','batal'))
    
def save(request, values, row=None):
    if not row:
        row = ARInvoice()
    row.from_dict(values)
    row.nilai = row.pokok+row.denda+row.bunga
    DBSession.add(row)
    DBSession.flush()
    return row
                                      
def save_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
    #values["nilai"]=values["nilai"].replace('.','')  
    if values["is_kota"]:
        values["is_kota"] = 1
    else:
        values["is_kota"] = 0
    row = save(request, values, row)
    request.session.flash('Tagihan sudah disimpan.')
    return row
        
def route_list(request):
    return HTTPFound(location=request.route_url('ar-payment-pbb-rekap'))
    
def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r
    
@view_config(route_name='ar-payment-pbb-rekap-add', renderer='templates/ar-payment-pbb-rekap/add.pt',
             permission='ar-payment-pbb-rekap-add')
def view_add(request):
    form = get_form(request, AddSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items() 
            controls_dicted = dict(controls)

            #Cek Kode Sama ato tidak
            if not controls_dicted['kode']=='':
                a = form.validate(controls)
                b = a['kode']
                c = "%s" % b
                cek  = DBSession.query(ARPaymentPbbRekap).filter(ARPaymentPbbRekap.kode==c).first()
                if cek :
                    request.session.flash('Kode ARInvoice sudah ada.', 'error')
                    return HTTPFound(location=request.route_url('ar-payment-add'))
            
            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                return dict(form=form)
            row = save_request(controls_dicted, request)
            return HTTPFound(location=request.route_url('ar-payment-edit',id=row.id))
        return route_list(request)
    elif SESS_ADD_FAILED in request.session:
        del request.session[SESS_ADD_FAILED]
    return dict(form=form)

########
# Edit #
########
def query_id(request):
    return DBSession.query(ARPaymentPbbRekap).filter(ARPaymentPbbRekap.id==request.matchdict['id'])
    
def id_not_found(request):    
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='ar-payment-pbb-rekap-edit', renderer='templates/ar-payment-pbb-rekap/add.pt',
             permission='ar-payment-pbb-rekap-edit')
def view_edit(request):
    row = query_id(request).first()

    if not row:
        return id_not_found(request)
    uid     = row.id
    kode    = row.kode
    if row.posted:
        request.session.flash('Data sudah diposting', 'error')
        return route_list(request)

    form = get_form(request, EditSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()

            #Cek Kode Sama ato tidak
            a = form.validate(controls)
            b = a['kode']
            c = "%s" % b
            cek = DBSession.query(ARPaymentPbbRekap).filter(ARPaymentPbbRekap.kode==c).first()
            if cek:
                kode1 = DBSession.query(ARPaymentPbbRekap).filter(ARPaymentPbbRekap.id==uid).first()
                d     = kode1.kode
                if d!=c:
                    request.session.flash('Kode ARPaymentPbbRekap sudah ada', 'error')
                    return HTTPFound(location=request.route_url('ar-payment-edit',id=row.id))
            
            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                return dict(form=form)
            save_request(dict(controls), request, row)
        return route_list(request)
    elif SESS_EDIT_FAILED in request.session:
        del request.session[SESS_EDIT_FAILED]
        return dict(form=form)
    values = row.to_dict() 
    form.set_appstruct(values) 
    return dict(form=form)

##########
# Delete #
##########    
@view_config(route_name='ar-payment-pbb-rekap-delete', renderer='templates/ar-payment-pbb-rekap/delete.pt',
             permission='ar-payment-pbb-rekap-delete')
def view_delete(request):
    q = query_id(request)
    row = q.first()
    
    if not row:
        return id_not_found(request)
    if row.posted:
        request.session.flash('Data sudah diposting', 'error')
        return route_list(request)
        
    form = Form(colander.Schema(), buttons=('hapus','cancel'))
    values= {}
    if request.POST:
        if 'hapus' in request.POST:
            msg = '%s dengan kode %s telah berhasil.' % (request.title, row.kode)
            DBSession.query(ARPaymentPbbRekap).filter(ARPaymentPbbRekap.id==request.matchdict['id']).delete()
            DBSession.flush()
            request.session.flash(msg)
        return route_list(request)
    return dict(row=row,form=form.render())
    
###########
# Posting #
###########   
def query_post_id(id):
    return DBSession.query(ARPaymentPbbRekap).filter(ARPaymentPbbRekap.id==id)

@view_config(route_name='ar-payment-pbb-rekap-post', renderer='json',
             permission='ar-payment-pbb-rekap-post')
def view_posting(request):
    if request.POST:
        controls = dict(request.POST.items())
        n_id_not_found = 0
        n_row_zero     = 0
        n_posted       = 0
        n_id           = 0
        msg = ""
        for id in controls['id'].split(","):
            row    = query_post_id(id).first()
            if not row:
                n_id_not_found = n_id_not_found + 1
                continue

            if not row.nilai:
                n_row_zero = n_row_zero + 1
                continue

            if request.session['posted']==0 and row.posted:
                n_posted = n_posted + 1
                continue

            if request.session['posted']==1 and not row.posted:
                n_posted = n_posted + 1
                continue

            n_id = n_id + 1

            id_inv = row.id

            if request.session['posted']==0:
                unitkey = SipkdUnit.get_key_by_kode(row.unit_kd)
                kodekey = row.kode
                #CEK DULU DATA SKP
                #row_skp = SipkdDBSession.query(SipkdSkp).\
                #                         filter_by(UNITKEY = unitkey,
                #                                   NOSKP   = row.ref_kode) #cek by no bayar
                #if row_skp:
                #    statuskd = '64' #Penerimaan (Rek.Bend)-Penetapan
                #else:
                #    statuskd = '63' #Penerimaan (Rek.Bend)-Tanpa Penetapan
                
                #if not row.ref_kode or row.ref_kode=='0' or row.ref_kode=='00':
                #    statuskd = '63' #Penerimaan (Rek.Bend)-Tanpa Penetapan
                #else:
                statuskd = '64' #Penerimaan (Rek.Bend)-Penetapan
                row_tbp = SipkdTbp()
                row_tbp.unitkey  = unitkey
                row_tbp.notbp    = kodekey 
                row_tbp.keybend1 = '1797_'

                row_tbp.kdstatus = statuskd
                row_tbp.keybend2 = '1797_'
                row_tbp.idxkode  = '1' #pendapatan
                row_tbp.tgltbp   = row.tgl_trans
                row_tbp.penyetor = 'Bank'#row.uraian
                #row_tbp.alamat   = row.alamat
                row_tbp.uraitbp  = row.uraian #row.rekening_nm
                row_tbp.tglvalid = row.tgl_trans
                SipkdDBSession.add(row_tbp)
                SipkdDBSession.flush()
                
                if row.pokok+row.denda+row.bunga>0:  
                    row_tbpdet = SipkdTbpDet()
                    row_tbpdet.unitkey = unitkey
                    row_tbpdet.notbp   = kodekey
                    row_tbpdet.nilai   = row.pokok+row.denda+row.bunga
                    row_tbpdet.mtgkey  = SipkdRek4.get_key_by_kode(row.rekening_kd)
                    row_tbpdet.nojetra = '11' #Penerimaan STS/TBP
                    SipkdDBSession.add(row_tbpdet)
                    SipkdDBSession.flush()
                
                #Insert into BKU   
                row_bku = SipkdBkuTbp()
                row_bku.unitkey     = unitkey
                row_bku.nobkuskpd   = kodekey
                row_bku.notbp       = kodekey
                row_bku.idxttd      = '1797_'
                row_bku.tglbkuskpd  = row.tgl_trans
                row_bku.uraian      = row.uraian
                row_bku.tglvalid    = row.tgl_trans
                row_bku.keybend     = '1797_'
                SipkdDBSession.add(row_bku)
                SipkdDBSession.flush()
                row_bku.tglvalid    = row.tgl_trans
                SipkdDBSession.add(row_bku)
                SipkdDBSession.flush()
    
                """"if (row.denda+row.bunga)>0:  
                    row_tbpdet = SipkdTbpDet()
                    row_tbpdet.UNITKEY = unitkey
                    row_tbpdet.NOTBP   = kodekey
                    row_tbpdet.NILAI   = row.denda+row.bunga
                    row_tbpdet.MTGKEY  = SipkdRek4.get_key_by_kode(row.rekening_kd)
                    row_tbpdet.NOJETRA = '11' #Penerimaan STS/TBP
                    SipkdDBSession.add(row_tbpdet)
                    SipkdDBSession.flush()
                
                
                if row_skp:
                    row_skptbp = SipkdSkpTbp()
                    row_skptbp.UNITKEY = unitkey
                    row_skptbp.NOTBP   = row_tbp.NOTBP
                    row_skptbp.NOSKP   = row.ref_kode
                    SipkdDBSession.add(row_skptbp)
                    SipkdDBSession.flush()
                """
                
                row.posted = 1
                DBSession.add(row)
                DBSession.flush()
            else:
                unitkey = SipkdUnit.get_key_by_kode(row.unit_kd)
                notbp = row.kode
                row_bku = SipkdDBSession.query(SipkdBkuTbp).\
                                         filter_by(unitkey = unitkey,
                                                   notbp   = notbp,
                                                   ).delete()
                                                   
                row_tbpdet = SipkdDBSession.query(SipkdTbpDet).\
                                         filter_by(unitkey = unitkey,
                                                   notbp   = notbp).delete()
                # row_skptbp = SipkdDBSession.query(SipkdSkpTbp).\
                                         # filter_by(unitkey = unitkey,
                                                   # notbp   = notbp).delete()
                row_tbp = SipkdDBSession.query(SipkdTbp).\
                                         filter_by(unitkey = unitkey,
                                                   notbp   = notbp).delete()
                SipkdDBSession.flush()
                row.posted = 0
                DBSession.add(row)
                DBSession.flush()

        if n_id_not_found > 0:
            msg = '%s Data Tidan Ditemukan %s \n' % (msg,n_id_not_found)
        if n_row_zero > 0:
            msg = '%s Data Dengan Nilai 0 sebanyak %s \n' % (msg,n_row_zero)
        if n_posted>0:
            msg = '%s Data Tidak Di Proses %s \n' % (msg,n_posted)
        msg = '%s Data Di Proses %s ' % (msg,n_id)
        
        return dict(success = True,
                    msg     = msg)
                    
    return dict(success = False,
                msg     = 'Terjadi kesalahan proses')

                

    
#############
# UnPosting #
#############   
@view_config(route_name='ar-payment-pbb-rekap-unpost', renderer='json',
             permission='ar-payment-pbb-rekap-unpost')
def view_unposting(request):
    row    = query_id(request).first()
    if not row:
        return id_not_found(request)
    if not row.nilai:
        request.session.flash('Data tidak dapat diunposting, karena bernilai 0.', 'error')
        return route_list(request)
    if not row.posted:
        request.session.flash('Data Belum di posting', 'error')
        return route_list(request)
    id_inv = row.id
    unitkey = SipkdUnit.get_key_by_kode(row.unit_kd)
    notbp = row.kode
            
    row_tbpdet = SipkdDBSession.query(SipkdTbpDet).\
                             filter_by(UNITKEY = unitkey,
                                       NOTBP   = notbp).delete()
                                       
    row_skptbp = SipkdDBSession.query(SipkdSkpTbp).\
                             filter_by(UNITKEY = unitkey,
                                       NOTBP   = notbp).delete()
    
    row_tbp = SipkdDBSession.query(SipkdTbp).\
                             filter_by(UNITKEY = unitkey,
                                       NOTBP   = notbp).delete()
    SipkdDBSession.flush()

    request.session.flash('Data Berhasil diunposting')
    row.posted = 0
    DBSession.add(row)
    DBSession.flush()
    return route_list(request)
##########
# CSV #
##########

@view_config(route_name='ar-payment-pbb-rekap-csv', renderer='csv',
             permission='ar-payment-pbb-rekap-csv')
def view_csv(request):
    ses = request.session
    req = request
    params   = req.params
    url_dict = req.matchdict
    q = DBSession.query(ARPaymentPbbRekap.id,
        ARPaymentPbbRekap.unit_kd,
        ARPaymentPbbRekap.kode,
        ARPaymentPbbRekap.uraian,
        ARPaymentPbbRekap.rekening_kd,
        ARPaymentPbbRekap.rekening_nm,
        ARPaymentPbbRekap.pokok,
        ARPaymentPbbRekap.denda,
        ARPaymentPbbRekap.bunga,
        ARPaymentPbbRekap.posted,
        ARPaymentPbbRekap.tgl_trans,
        ARPaymentPbbRekap.tgl_validasi,
        ).filter(ARPaymentPbbRekap.tahun==ses['tahun'],
                 between(ARPaymentPbbRekap.tgl_trans, ses['tanggal'], ses['tanggal_to']),
                 ARPaymentPbbRekap.posted==ses['posted']
        ) 
              
    r = q.first()
    header = r.keys()
    query = q.all()
    rows = []
    for item in query:
        rows.append(list(item))

    # override attributes of response
    filename = 'ar-payment.csv'
    request.response.content_disposition = 'attachment;filename=' + filename

    return {
      'header': header,
      'rows': rows,
    }
      