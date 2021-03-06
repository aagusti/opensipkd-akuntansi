import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy import not_, func, between
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from ..models import pbbDBSession
from ...tool_apps import SIKLUS
from ..models.tap import SpptRekap, SpptAkrual
from ...tools import _DTstrftime, _DTnumber_format, FixLength
#from ...views.base_views import base_view
from ..views import PbbView
from ...views.common import ColumnDT, DataTables
import re

SESS_ADD_FAILED  = 'Tambah Ketetapan gagal'
SESS_EDIT_FAILED = 'Edit Ketetapan gagal'

def deferred_jenis_id(node, kw):
    values = kw.get('jenis_id', [])
    return widget.SelectWidget(values=values)

def deferred_sumber_id(node, kw):
    values = kw.get('sumber_id', [])
    return widget.SelectWidget(values=values)

class KetetapanRekapView(PbbView):
    def _init__(self,request):
        super(KetetapanRekapView, self).__init__(request)
        
    @view_config(route_name="pbb-ketetapan-rekap", renderer="templates/ketetapan_rekap/list.pt",
                 permission="pbb-ketetapan-rekap")
    def view_list(request):
        return dict(project='Integrasi')

    ##########
    # Action #
    ##########
    @view_config(route_name='pbb-ketetapan-rekap-act', renderer='json',
                 permission='pbb-ketetapan-rekap-act')
    def view_act(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict

        if url_dict['id']=='grid':
            #pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if url_dict['id']=='grid':
                # defining columns
                columns = []
                columns.append(ColumnDT(SpptRekap.id, mData='id'))
                columns.append(ColumnDT(func.to_char(SpptRekap.tanggal,'DD-MM-YYYY'), mData='tanggal'))
                columns.append(ColumnDT(SpptRekap.kode, mData='kode'))
                columns.append(ColumnDT(SpptRekap.uraian, mData='uraian'))
                columns.append(ColumnDT(SpptRekap.pokok, mData='pokok'))
                columns.append(ColumnDT(SpptRekap.posted, mData='posted'))

                query = pbbDBSession.query().select_from(SpptRekap).\
                                     filter(SpptRekap.tanggal.between(self.dt_awal, self.dt_akhir)).\
                                     filter(SpptRekap.posted==self.posted)
                rowTable = DataTables(req.GET, query, columns)
                return rowTable.output_result()
                
    ###########
    # Posting #
    ###########
    @view_config(route_name='pbb-ketetapan-rekap-post', renderer='json',
                 permission='pbb-ketetapan-rekap-post')
    def view_posting(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict
        n_id_not_found = n_row_zero = n_posted = n_id = 0
        now = datetime.now()
        n_id = n_id_not_found = n_posted = 0
                
        if req.POST:
            controls = dict(req.POST.items())
            awal = self.dt_awal
            akhir = self.dt_akhir
            #GENERATOR rekap ketetapan
            if url_dict['id']=='gen': 
                adate = func.to_char(SpptAkrual.create_date,'YYYY-MM-DD')
                query = pbbDBSession.query(
                            adate.label('tanggal'),
                            func.sum(SpptAkrual.pbb_yg_harus_dibayar_sppt).label('pokok')).\
                        filter(SpptAkrual.create_date.between(
                            self.dt_awal, self.dt_akhir+timedelta(days=1))).\
                        filter(SpptAkrual.posted==0).\
                        group_by(adate)
                
                r = query.first()
                if not r:
                    return dict(success = False,
                                msg     = 'Tidak ada data yang di proses')
                    
                headers = r.keys()
                for row in query.all():
                    row_dicted = dict(zip(row.keys(), row))
                    #bank.from_dict(row_dicted)
                    row_dicted['uraian'] = "Penetapan Tanggal {tanggal}".\
                                           format(tanggal = row.tanggal)
                    row_dicted['kode'] = "PBB-TAP-{tanggal}".\
                                         format(tanggal = row.tanggal)
                    row_dicted['posted'] = 0
                    tanggal = row_dicted['tanggal'] 
                    row_dicted['tanggal'] = datetime.strptime(tanggal,'%Y-%m-%d')
                    spptRekap = SpptRekap()
                    spptRekap.from_dict(row_dicted)
                    pbbDBSession.add(spptRekap)
                    pbbDBSession.flush()
                    
                pbbDBSession.query(SpptAkrual).\
                             filter(SpptAkrual.posted == 0,
                                    SpptAkrual.create_date.between(awal,akhir+timedelta(days=1))).\
                             update({SpptAkrual.posted: 2}, synchronize_session=False)
                return dict(success = True,
                            msg     = 'Proses Berhasil')
                                
            elif url_dict['id']=='del': #Hapus data rekap
                for id in controls['id'].split(","):
                    q = query_id(id)
                    row    = q.first()
                    if not row:
                        n_id_not_found = n_id_not_found + 1
                        continue

                    if row.posted:
                        n_posted = n_posted + 1
                        continue
                        
                    n_id = n_id + 1
                    row_dicted = row.to_dict()
                    
                    pbbDBSession.query(SpptAkrual).\
                                 filter(SpptAkrual.create_date.between(row.tanggal,row.tanggal+timedelta(days=1)),
                                        SpptAkrual.posted == 2,).\
                                 update({SpptAkrual.posted:0}, synchronize_session=False)
                    q.delete()
                    pbbDBSession.flush()
                    
                msg = {}        
                if n_id_not_found > 0:
                    msg['id_not_found'] = {'msg': 'Data Tidak Ditemukan %s ' % (n_id_not_found),
                                           'count': n_id_not_found}
                if n_row_zero > 0:
                    msg['row_zero'] = {'msg': 'Data Dengan Nilai 0 sebanyak  %s ' % (n_row_zero),
                                       'count': n_row_zero}
                if n_posted>0:
                    msg['not_posted'] = {'msg': 'Data Tidak Di Proses %s \n' % (n_posted),
                                          'count': n_posted}
                msg['proses'] = {'msg': 'Data Di Proses %s ' % (n_id),
                                 'count':n_id}
                
                return dict(success = True,
                            msg     = msg)
            #POSTING Data                
            elif url_dict['id']=='post': 
                controls = dict(req.POST.items())
                for id in controls['id'].split(","):
                    row    = query_id(id).first()
                    if not row:
                        n_id_not_found = n_id_not_found + 1
                        continue

                    if not row.pokok:
                        n_row_zero = n_row_zero + 1
                        continue

                    if url_dict['id']=='false' and row.posted:
                        n_posted = n_posted + 1
                        continue

                    if url_dict['id']=='true' and not row.posted:
                        n_posted = n_posted + 1
                        continue

                    n_id = n_id + 1

                    #id_inv = row.id
                    
                    if self.posted==1:
                        row.posted = 0 
                    else:
                        row.posted = 1
                        
                    pbbDBSession.add(row)
                    pbbDBSession.flush()
                    
                msg = {}        
                if n_id_not_found > 0:
                    msg['id_not_found'] = {'msg': 'Data Tidan Ditemukan %s ' % (n_id_not_found),
                                           'count': n_id_not_found}
                if n_row_zero > 0:
                    msg['row_zero'] = {'msg': 'Data Dengan Nilai 0 sebanyak  %s ' % (n_row_zero),
                                       'count': n_row_zero}
                if n_posted>0:
                    msg['not_posted'] = {'msg': 'Data Tidak Di Proses %s \n' % (n_posted),
                                          'count': n_posted}
                msg['proses'] = {'msg': 'Data Di Proses %s ' % (n_id),
                                 'count':n_id}
                
                return dict(success = True,
                            msg     = msg)
                        
        return dict(success = False,
                    msg     = 'Terjadi kesalahan proses')

    ##########
    # CSV #
    ##########
    @view_config(route_name='pbb-ketetapan-rekap-csv', renderer='csv',
                 permission='pbb-ketetapan-rekap-csv')
    def view_csv(self):
        req = self.req
        ses = self.ses
        params   = req.params
        url_dict = req.matchdict
        
        q = pbbDBSession.query(SpptRekap.id,
                        func.to_char(SpptRekap.tanggal,'DD-MM-YYYY').label('tanggal'),
                        SpptRekap.kode,
                        SpptRekap.uraian, 
                        SpptRekap.pokok,
                        SpptRekap.posted,).\
                filter(SpptRekap.tanggal.between(self.dt_awal, self.dt_akhir)).\
                filter(SpptRekap.posted==self.posted)
        
        # override attributes of response
        filename = 'pbb-ketetapan-rekap.csv'
        req.response.content_disposition = 'attachment;filename=' + filename
        rows = []
        header = []
        
        r = q.first()
        if r:
            header = r.keys()
            query = q.all()
            rows = []
            for item in query:
                rows.append(list(item))

        
        return {
          'header': header,
          'rows': rows,
        }                

#######
# Add #
#######
def form_validator(form, value):
    def err_kegiatan():
        raise colander.Invalid(form,
            'Kegiatan dengan no urut tersebut sudah ada')

class AddSchema(colander.Schema):
    tahun       = colander.SchemaNode(
                            colander.String())
    uraian      = colander.SchemaNode(
                            colander.String(),
                            missing = colander.drop)
    tahun_tetap = colander.SchemaNode(
                            colander.String(),
                            title = "Tahun Ketetapan")
    nilai         = colander.SchemaNode(
                            colander.String())
    
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
        row = SpptRekap()
    row.from_dict(values)
    pbbDBSession.add(row)
    pbbDBSession.flush()
    return row

def save_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
        values['update_uid'] = request.user.id
        values['updated'] = datetime.now()
    else:
        values['create_uid'] = request.user.id
        values['created'] = datetime.now()
        values['posted'] = 0
        
    row = save(request, values, row)
    request.session.flash('Saldo Awal sudah disimpan.')
    return row

def route_list(request):
    return HTTPFound(location=request.route_url('pbb-ketetapan-rekap'))

def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r

########
# Edit #
########
def query_id(id):
    return pbbDBSession.query(SpptRekap).\
           filter(SpptRekap.id==id)

def id_not_found(request):
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='pbb-ketetapan-rekap-view', renderer='templates/ketetapan_rekap/add.pt',
             permission='pbb-ketetapan-rekap-view')
def view_edit(request):
    row = query_id(request).first()

    if not row:
        return id_not_found(request)
    if row.posted:
        request.session.flash('Data sudah diposting', 'error')
        return route_list(request)

    form = get_form(request, EditSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()
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



