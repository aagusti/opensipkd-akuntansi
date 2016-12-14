import os
import uuid
from datetime import datetime
from sqlalchemy import not_, func, between
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from ..models import bphtbDBSession
from ..models.transaksi import SaldoAwal
#from ...tools import _DTstrftime, _DTnumber_format
#from ...views.base_views import base_view
from datatables import ColumnDT, DataTables

SESS_ADD_FAILED  = 'Tambah Saldo Awal gagal'
SESS_EDIT_FAILED = 'Edit Saldo Awal gagal'

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
    (1, 'PBB'),
    )

@view_config(route_name="bphtb-sa", renderer="templates/saldo_awal/list.pt",
             permission="bphtb-sa")
def view(request):
    return dict(project='Integrasi')

##########
# Action #
##########
@view_config(route_name='bphtb-sa-act', renderer='json',
             permission='bphtb-sa-act')
def view_act(request):
    req = request
    ses = req.session
    params   = req.params
    url_dict = req.matchdict
    tahun = 'tahun' in params and params['tahun'] or \
                datetime.now().strftime('%Y')
    posted = 'posted' in params and params['posted'] or 0
        
    if url_dict['id']=='grid':
        #pk_id = 'id' in params and params['id'] and int(params['id']) or 0
        if url_dict['id']=='grid':
            # defining columns
            columns = []
            columns.append(ColumnDT(SaldoAwal.id, mData='id'))
            columns.append(ColumnDT(SaldoAwal.tahun, mData='tahun'))
            columns.append(ColumnDT(SaldoAwal.uraian, mData='uraian'))
            columns.append(ColumnDT(SaldoAwal.tahun_tetap, mData='tahun_tetap'))
            columns.append(ColumnDT(SaldoAwal.nilai, mData='nilai'))
            columns.append(ColumnDT(SaldoAwal.posted, mData='posted'))

            query = bphtbDBSession.query().select_from(SaldoAwal).\
                              filter(SaldoAwal.tahun==tahun,
                                     SaldoAwal.posted==posted
                                    )
            rowTable = DataTables(req.GET, query, columns)
            return rowTable.output_result()

#######
# Add #
#######
def form_validator(form, value):
    def err_kegiatan():
        raise colander.Invalid(form,
            'Kegiatan dengan no urut tersebut sudah ada')

class AddSchema(colander.Schema):
    tahun      = colander.SchemaNode(
                            colander.String())
    uraian      = colander.SchemaNode(
                            colander.String(),
                            missing = colander.drop)
    tahun_tetap         = colander.SchemaNode(
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
        row = SaldoAwal()
    row.from_dict(values)
    bphtbDBSession.add(row)
    bphtbDBSession.flush()
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
    return HTTPFound(location=request.route_url('bphtb-sa'))

def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r

@view_config(route_name='bphtb-sa-add', renderer='templates/saldo_awal/add.pt',
             permission='bphtb-sa-add')
def view_add(request):
    form = get_form(request, AddSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()
            controls_dicted = dict(controls)
            
            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                return dict(form=form)
                
            row = save_request(controls_dicted, request)
            #return HTTPFound(location=request.route_url('bphtb-sa-edit',id=row.id))
        return route_list(request)
    elif SESS_ADD_FAILED in request.session:
        del request.session[SESS_ADD_FAILED]
    return dict(form=form)

########
# Edit #
########
def query_id(request):
    return bphtbDBSession.query(SaldoAwal).filter(SaldoAwal.id==request.matchdict['id'])

def id_not_found(request):
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='bphtb-sa-edit', renderer='templates/saldo_awal/add.pt',
             permission='bphtb-sa-edit')
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

##########
# Delete #
##########
@view_config(route_name='bphtb-sa-delete', renderer='templates/saldo_awal/delete.pt',
             permission='bphtb-sa-delete')
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
            bphtbDBSession.query(ARInvoicePbb).filter(ARInvoicePbb.id==request.matchdict['id']).delete()
            bphtbDBSession.flush()
            msg = '%s dengan id %s telah berhasil.' % (request.title, row.id)
            request.session.flash(msg)
        return route_list(request)
    return dict(row=row,form=form.render())

###########
# Posting #
###########
@view_config(route_name='bphtb-sa-post', renderer='json',
             permission='bphtb-sa-post')
def view_posting(request):
    if request.POST:
        controls = dict(request.POST.items())
        for id in controls['id'].split(","):
            row    = query_id(id).first()
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
                pass 
            else:
                pass
                
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

##########
# CSV #
##########
@view_config(route_name='bphtb-sa-csv', renderer='csv',
             permission='bphtb-sa-csv')
def view_csv(request):
    ses = request.session
    req = request
    params   = req.params
    url_dict = req.matchdict
    tahun = 'tahun' in params and params['tahun'] or \
                datetime.now().strftime('%Y')
    q = bphtbDBSession.query(SaldoAwal.id,
                          SaldoAwal.tahun,
                          SaldoAwal.uraian,
                          SaldoAwal.tahun_tetap,
                          SaldoAwal.nilai,
                          SaldoAwal.posted,).\
                  filter(SaldoAwal.tahun==tahun)

    r = q.first()
    header = r.keys()
    query = q.all()
    rows = []
    for item in query:
        rows.append(list(item))

    # override attributes of response
    filename = 'bphtb-sa.csv'
    request.response.content_disposition = 'attachment;filename=' + filename

    return {
      'header': header,
      'rows': rows,
    }
