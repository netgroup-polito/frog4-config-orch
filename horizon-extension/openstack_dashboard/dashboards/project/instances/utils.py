
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import xmltodict 
import StringIO
import json
import types
import collections
import os
import types
import copy
import re

from pyang.__init__ import Context, FileRepository
from pyang.translators.yin import YINPlugin
from pyang import plugin

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions

from openstack_dashboard import api

from openstack_dashboard.dashboards.project.instances.external_rest \
    import Orchestrator
from openstack_dashboard.dashboards.project.instances.external_rest \
    import ConfigurationServer
LOG = logging.getLogger(__name__)


def flavor_list(request):
    """Utility method to retrieve a list of flavors."""
    try:
        return api.nova.flavor_list(request)
    except Exception:
        exceptions.handle(request,
                          _('Unable to retrieve instance flavors.'))
        return []


def sort_flavor_list(request, flavors):
    """Utility method to sort a list of flavors.
        By default, returns the available flavors, sorted by RAM
        usage (ascending). Override these behaviours with a
        CREATE_INSTANCE_FLAVOR_SORT dict
        in local_settings.py.
    """
    def get_key(flavor, sort_key):
        try:
            return getattr(flavor, sort_key)
        except AttributeError:
            LOG.warning('Could not find sort key "%s". Using the default '
                        '"ram" instead.', sort_key)
            return getattr(flavor, 'ram')
    try:
        flavor_sort = getattr(settings, 'CREATE_INSTANCE_FLAVOR_SORT', {})
        sort_key = flavor_sort.get('key', 'ram')
        rev = flavor_sort.get('reverse', False)
        if not callable(sort_key):
            key = lambda flavor: get_key(flavor, sort_key)
        else:
            key = sort_key
        flavor_list = [(flavor.id, '%s' % flavor.name)
                   for flavor in sorted(flavors, key=key, reverse=rev)]
        return flavor_list
    except Exception:
        exceptions.handle(request,
                          _('Unable to sort instance flavors.'))
        return []

class FormFields(object):
    '''
    Define the fields that are showed in the configuration panel
    '''
    
    def __init__(self, instance_id):
        self.instance_id = instance_id
        self.generate_json = {}
        self.yang_model = None
        self.template = None
        self.yang = None
        self.description = None
        self.fields = None        

    def inizialize_form(self):
        self.yang_model = get_yang_model(self.instance_id)
        LOG.debug("yang model: "+json.dumps(self.yang_model))
        # Get the json instance of the model
        self.json_instance = json.loads(get_json_instance(self.instance_id))
        LOG.debug("json instance: "+json.dumps(self.json_instance))
        # Get template from orchestrator
        self.template = get_template(self.instance_id)
        
        # TODO: Convert internal interface name with external interface name:
        #       es.
        #           eth0 --> Control:0
        #           eth1 --> L2Port:0
        #           eth2 --> L2Port:1
    
        self.yang = self.yang_model['module']
        self.description = self.yang['description']['text']
        self.yang_import()
        self.fields = self.parse(self.yang, self.json_instance, "", augments={})
   
    def create_configuration_instance(self, data):
        form_responses = collections.OrderedDict(sorted(data.items()))
        LOG.info("ordered form responses: "+str(form_responses))
        
        self.parse_form_responces(form_responses)
        
        exit_code, output = validate_form(self.instance_id, self.generate_json)
        
        LOG.info("Output json_instance: "+json.dumps(self.generate_json))
        return self.generate_json, exit_code, output
  
    def parse_form_responces(self, form_responses):
        '''
        From the form responses create a json instance
        to configure the VNF
        '''
        yang_model = get_yang_model(self.instance_id)
        dicts = []
        for path, value in form_responses.iteritems():
            fields = path.split('/')
            parent = self.generate_json
            obj_value = None
            parent_list_index = None
            for index, field in enumerate(fields):          
                if index == len(fields)-1:
                    obj_value = value
                    # TODO: the type should be retrieved by the yang (currently we suppose that the field is always a string)
                    _type = 'string'
                    obj_field = field
                elif ':' in field:
                    _type='list'
                    obj_field = field.split(':')[0]
                    obj_value = []
                else:
                    _type='dict'
                    obj_field = field
                    obj_value = {}
                parent = self.create_json(field=obj_field, _type=_type, level=None,
                                         parent=parent, value=obj_value, list_index=parent_list_index)
                if ':' in field:
                    parent_list_index = int(field.split(':')[1])
            dicts.append(value)
        index_list = []
        value_list = []
        for index, value in self.generate_json.iteritems():
            index_list.append(index)
            value_list.append(value)
        for index_index, index_item in enumerate(index_list):
            self.generate_json[yang_model['module']['@name']+':'+index_item] = value_list[index_index]
            del self.generate_json[index_item]
        #self.generate_json[yang_model['module']['@name']+':'+index] = value
        #del self.generate_json[index]
        LOG.info("real json: "+json.dumps(self.generate_json))
        
    def create_json(self, field, _type, level, parent = None, value = None, list_index = None):
        obj = None
        if isinstance(parent, dict) or parent is None:
            if parent is not None and field in parent:
                obj = parent[field]
                return obj
            else:
                if parent is None:
                    parent = self.generate_json
                parent[field] = value
                obj = parent[field]
        elif isinstance(parent, list):
            # Note that the list of field from the form MUST be in alphabetic order 
            elem = {}
            elem[field] = value
            
            if len(parent) > list_index:
                if field not in parent[list_index]:
                    parent[list_index].update(elem)
                    obj = elem[field]
                else:
                    obj = parent[list_index][field]
            else:
                parent.append(elem)
                obj = elem[field]
        return obj   
 
    def object_from_instance(self, i, index, json_instance, field, value = None):
        if ':' in field:
            if json_instance is None:
                json_instance = []
            arg = {}
            arg[field.split(':')[0]] = value
            json_instance.append(value)
            return json_instance[field.split(':')[0]]
        else:
            if json_instance is None:
                json_instance = {}
            json_instance[field] = value
            return json_instance[field]
    
    def yang_import(self):
        '''
        Manage the the yang import in the model
        An example is the type inet:ipv4_address, 
        that is imported from ietf-inet-types.yang 
        '''
        class YangImport(object):
            def __init__(self, module, prefix):
                self.module = module
                self.prefix = prefix
        
        self.yang_imports = []
        if 'import' in self.yang:
            self.yang_imports.append(YangImport(self.yang['import']['@module'], self.yang['import']['prefix']['@value']))
    
    def get_rfc_module(self, module_name):
        '''
        Retrieve the yang module imported from those in the ietf folder.
        '''
        with open ("/usr/local/share/yang/modules/ietf/"+module_name+".yang", "r") as yang_model_file:
            ctx = Context(FileRepository())
            return transform_yang_to_dict(instance_id="rfc",
                                          yang_model_string=yang_model_file.read())
    
    def get_type_from_rfc(self, module_name, yang_type, patterns = None):
        '''
        Retrieve a type imported from an external module.
        '''
        print "get_type_from_rfc"
        patterns = patterns or []
        rfc_yang = self.get_rfc_module(module_name)
        prefix = rfc_yang['module']['prefix']['@value']
        for typedef in rfc_yang['module']['typedef']:
            
            if typedef['@name'] == yang_type:
                if typedef['type']['@name'] == 'union':
                    for union_type in typedef['type']['type']:
                        if prefix+':' in union_type['@name']:
                            external_yang_type, patterns_union = self.get_type_from_rfc(module_name, union_type['@name'].split(':')[1])
                        else:
                            external_yang_type, patterns_union = self.get_type_from_rfc(module_name, union_type['@name'])
                        patterns += patterns_union
                else:
                    external_yang_type = typedef['type']['@name']
                    if external_yang_type == 'string' and 'pattern' in  typedef['type']:
                        print str(type(typedef['type']['pattern']))
                        if type(typedef['type']['pattern']) is types.ListType:
                            for pattern_elem in typedef['type']['pattern']:
                                patterns.append(pattern_elem['@value'])
                        else:
                            patterns.append(typedef['type']['pattern']['@value'])      
        return external_yang_type, patterns

    def parse(self, yang, json_instance, path, key = None, list = False, list_index = None, augments = None):   
        '''
        Starting from the yang model and the json instance,
        that represents  the status of a VNF, this method
        return the fields that will be showed in the form. 
        ''' 
        # Parse augment
        if 'augment' in yang:
            if augments is None:
                augments = {}
            if yang['augment']['@target-node'] not in augments:
                augments[yang['augment']['@target-node']] = []
            augments[yang['augment']['@target-node']].append(yang['augment'])
        
        if '/'+path in augments:
            for augment in augments['/'+path][:]:
                if 'leaf' in augment:
                    if yang['leaf'] is None:
                        yang['leaf'] = []
                    yang['leaf'].append(augment['leaf'])
                augments['/'+path].remove(augment)
        
        # Parse container
        fields = []
        if 'container' in yang:
            if isinstance(yang['container'], types.ListType):
                for container in yang['container']:
                    if list is False:
                        if path != '':
                            new_json_instance = json_instance[container['@name']]
                            new_path = path+'/'+container['@name']
                        else:
                            new_json_instance = json_instance[yang['@name']+':'+container['@name']]
                            new_path = container['@name']
                    else:
                        new_json_instance = json_instance[container['@name']]
                        new_path = path+':'+str(list_index)+'/'+container['@name']
                    fields += self.parse(container, new_json_instance,  new_path, augments=augments, list_index=list_index)

            else:
                if list is False:
                    if path != '':
                        new_json_instance = json_instance[yang['container']['@name']]
                        new_path = path+'/'+yang['container']['@name']
                    else:
                        new_json_instance = json_instance[yang['@name']+':'+yang['container']['@name']]
                        new_path = yang['container']['@name']
                else:
                    new_json_instance = json_instance[yang['@name']]
                    new_path = path+':'+str(list_index)+'/'+yang['@name']
                fields += self.parse(yang['container'], new_json_instance,  new_path, augments=augments, list_index=list_index)                   
 
        # Parse list
        if 'list' in yang:
            for i, val in enumerate(json_instance[yang['list']['@name']]):
                fields += self.parse(yang['list'], val,  path+'/'+yang['list']['@name'], key = yang['list']['key']['@value'], list = True, list_index = i, augments=augments)
        
        # Parse leaf
        if 'leaf' in yang:
            for leaf in yang['leaf']:
                field = {}
                field['label'] = leaf['@name']
                if list is False:
                    field['id'] = path+'/'+leaf['@name']
                    field['long_id'] = 'id_'+path+'/'+leaf['@name']
                else:
                    field['id'] = path+':'+str(list_index)+'/'+leaf['@name']
                    field['long_id'] = 'id_'+path+':'+str(list_index)+'/'+leaf['@name']
                    field['list_object_id'] = str(list_index)
                field['default'] = json_instance[leaf['@name']]
                field['path'] = self.get_normalized_path(path)
                yang_type = leaf['type']['@name'].split(':')
                if len(yang_type) == 1:
                    field['type'] = leaf['type']['@name']
                else:
                    for yang_import in self.yang_imports:
                        if yang_import.prefix == yang_type[0]:
                            field['type'], field['patterns'] = self.get_type_from_rfc(yang_import.module, yang_type[1])
                           
                            
                if leaf['type']['@name'] == 'enumeration':
                    field['enumeration'] = []
                    for enum in leaf['type']['enum']:
                        el = (enum['@name'], enum['@name'])
                        field['enumeration'].append(el)
                if key == leaf['@name']:
                    field['key'] = True
                else:
                    field['key'] = False
                    
                field['indent'] = field['id'].count('/')
                fields.append(field)
        return fields
 
    def get_description(self):
        '''
        Get the description of the VNF from the 
        yang model.
        '''
        return self.description

    def get_fields(self):
        return self.fields

    def get_normalized_path(self, path):
        '''
        Get rid of the index of the lists in the path
        '''
        normalized_path = copy.deepcopy(path)
        if ':' in normalized_path:
            rest = normalized_path.split(':', 1)[1]
            list_index = rest.split('/', 1)[0]
            normalized_path = re.sub('\:'+list_index+'\/', '/', normalized_path)
        return normalized_path
    
    def get_paths(self):
        '''
        Get all paths, of all fields that will be showed
        in the form. This paths will be used in the rendering
        to indent in the right way the lables. 
        '''
        paths = []
        for field in self.fields:
            path = self.get_normalized_path(field['path'])
            paths.append(path)
        paths = set(paths)
        print paths
        paths_with_labels = []
        for path in paths:
            paths_with_label = {}
            paths_with_label['layers'] = {}
            paths_with_label['layers']['0'] = None
            paths_with_label['layers']['1'] = None
            paths_with_label['layers']['2'] = None
            paths_with_label['layers']['3'] = None
            paths_with_label['layers']['4'] = None
            paths_with_label['layers']['5'] = None
            for index, pp in enumerate(path.split('/')):
                paths_with_label['layers'][str(index)] = pp
            paths_with_label['label']  = path
            paths_with_label['path']  = path
            paths_with_labels.append(paths_with_label)
        return paths_with_labels

class Bash():
    '''
    Wrapper used to execure a bash command
    '''
    def __init__(self, command):
        command = command + " 2>&1"
        self.pipe = os.popen(command)
        self.output = self.pipe.read()
        self.exit_code = self.pipe.close()
        if self.exit_code is not None:
            print "Error code: "+str(self.exit_code)+" -Due to command: "+str(command)+" - Message: "+self.output
    
    def get_output(self):
        return self.output

def transform_yang_to_dict(instance_id, yang_model_string): 
    '''
    Transform a yang model in a python dictionary,
    in order to use it both to validate the json_instance
    and to retrieve the field to show in the form.
    '''
    class Opts(object):
        def __init__(self, yin_canonical=False, yin_pretty_strings=True):
            self.yin_canonical = yin_canonical
            self.yin_pretty_strings = yin_pretty_strings
    ctx = Context(FileRepository())
    yang_mod =  ctx.add_module(instance_id, yang_model_string, format='yang')
    
    yin = YINPlugin()
    modules = []
    modules.append(yang_mod)
    ctx.opts = Opts()
    yin_string = StringIO.StringIO()
    yin.emit(ctx=ctx, modules=modules, fd=yin_string)
    xml = yin_string.getvalue()
    return xmltodict.parse(xml)

def validate_form(instance_id, form_responses):
    '''
    Validate the json instance created starting 
    from the form.
    '''
    json_instance = json.dumps(form_responses)
    LOG.info("Dentro validate: "+json_instance)
    yang_model = _get_yang_model(instance_id)
    yang_model_dict = transform_yang_to_dict(instance_id, yang_model)
    Bash('cd /etc/openstack-dashboard/ \n mkdir tmp')
    Bash('cd /etc/openstack-dashboard/tmp/ \n cp /usr/local/share/yang/modules/ietf/* .')
    

    # Save temporary on disk the xml and the yang model
    yang_file_name = yang_model_dict['module']['@name']+".yang"
    yang_name = yang_model_dict['module']['@name']
    with open ("/etc/openstack-dashboard/tmp/"+yang_file_name, "w") as yang_model_file:
        yang_model_file.write(yang_model)
    json_file_name = yang_name+".json"
    with open ("/etc/openstack-dashboard/tmp/"+json_file_name, "w") as yang_model_file:
        yang_model_file.write(json_instance)

    Bash('cd /etc/openstack-dashboard/tmp/ \n yang2dsdl -t config '+yang_file_name)
    Bash('cd /etc/openstack-dashboard/tmp/ \n pyang -f jtox -o '+yang_name+'.jtox '+yang_name+'.yang')
    Bash('cd /etc/openstack-dashboard/tmp/ \n json2xml -t config -o '+yang_name+'.xml '+yang_name+'.jtox '+yang_name+'.json')
    response = Bash('cd  /etc/openstack-dashboard/tmp/ \n yang2dsdl -s -j -b '+yang_name+' -t config -v '+yang_name+'.xml')
    return response.exit_code,  response.get_output()

def send_configuration(instance_id, json_instance):
    '''
    Send to the configuration server the json instance
    created.
    '''
    ConfigurationServer().set_vnf_status(instance_id, json_instance)

def get_template(instance_id):
    '''
    Get from the orchestrator the template of 
    the VNF, to associate to
    the internal name of the interface, the label 
    used in the template.
    '''
    return Orchestrator().get_template(instance_id)

def get_json_instance(instance_id):
    '''
    Get from the configuration server the status 
    of the VNF.
    '''
    return ConfigurationServer().get_vnf_status(instance_id)

def _get_yang_model(instance_id):
    '''
    Get from the orchestrator the yang model 
    of the VNF.
    '''
    return Orchestrator().get_yang_model(instance_id)

def get_yang_model(instance_id):
    yang_model_string = _get_yang_model(instance_id)
    return transform_yang_to_dict(instance_id, yang_model_string)
