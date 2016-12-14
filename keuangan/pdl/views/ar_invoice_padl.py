import os
import uuid
from datetime import datetime
from sqlalchemy import not_, func, between
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from ...models import DBSession
from ...models.keuangan import SipkdDBSession
from ...models.ar import ARInvoiceTrans
from ...models.keuangan import SipkdSkp, SipkdSkpDet, SipkdUnit, SipkdRek4
from ...tools import _DTstrftime, _DTnumber_format
from ...views.base_views import base_view
from datatables import ColumnDT, DataTables

SESS_ADD_FAILED  = 'Tambah Invoice gagal'
SESS_EDIT_FAILED = 'Edit Invoice gagal'

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
    (3, 'PADL'),
    (4, 'Manual'),
    #(1, 'PBB'),
    #(2, 'BPHTB'),
    )
    
class ListSchema(colander.Schema):
    tahun_fltr      = colander.SchemaNode(
                            colander.Integer(),
                            title = "Tahun",
                            oid = "tahun_fltr",)
    tanggal_fltr    = colander.SchemaNode(
                            colander.Date(),
                            missing = colander.drop,
                            oid = "tanggal_fltr",)
    tanggal_to_fltr = colander.SchemaNode(
                            colander.Date(),
                            oid = "tanggal_to_fltr",)
    posted_fltr          = colander.SchemaNode(
                            colander.Boolean(),
                            oid='posted_fltr'
                            )

def list_form(request, class_form):
    schema = class_form(validator=form_validator)
    schema.request = request
    return Form(schema, buttons=('btn-filter'))


    
class view_invoice(base_view):
    @view_config(route_name="ar-invoice-padl", renderer="templates/ar-invoice-padl/list.pt",
                 permission="ar-invoice-padl")
    def view_list(self):
        params   = dict(self.req.params)
        form = list_form(self.req, ListSchema)
        if self.req.POST:
            if 'btn-filter' in self.req.POST:
                controls = dict(self.req.POST.items())
                self.ses['tahun']=controls['tahun_fltr']
                self.ses['tanggal']=controls['tanggal_fltr']
                self.ses['tanggal_to']=controls['tanggal_to_fltr']
                if 'posted_fltr' in controls and controls['posted_fltr']:
                    self.ses['posted'] = 1
                else:
                    self.ses['posted'] = 0
        #url_dict = self.req.matchdict
        return dict(form=form.render())


##########
# Action #
##########
@view_config(route_name='ar-invoice-padl-act', renderer='json',
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
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('rekening_kd'))
            columns.append(ColumnDT('rekening_nm'))
            columns.append(ColumnDT('tgl_tetap', filter=_DTstrftime))
            columns.append(ColumnDT('pokok', filter=_DTnumber_format))
            columns.append(ColumnDT('denda', filter=_DTnumber_format))
            columns.append(ColumnDT('bunga', filter=_DTnumber_format))
            columns.append(ColumnDT('posted'))

            query = DBSession.query(ARInvoiceTrans.id,
                      ARInvoiceTrans.unit_kd,
                      ARInvoiceTrans.kode,
                      ARInvoiceTrans.nama,
                      ARInvoiceTrans.rekening_kd,
                      ARInvoiceTrans.rekening_nm,
                      ARInvoiceTrans.pokok,
                      ARInvoiceTrans.denda,
                      ARInvoiceTrans.bunga,
                      ARInvoiceTrans.posted,
                      ARInvoiceTrans.tgl_tetap,
                      ARInvoiceTrans.tgl_validasi,
                      ).filter(ARInvoiceTrans.tahun==ses['tahun'],
                               between(ARInvoiceTrans.tgl_tetap, ses['tanggal'], ses['tanggal_to']),
                               ARInvoiceTrans.posted==ses['posted']
                      )
                    #).order_by(ARInvoiceTrans.kode.asc()
                    #)
            rowTable = DataTables(req, ARInvoiceTrans, query, columns)
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
                            title = "No. Bayar")
    nama         = colander.SchemaNode(
                            colander.String())
    alamat       = colander.SchemaNode(
                            colander.String())
    uraian       = colander.SchemaNode(
                            colander.String(),
                            missing = colander.drop)
    tgl_tetap    = colander.SchemaNode(
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
                            title = "No. Ketetapan")
    ref_nama     = colander.SchemaNode(
                            colander.String(),
                            title = "Uraian")
    kecamatan_kd = colander.SchemaNode(
                            colander.String(),
                            title = "Kecamatan",
                            missing = colander.drop)
    kecamatan_nm = colander.SchemaNode(
                            colander.String(),
                            missing = colander.drop)
    kelurahan_kd = colander.SchemaNode(
                            colander.String(),
                            title = "Kelurahan",
                            missing = colander.drop)
    kelurahan_nm = colander.SchemaNode(
                            colander.String(),
                            missing = colander.drop)
    is_kota      = colander.SchemaNode(
                            colander.Boolean(),
                            title = "Kota")
    npwpd        = colander.SchemaNode(
                            colander.String(),
                            missing = colander.drop)
    jth_tempo    = colander.SchemaNode(
                            colander.Date(),
                            missing = colander.drop,
                            oid = "jth_tempo")

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
    return HTTPFound(location=request.route_url('ar-invoice-padl'))

def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r

@view_config(route_name='ar-invoice-padl-add', renderer='templates/ar-invoice-padl/add.pt',
             permission='ar-invoice-padl-add')
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
                cek  = DBSession.query(ARInvoiceTrans).filter(ARInvoiceTrans.kode==c).first()
                if cek :
                    request.session.flash('Kode ARInvoice sudah ada.', 'error')
                    return HTTPFound(location=request.route_url('ar-invoice-add'))

            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                return dict(form=form)
            row = save_request(controls_dicted, request)
            return HTTPFound(location=request.route_url('ar-invoice-edit',id=row.id))
        return route_list(request)
    elif SESS_ADD_FAILED in request.session:
        del request.session[SESS_ADD_FAILED]
    return dict(form=form)

########
# Edit #
########
def query_id(request):
    return DBSession.query(ARInvoiceTrans).filter(ARInvoiceTrans.id==request.matchdict['id'])

def id_not_found(request):
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='ar-invoice-padl-edit', renderer='templates/ar-invoice-padl/add.pt',
             permission='ar-invoice-padl-edit')
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
            cek = DBSession.query(ARInvoiceTrans).filter(ARInvoiceTrans.kode==c).first()
            if cek:
                kode1 = DBSession.query(ARInvoiceTrans).filter(ARInvoiceTrans.id==uid).first()
                d     = kode1.kode
                if d!=c:
                    request.session.flash('Kode ARInvoiceTrans sudah ada', 'error')
                    return HTTPFound(location=request.route_url('ar-invoice-edit',id=row.id))

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
@view_config(route_name='ar-invoice-padl-delete', renderer='templates/ar-invoice-padl/delete.pt',
             permission='ar-invoice-padl-delete')
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
            DBSession.query(ARInvoiceTrans).filter(ARInvoiceTrans.id==request.matchdict['id']).delete()
            DBSession.flush()
            request.session.flash(msg)
        return route_list(request)
    return dict(row=row,form=form.render())

###########
# Posting #
###########
def query_post_id(id):
    return DBSession.query(ARInvoiceTrans).filter(ARInvoiceTrans.id==id)

@view_config(route_name='ar-invoice-padl-post', renderer='json',
             permission='ar-invoice-padl-post')
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
                row_skp = SipkdSkp()
                row_skp.unitkey  = SipkdUnit.get_key_by_kode(row.unit_kd)
                row_skp.noskp    = "%s/%s" % (row.kode, row.ref_kode)
                row_skp.kdstatus = '70'
                row_skp.keybend  = '1797_'
                row_skp.idxkode  = '1' #pendapatan
                row_skp.kenaikan = 0
                row_skp.npwpd    = row.npwpd[-10:]
                row_skp.tglskp   = row.tgl_tetap
                row_skp.penyetor = row.nama
                row_skp.alamat   = row.alamat
                row_skp.uraiskp  = row.rekening_nm
                row_skp.tgltempo = row.jth_tempo
                #row_skp.tglvalid = datetime.now()
                row_skp.bunga    = row.denda+row.bunga
                SipkdDBSession.add(row_skp)
                SipkdDBSession.flush()

                if row.pokok>0:
                    row_skpdet = SipkdSkpDet()
                    row_skpdet.unitkey = row_skp.unitkey
                    row_skpdet.noskp   = row_skp.noskp
                    row_skpdet.nilai   = row.pokok
                    row_skpdet.mtgkey  = SipkdRek4.get_key_by_kode(row.rekening_kd)
                    row_skpdet.nojetra = '11' #Penerimaan STS/TBP
                    SipkdDBSession.add(row_skpdet)
                    SipkdDBSession.flush()

                row_skp.tglvalid = row_skp.tglskp
                SipkdDBSession.add(row_skp)
                SipkdDBSession.flush()
                row.posted = 1
                DBSession.add(row)
                DBSession.flush()
            else:
                unitkey = SipkdUnit.get_key_by_kode(row.unit_kd)
                noskp = "%s/%s" % (row.kode, row.ref_kode)

                row_skpdet = SipkdDBSession.query(SipkdSkpDet).\
                                         filter_by(unitkey = unitkey,
                                                   noskp   = noskp).delete()
                SipkdDBSession.flush()

                row_skp = SipkdDBSession.query(SipkdSkp).\
                                         filter_by(unitkey = unitkey,
                                                   noskp   = noskp).delete()
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

##########
# CSV #
##########
@view_config(route_name='ar-invoice-padl-csv', renderer='csv',
             permission='ar-invoice-padl-csv')
def view_csv(request):
    ses = request.session
    req = request
    params   = req.params
    url_dict = req.matchdict
    q = DBSession.query(ARInvoiceTrans.id,
              ARInvoiceTrans.unit_kd,
              ARInvoiceTrans.kode,
              ARInvoiceTrans.nama,
              ARInvoiceTrans.rekening_kd,
              ARInvoiceTrans.rekening_nm,
              ARInvoiceTrans.pokok,
              ARInvoiceTrans.denda,
              ARInvoiceTrans.bunga,
              ARInvoiceTrans.posted,
              ARInvoiceTrans.tgl_tetap,
              ARInvoiceTrans.tgl_validasi,
              ).filter(ARInvoiceTrans.tahun==ses['tahun'],
                       between(ARInvoiceTrans.tgl_tetap, ses['tanggal'], ses['tanggal_to']),
                       ARInvoiceTrans.posted==ses['posted']
              )

    r = q.first()
    header = r.keys()
    query = q.all()
    rows = []
    for item in query:
        rows.append(list(item))

    # override attributes of response
    filename = 'ar-invoice.csv'
    request.response.content_disposition = 'attachment;filename=' + filename

    return {
      'header': header,
      'rows': rows,
    }
