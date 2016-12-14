import locale
from types import (
    StringType,
    UnicodeType,
    )
from urllib import (
    urlencode,
    quote,
    quote_plus,
    )    
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.events import subscriber
from pyramid.events import BeforeRender
from pyramid.interfaces import IRoutesMapper
from pyramid.httpexceptions import (
    default_exceptionresponse_view,
    HTTPFound,
    )
from pyramid.renderers import JSON 
import datetime
from sqlalchemy import engine_from_config
from security import (
    group_finder,
    get_user,
    )
from models import (
    DBSession,
    Base,
    init_model,
    Route
    )
from tools import (
    DefaultTimeZone,
    money,
    should_int,
    thousand,
    as_timezone,
    split,
    )



# http://stackoverflow.com/questions/9845669/pyramid-inverse-to-add-notfound-viewappend-slash-true    
class RemoveSlashNotFoundViewFactory(object):
    def __init__(self, notfound_view=None):
        if notfound_view is None:
            notfound_view = default_exceptionresponse_view
        self.notfound_view = notfound_view

    def __call__(self, context, request):
        if not isinstance(context, Exception):
            # backwards compat for an append_notslash_view registered via
            # config.set_notfound_view instead of as a proper exception view
            context = getattr(request, 'exception', None) or context
        path = request.path
        registry = request.registry
        mapper = registry.queryUtility(IRoutesMapper)
        if mapper is not None and path.endswith('/'):
            noslash_path = path.rstrip('/')
            for route in mapper.get_routes():
                if route.match(noslash_path) is not None:
                    qs = request.query_string
                    if qs:
                        noslash_path += '?' + qs
                    return HTTPFound(location=noslash_path)
        return self.notfound_view(context, request)
    
# https://groups.google.com/forum/#!topic/pylons-discuss/QIj4G82j04c
def has_permission_(request, perm_names):
    if type(perm_names) in [UnicodeType, StringType]:
        perm_names = [perm_names]
    for perm_name in perm_names:
        if request.has_permission(perm_name):
            return True

@subscriber(BeforeRender)
def add_global(event):
     event['has_permission'] = has_permission_
     event['urlencode'] = urlencode
     event['quote_plus'] = quote_plus
     event['quote'] = quote   
     event['money'] = money
     event['should_int'] = should_int  
     event['thousand'] = thousand
     event['as_timezone'] = as_timezone
     event['split'] = split

def get_title(request):
    route_name = request.matched_route.name
    return titles[route_name]

main_title = 'opensipkd-keuangan'
titles = {}

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    init_model()

    if 'sipkd.url' in settings and settings['sipkd.url']:
        from sipkd.models import sipkdDBSession, sipkdBase
        engineSipkd = engine_from_config(settings, 'sipkd.')
        sipkdDBSession.configure(bind=engineSipkd)
        sipkdBase.metadata.bind = engineSipkd
    
    #added 09-08-2016
    if 'pdl.url' in settings and settings['pdl.url']:
        from pdl.models import pdlDBSession, pdlBase
        enginePdl = engine_from_config(settings, 'pdl.')
        pdlDBSession.configure(bind=enginePdl)
        pdlBase.metadata.bind = enginePdl
        pdl_schema = 'schema.pdl' in settings and settings['schema.pdl'] or None

    if 'pbb.url' in settings and settings['pbb.url']:
        from pbb.models import pbbDBSession, pbbBase, pbb_schema
        enginePbb = engine_from_config(settings, 'pbb.')
        pbbDBSession.configure(bind=enginePbb)
        pbbBase.metadata.bind = enginePbb
        pbb_schema = 'schema.pbb' in settings and settings['schema.pbb'] or None
        
    if 'bphtb.url' in settings and settings['bphtb.url']:
        from bphtb.models import bphtbDBSession, bphtbBase, bphtb_schema
        engineBphtb = engine_from_config(settings, 'bphtb.')
        bphtbDBSession.configure(bind=engineBphtb)
        bphtbBase.metadata.bind = engineBphtb
        bphtb_schema = 'schema.bphtb' in settings and settings['schema.bphtb'] or None
        
        
    session_factory = session_factory_from_settings(settings)
    if 'localization' not in settings:
        settings['localization'] = 'id_ID.UTF-8'
    locale.setlocale(locale.LC_ALL, settings['localization'])        
    if 'timezone' not in settings:
        settings['timezone'] = DefaultTimeZone
    config = Configurator(settings=settings,
                          root_factory='keuangan.models.RootFactory',
                          session_factory=session_factory)
    config.include('pyramid_beaker')                          
    config.include('pyramid_chameleon')

    authn_policy = AuthTktAuthenticationPolicy('sosecret',
                    callback=group_finder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()                          
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_request_method(get_user, 'user', reify=True)
    config.add_request_method(get_title, 'title', reify=True)
    config.add_notfound_view(RemoveSlashNotFoundViewFactory())        
                          
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('deform_static', 'deform:static')
    config.add_static_view('files', settings['static_files'])    
    
    config.add_renderer('csv', '.tools.CSVRenderer')
    
    routes = DBSession.query(Route.kode, Route.path, Route.nama).all()
    for route in routes:
        #if route.factory and route.factory != 'None': 
        #    config.add_route(route.kode, route.path) #(route.factory).encode("utf8"))
        #else:
        config.add_route(route.kode, route.path)
            
        if route.nama:
            titles[route.kode] = route.nama

    ############################################################################
    config.include('pyramid_rpc.jsonrpc') # JSON RPC
    json_renderer = JSON()
    json_renderer.add_adapter(datetime.datetime, lambda v, request: v.isoformat())
    json_renderer.add_adapter(datetime.date, lambda v, request: v.isoformat())
    config.add_renderer('myjson', json_renderer)
    #config.add_jsonrpc_endpoint('ws_user', '/ws/user', default_renderer="myjson")
    config.add_jsonrpc_endpoint('ws_keuangan', '/ws/keuangan', default_renderer="myjson")
    
    ############################################################################
 
    config.scan()
    app = config.make_wsgi_app()
    from paste.translogger import TransLogger
    app = TransLogger(app, setup_console_handler=False)    
    return app
