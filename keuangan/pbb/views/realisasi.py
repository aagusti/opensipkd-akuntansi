import os
import uuid
from datetime import datetime
from sqlalchemy import not_, func, between
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from ..models import pbbDBSession
from ...tool_apps import BAYAR
from ..models.tap import PembayaranSppt
from ...tools import _DTstrftime, _DTnumber_format, FixLength
#from ...views.base_views import base_view
from datatables import ColumnDT, DataTables
from ..views import PbbView
import re

SESS_ADD_FAILED  = 'Tambah Saldo Awal gagal'
SESS_EDIT_FAILED = 'Edit Saldo Awal gagal'

class RealisasiView(PbbView):
    def _init__(self,request):
        super(RealisasiView, self).__init__(request)
        
    @view_config(route_name="pbb-realisasi", renderer="templates/realisasi/list.pt",
                 permission="pbb-realisasi")
    def view_list(self):
        req = self.req
        ses = req.session
        params  = req.params
        return dict(project='Integrasi')

                    
    ##########
    # Action #
    ##########
    @view_config(route_name='pbb-realisasi-act', renderer='json',
                 permission='pbb-realisasi-act')
    def view_act(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict
        awal  = self.dt_awal
        akhir = self.dt_akhir    
        if url_dict['id']=='grid':
            if url_dict['id']=='grid':
                columns = [
                    ColumnDT(func.concat(PembayaranSppt.kd_propinsi,
                             func.concat(".", 
                             func.concat(PembayaranSppt.kd_dati2, 
                             func.concat("-", 
                             func.concat(PembayaranSppt.kd_kecamatan,
                             func.concat(".", 
                             func.concat(PembayaranSppt.kd_kelurahan,
                             func.concat("-", 
                             func.concat(PembayaranSppt.kd_blok,
                             func.concat(".", 
                             func.concat(PembayaranSppt.no_urut,
                             func.concat(".", PembayaranSppt.kd_jns_op)))))))))))) ,
                             mData='nop'),
                ColumnDT(PembayaranSppt.thn_pajak_sppt, mData='tahun'),
                ColumnDT(PembayaranSppt.pembayaran_sppt_ke, mData='ke'),
                ColumnDT(func.to_char(PembayaranSppt.tgl_pembayaran_sppt,'DD-MM-YYYY'), mData='tanggal'),
                ColumnDT(PembayaranSppt.jml_sppt_yg_dibayar - PembayaranSppt.denda_sppt, mData='pokok'),
                ColumnDT(PembayaranSppt.denda_sppt, mData='denda'),
                ColumnDT(PembayaranSppt.jml_sppt_yg_dibayar, mData='bayar'),
                ColumnDT(PembayaranSppt.posted, mData='posted')
                ]
                
                query = pbbDBSession.query().select_from(PembayaranSppt).\
                                     filter(PembayaranSppt.tgl_pembayaran_sppt.between(awal,akhir)).\
                                     filter(PembayaranSppt.posted == self.posted)
                rowTable = DataTables(req.GET, query, columns)
                return rowTable.output_result()

    ###########
    # Posting #
    ###########
    @view_config(route_name='pbb-realisasi-post', renderer='json',
                 permission='pbb-realisasi-post')
    def view_posting(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict
        n_id_not_found = n_row_zero = n_posted = n_id = 0
        if req.POST:
            controls = dict(req.POST.items())
            if url_dict['id']=='post':
                for id in controls['id'].split(","):
                    row    = query_nop(id).first()
                    if not row:
                        n_id_not_found = n_id_not_found + 1
                        continue

                    if not row.jml_sppt_yg_dibayar:
                        n_row_zero = n_row_zero + 1
                        continue

                    if not self.posted and row.posted:
                        n_posted = n_posted + 1
                        continue

                    if self.posted  and not row.posted:
                        n_posted = n_posted + 1
                        continue
                    if row.posted == 2:
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
    @view_config(route_name='pbb-realisasi-csv', renderer='csv',
                 permission='pbb-realisasi-csv')
    def view_csv(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict
        
        q = pbbDBSession.query(func.concat(PembayaranSppt.kd_propinsi,
                               func.concat(".", 
                               func.concat(PembayaranSppt.kd_dati2, 
                               func.concat("-", 
                               func.concat(PembayaranSppt.kd_kecamatan,
                               func.concat(".", 
                               func.concat(PembayaranSppt.kd_kelurahan,
                               func.concat("-", 
                               func.concat(PembayaranSppt.kd_blok,
                               func.concat(".", 
                               func.concat(PembayaranSppt.no_urut,
                               func.concat(".", PembayaranSppt.kd_jns_op)))))))))))),
                               PembayaranSppt.thn_pajak_sppt,
                               PembayaranSppt.pembayaran_sppt_ke,
                               func.to_char(PembayaranSppt.tgl_pembayaran_sppt,'DD-MM-YYYY').label('tanggal'),
                               (PembayaranSppt.jml_sppt_yg_dibayar-PembayaranSppt.denda_sppt).label('pokok'),
                               PembayaranSppt.denda_sppt.label('denda'),
                               PembayaranSppt.jml_sppt_yg_dibayar.label('bayar'),
                               PembayaranSppt.posted,).\
                          filter(PembayaranSppt.tgl_pembayaran_sppt.between(awal,akhir))
        r = q.first()
        header = r.keys()
        query = q.all()
        rows = []
        for item in query:
            rows.append(list(item))

        # override attributes of response
        filename = 'pbb-realisasi.csv'
        req.response.content_disposition = 'attachment;filename=' + filename

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
        row = PembayaranSppt()
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
    return HTTPFound(location=request.route_url('pbb-realisasi'))

def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r

########
# Edit #
########
def query_nop(value):
    val = re.sub("\D", "", value)
    print val
    nop = FixLength(BAYAR)
    nop.set_raw(val)
    #bayar = val[len(nop.get_raw()):]
    
    return pbbDBSession.query(PembayaranSppt).\
           filter(PembayaranSppt.kd_propinsi==nop['kd_propinsi'],
                  PembayaranSppt.kd_dati2==nop['kd_dati2'],
                  PembayaranSppt.kd_kecamatan==nop['kd_kecamatan'],
                  PembayaranSppt.kd_kelurahan==nop['kd_kelurahan'],
                  PembayaranSppt.kd_blok==nop['kd_blok'],
                  PembayaranSppt.no_urut==nop['no_urut'],
                  PembayaranSppt.kd_jns_op==nop['kd_jns_op'],
                  PembayaranSppt.thn_pajak_sppt==nop['thn_pajak_sppt'],
                  PembayaranSppt.pembayaran_sppt_ke==nop['pembayaran_sppt_ke'],
                  )

def id_not_found(request):
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='pbb-realisasi-view', renderer='templates/realisasi/add.pt',
             permission='pbb-realisasi-view')
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


