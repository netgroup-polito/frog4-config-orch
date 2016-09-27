import xmltodict
import json
try:
    import StringIO
except ImportError:
    from io import StringIO

from pyang.__init__ import Context, FileRepository
from pyang.translators.yin import YINPlugin
from pyang import plugin

def _transform_yang_to_dict(yang_model_string): 
    class Opts(object):
        def __init__(self, yin_canonical=False, yin_pretty_strings=True):
            self.yin_canonical = yin_canonical
            self.yin_pretty_strings = yin_pretty_strings
    ctx = Context(FileRepository())
    yang_mod = ctx.add_module('yang', yang_model_string, format='yang')
    
    yin = YINPlugin()
    modules = []
    modules.append(yang_mod)
    ctx.opts = Opts()
    yin_string = StringIO()
    yin.emit(ctx=ctx, modules=modules, fd=yin_string)
    xml = yin_string.getvalue()
    return xmltodict.parse(xml)

def yang_to_json(yang_file):
    with open (yang_file, "r") as myfile:
	    yang_model=myfile.read().replace('\n', '')
	    yang_model_dict = _transform_yang_to_dict(yang_model)
    #print yang_model_dict['module']
    return json.dumps(yang_model_dict['module'], ensure_ascii=False)
