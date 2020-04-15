import web

from dlkit.json_ import types
from dlkit.runtime import PROXY_SESSION, RUNTIME
from dlkit.runtime.primitives import InitializableLocale
from dlkit.runtime.primordium import Type
from dlkit.runtime.proxy_example import SimpleRequest

DEFAULT_LANGUAGE_TYPE = Type(**types.Language().get_type_data('DEFAULT'))
DEFAULT_SCRIPT_TYPE = Type(**types.Script().get_type_data('DEFAULT'))
DEFAULT_FORMAT_TYPE = Type(**types.Format().get_type_data('DEFAULT'))


def get_commenting_manager():
    condition = PROXY_SESSION.get_proxy_condition()
    dummy_request = SimpleRequest(username=web.ctx.env.get('HTTP_X_API_PROXY', 'student@tiss.edu'),
                                  authenticated=True)
    condition.set_http_request(dummy_request)

    if 'HTTP_X_API_LOCALE' in web.ctx.env:
        language_code = web.ctx.env['HTTP_X_API_LOCALE'].lower()
        if language_code in ['en', 'hi', 'te']:
            if language_code == 'en':
                language_code = 'ENG'
                script_code = 'LATN'
            elif language_code == 'hi':
                language_code = 'HIN'
                script_code = 'DEVA'
            else:
                language_code = 'TEL'
                script_code = 'TELU'
        else:
            language_code = DEFAULT_LANGUAGE_TYPE.identifier
            script_code = DEFAULT_SCRIPT_TYPE.identifier

        locale = InitializableLocale(language_type_identifier=language_code,
                                     script_type_identifier=script_code)

        condition.set_locale(locale)

    proxy = PROXY_SESSION.get_proxy(condition)
    return RUNTIME.get_service_manager('COMMENTING',
                                       proxy=proxy)
