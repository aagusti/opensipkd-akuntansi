import os
import uuid
from datetime import datetime
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from ...views.common import ColumnDT, DataTables

from sqlalchemy import not_, func, between
from ..models import bphtbDBSession
from ..models.transaksi import SspdBphtb
from ...tools import _DTstrftime, _DTnumber_format, FixLength
from ..views import BphtbView
import re
from ..views import BPHTB_SELF    
class BphtbKetetapanView(BphtbView):
    def __init__(self, request):
        super(BphtbKetetapanView, self).__init__(request)
        
    @view_config(route_name="bphtb-ketetapan", renderer="templates/ketetapan/list.pt",
                 permission="bphtb-ketetapan")
    def view_list(self):
        return dict(project='Integrasi')

    ##########
    # Action #
    ##########
    @view_config(route_name='bphtb-ketetapan-act', renderer='json',
                 permission='bphtb-ketetapan-act')
    def view_act(self):
        url_dict = self.req.matchdict
        if url_dict['id']=='grid':
            if url_dict['id']=='grid':
                columns = [
                    ColumnDT(SspdBphtb.id, mData="id"),
                    ColumnDT(func.concat(SspdBphtb.tahun,
                             func.concat(".", 
                             func.concat( func.lpad(SspdBphtb.kode, 2, '0'), 
                             func.concat(".", func.lpad(SspdBphtb.no_urut, 5, '0'))))),
                             mData="no_tagihan"),
                    ColumnDT(func.to_char(SspdBphtb.created,"DD-MM-YYYY"), mData="tanggal"),
                    ColumnDT(func.concat(SspdBphtb.kd_propinsi,
                             func.concat(".", 
                             func.concat(SspdBphtb.kd_dati2, 
                             func.concat("-", 
                             func.concat(SspdBphtb.kd_kecamatan,
                             func.concat(".", 
                             func.concat(SspdBphtb.kd_kelurahan,
                             func.concat("-", 
                             func.concat(SspdBphtb.kd_blok,
                             func.concat(".", 
                             func.concat(SspdBphtb.no_urut,
                             func.concat(".", SspdBphtb.kd_jns_op)))))))))))) ,
                             mData='nop'),
                    ColumnDT(SspdBphtb.thn_pajak_sppt, mData='tahun'),
                    ColumnDT(SspdBphtb.wp_nama, mData='wp_nama'),
                    ColumnDT(SspdBphtb.npop, mData='npop'),
                    ColumnDT(SspdBphtb.tarif, mData='tarif'),
                    ColumnDT(SspdBphtb.terhutang, mData='terhutang'),
                    ColumnDT(SspdBphtb.bphtb_sudah_dibayarkan, mData='setoran'),
                    ColumnDT(SspdBphtb.bphtb_harus_dibayarkan, mData='sisa'),
                    ColumnDT(SspdBphtb.posted, mData='posted'),
                ]
                
                query = bphtbDBSession.query().select_from(SspdBphtb).\
                                     filter(SspdBphtb.created.between(self.dt_awal,self.dt_akhir)).\
                                     filter(SspdBphtb.posted == self.posted,
                                            not_(SspdBphtb.kode.in_(BPHTB_SELF)))
                
                rowTable = DataTables(self.req.GET, query, columns)
                return rowTable.output_result()
                # select b.id, b.transno, b.tanggal, get_nop_bank(b.id,true) as nop,
                # b.thn_pajak_sppt, b.wp_nama, b.bayar, b.no_tagihan
                # left join bphtb_sspd s on b.sspd_id=s.id
                # from bphtb_bank b

    ##########
    # CSV #
    ##########
    @view_config(route_name='bphtb-ketetapan-csv', renderer='csv',
                 permission='bphtb-ketetapan-csv')
    def view_csv(self):
        q = bphtbDBSession.query(SspdBphtb.id.label("id"),
                    SspdBphtb.transno.label("transno"),
                    func.to_char(SspdBphtb.tanggal,"DD-MM-YYYY").label("tanggal"),
                    func.concat(SspdBphtb.kd_propinsi,
                             func.concat(".", 
                             func.concat(SspdBphtb.kd_dati2, 
                             func.concat("-", 
                             func.concat(SspdBphtb.kd_kecamatan,
                             func.concat(".", 
                             func.concat(SspdBphtb.kd_kelurahan,
                             func.concat("-", 
                             func.concat(SspdBphtb.kd_blok,
                             func.concat(".", 
                             func.concat(SspdBphtb.no_urut,
                             func.concat(".", SspdBphtb.kd_jns_op)))))))))))).label('nop'),
                    SspdBphtb.thn_pajak_sppt.label('tahun'),
                    SspdBphtb.pembayaran_ke.label('ke'),
                    SspdBphtb.wp_nama.label('wp_nama'),
                    (SspdBphtb.bayar - SspdBphtb.denda).label('pokok'),
                    SspdBphtb.denda.label('denda'),
                    SspdBphtb.bayar.label('bayar'),
                    SspdBphtb.posted.label('posted')).\
                filter(SspdBphtb.tanggal.between(self.dt_awal, self.dt_akhir),)
        r = q.first()
        header = r.keys()
        rows = []
        for item in q.all():
            rows.append(list(item))

        # override attributes of response
        filename = 'bphtb-self.csv'
        self.req.response.content_disposition = 'attachment;filename=' + filename

        return {
          'header': header,
          'rows': rows,
        }

    ###########
    # Posting #
    ###########
    @view_config(route_name='bphtb-ketetapan-post', renderer='json',
                 permission='bphtb-ketetapan-post')
    def view_posting(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict
        n_id_not_found = n_row_zero = n_posted = n_id = 0
        if req.POST:
            if url_dict['id']=='post':
                controls = dict(req.POST.items())
                for id in controls['id'].split(","):
                    q = query_id(id)
                    q = q.filter(SspdBphtb.created.\
                          between(self.dt_awal,self.dt_akhir))
                    q = q.filter(SspdBphtb.posted == self.posted)
                    row    = q.first()
                    if not row:
                        n_id_not_found = n_id_not_found + 1
                        continue

                    if not row.bphtb_harus_dibayarkan:
                        n_row_zero = n_row_zero + 1
                        continue

                    if not self.posted and row.posted:
                        n_posted = n_posted + 1
                        continue

                    if self.posted and not row.posted:
                        n_posted = n_posted + 1
                        continue
                        
                    if row.posted > 1:
                        n_posted = n_posted + 1
                        continue
                    
                    n_id = n_id + 1

                    #id_inv = row.id
                    
                    if self.posted:
                        row.posted = 0 
                    else:
                        row.posted = 1
                    
                    bphtbDBSession.add(row)
                    bphtbDBSession.flush()
                    
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
                
#######
# Add #
#######
# def form_validator(form, value):
    # def err_kegiatan():
        # raise colander.Invalid(form,
            # 'Kegiatan dengan no urut tersebut sudah ada')

# class AddSchema(colander.Schema):
    # tahun       = colander.SchemaNode(
                            # colander.String())
    # uraian      = colander.SchemaNode(
                            # colander.String(),
                            # missing = colander.drop)
    # tahun_tetap = colander.SchemaNode(
                            # colander.String(),
                            # title = "Tahun Ketetapan")
    # nilai         = colander.SchemaNode(
                            # colander.String())
    
# class EditSchema(AddSchema):
    # id             = colander.SchemaNode(
                          # colander.Integer(),
                          # oid="id")

# def get_form(request, class_form):
    # schema = class_form(validator=form_validator)
    # schema = schema.bind(jenis_id=JENIS_ID,sumber_id=SUMBER_ID)
    # schema.request = request
    # return Form(schema, buttons=('simpan','batal'))

# def save(request, values, row=None):
    # if not row:
        # row = SspdBphtb()
    # row.from_dict(values)
    # bphtbDBSession.add(row)
    # bphtbDBSession.flush()
    # return row

# def save_request(values, request, row=None):
    # if 'id' in request.matchdict:
        # values['id'] = request.matchdict['id']
        # values['update_uid'] = request.user.id
        # values['updated'] = datetime.now()
    # else:
        # values['create_uid'] = request.user.id
        # values['created'] = datetime.now()
        # values['posted'] = 0
        
    # row = save(request, values, row)
    # request.session.flash('Saldo Awal sudah disimpan.')
    # return row

def route_list(request):
    return HTTPFound(location=request.route_url('bphtb-ketetapan'))

def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r

########
# Edit #
########
def query_id(value):
    return bphtbDBSession.query(SspdBphtb).\
           filter(SspdBphtb.id==value)

def id_not_found(request):
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

# @view_config(route_name='bphtb-ketetapan-view', renderer='templates/ketetapan/add.pt',
             # permission='bphtb-ketetapan-view')
# def view_edit(request):
    # row = query_id(request).first()

    # if not row:
        # return id_not_found(request)
    # if row.posted:
        # request.session.flash('Data sudah diposting', 'error')
        # return route_list(request)

    # form = get_form(request, EditSchema)
    # if request.POST:
        # if 'simpan' in request.POST:
            # controls = request.POST.items()
            # try:
                # c = form.validate(controls)
            # except ValidationFailure, e:
                # return dict(form=form)
            # save_request(dict(controls), request, row)
        # return route_list(request)
    # elif SESS_EDIT_FAILED in request.session:
        # del request.session[SESS_EDIT_FAILED]
        # return dict(form=form)
    # values = row.to_dict()
    # form.set_appstruct(values)
    # return dict(form=form)





