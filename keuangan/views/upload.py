import os
from datetime import (
    date,
    datetime,
    timedelta,
    )
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from deform.interfaces import FileUploadTempStore
from pyramid.path import AssetResolver
import webhelpers.paginate    
import colander
from deform import (
    Form,
    widget,
    FileData,    
    )
from ..models import (
    DBSession,
    User,
    )
# from ...models.imgw import (
    # Broadcast,
    # BroadcastPenerima as BP,
    # Status,
    # ImSelesai,
    # )
from ..tools import (
    get_ext,
    create_date,
    create_now,
    get_settings,
    date_from_str,
    dict_to_str,
    create_datetime,
    SaveFile,
    )
#from unggah import DbUpload
def route_list(request, p={}):
    q = dict_to_str(p)
    return HTTPFound(location=request.route_url('home', _query=q))

##########
# Unggah #
##########
class UploadLogo(SaveFile):
    def save(self, fs):
        input_file = fs.file
        ext = get_ext(fs.filename)
        fullpath = self.create_fullpath(ext)
        print ext, fullpath
        output_file = open(fullpath, 'wb')
        input_file.seek(0)
        while True:
            data = input_file.read(2<<16)
            if not data:
                break
            output_file.write(data)
        output_file.close()
        return fullpath     
        
tmpstore = FileUploadTempStore()      
        
class AddSchema(colander.Schema):
    upload = colander.SchemaNode(
                FileData(),
                widget=widget.FileUploadWidget(tmpstore),
                title='Unggah')


def get_form(schema_cls):
    schema = schema_cls()
    return Form(schema, buttons=('simpan', 'batalkan'))        
        

@view_config(route_name='upload-logo',
             renderer='templates/upload.pt',
             permission='upload-logo')
def view_file(request):
    form = get_form(AddSchema)
    if request.POST:
        if 'simpan' in request.POST:
            settings = get_settings()
            input_file = request.POST['upload'].file
            filename = request.POST['upload'].filename
            ext = get_ext(filename)
            
            if ext.lower()!='.png':
                request.session.flash('File harus format png','error')
                return dict(form=form.render())	

            resolver = AssetResolver()
            static_path = resolver.resolve('keuangan:static').abspath()
            fullpath = os.path.join( static_path, 'img/logo.png')
            print '------------------>',fullpath
            output_file = open(fullpath, 'wb')
            input_file.seek(0)
            while True:
                data = input_file.read(2<<16)
                if not data:
                    break
                output_file.write(data)
        
        return route_list(request)
    return dict(form=form.render())        
