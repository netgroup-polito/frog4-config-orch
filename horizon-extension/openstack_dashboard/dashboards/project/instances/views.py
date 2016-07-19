

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Views for managing instances.
"""
import logging
import json

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django import http
from django import shortcuts
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
from horizon.utils import memoized
from horizon import workflows

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.instances \
    import forms as project_forms
from openstack_dashboard.dashboards.project.instances \
    import tables as project_tables
from openstack_dashboard.dashboards.project.instances \
    import tabs as project_tabs
from openstack_dashboard.dashboards.project.instances \
    import workflows as project_workflows
from openstack_dashboard.dashboards.project.instances \
    import utils as project_utils
LOG = logging.getLogger(__name__)

class IndexView(tables.DataTableView):
    table_class = project_tables.InstancesTable
    template_name = 'project/instances/index.html'

    def has_more_data(self, table):
        return self._more

    def get_data(self):
        marker = self.request.GET.get(
            project_tables.InstancesTable._meta.pagination_param, None)
        # Gather our instances
        try:
            instances, self._more = api.nova.server_list(
                self.request,
                search_opts={'marker': marker,
                             'paginate': True})
        except Exception:
            self._more = False
            instances = []
            exceptions.handle(self.request,
                              _('Unable to retrieve instances.'))

        if instances:
            try:
                api.network.servers_update_addresses(self.request, instances)
            except Exception:
                exceptions.handle(
                    self.request,
                    message=_('Unable to retrieve IP addresses from Neutron.'),
                    ignore=True)

            # Gather our flavors and images and correlate our instances to them
            try:
                flavors = api.nova.flavor_list(self.request)
            except Exception:
                flavors = []
                exceptions.handle(self.request, ignore=True)

            try:
                # TODO(gabriel): Handle pagination.
                images, more = api.glance.image_list_detailed(self.request)
            except Exception:
                images = []
                exceptions.handle(self.request, ignore=True)

            full_flavors = SortedDict([(str(flavor.id), flavor)
                                       for flavor in flavors])
            image_map = SortedDict([(str(image.id), image)
                                    for image in images])

            # Loop through instances to get flavor info.
            for instance in instances:
                if hasattr(instance, 'image'):
                    # Instance from image returns dict
                    if isinstance(instance.image, dict):
                        if instance.image.get('id') in image_map:
                            instance.image = image_map[instance.image['id']]
                    else:
                        # Instance from volume returns a string
                        instance.image = {'name':
                                instance.image if instance.image else _("-")}

                try:
                    flavor_id = instance.flavor["id"]
                    if flavor_id in full_flavors:
                        instance.full_flavor = full_flavors[flavor_id]
                    else:
                        # If the flavor_id is not in full_flavors list,
                        # get it via nova api.
                        instance.full_flavor = api.nova.flavor_get(
                            self.request, flavor_id)
                except Exception:
                    msg = _('Unable to retrieve instance size information.')
                    exceptions.handle(self.request, msg)
        return instances


class LaunchInstanceView(workflows.WorkflowView):
    workflow_class = project_workflows.LaunchInstance

    def get_initial(self):
        initial = super(LaunchInstanceView, self).get_initial()
        initial['project_id'] = self.request.user.tenant_id
        initial['user_id'] = self.request.user.id
        return initial

class ConfigurationView(forms.ModalFormView):
    '''
    Configuration view, used to configure the VNFs
    '''
    form_class = project_forms.ConfigurationForm
    form_id = "configuration_form"
    template_name = 'project/instances/configuration.html'
    success_url = reverse_lazy("horizon:project:instances:index")
    modal_id = "configuration_modal"
    context_object_name = 'configure'
    submit_label = _("Configure")
    submit_url = "horizon:project:instances:configuration"
    
    #def get_form_kwargs(self):
    #    return {"extra":['ipaddress', 'default_gw']}

    def get_initial(self):
        instance_id = self.kwargs['instance_id']
        form = project_utils.FormFields(instance_id)
        form.inizialize_form()
        description = form.get_description()
        fields = form.get_fields()
        LOG.info("fields: "+json.dumps(fields))
        return {"extra": fields , "instance_id": instance_id}

    def get_context_data(self, **kwargs):
        context = super(ConfigurationView, self).get_context_data(**kwargs)
        instance_id = self.kwargs['instance_id']
        context['instance_id'] = instance_id
        form = project_utils.FormFields(instance_id)
        form.inizialize_form()
        context['description'] = form.get_description()
        context['labels'] = form.get_paths()
        LOG.info("labels: "+str(form.get_paths()))
        context['form_fields'] = form.get_fields()
        #context['submit_url'] = reverse(self.submit_url, args=[instance_id])
        #LOG.info("submit_url: "+str(context['submit_url']))
        '''
// Handle field toggles for the Launch Instance source type field
  function update_launch_source_displayed_fields (field) {
    var $this = $(field),
      base_type = $this.val();

    $this.closest(".control-group").nextAll().hide();

    switch(base_type) {
      case "image_id":
        $("#id_image_id").closest(".control-group").show();
        break;

      case "instance_snapshot_id":
        $("#id_instance_snapshot_id").closest(".control-group").show();
        break;

      case "volume_id":
        $("#id_volume_id").closest(".control-group").show();
        break;

      case "volume_image_id":
        $("#id_image_id, #id_volume_size, #id_device_name, , #id_delete_on_terminate")
          .closest(".control-group").show();
        break;

      case "volume_snapshot_id":
        $("#id_volume_snapshot_id, #id_device_name, #id_delete_on_terminate")
          .closest(".control-group").show();
        break;
    }
  }

  $(document).on('change', '.workflow #id_source_type', function (evt) {
    update_launch_source_displayed_fields(this);
  });

  $('.workflow #id_source_type').change();
  horizon.modals.addModalInitFunction(function (modal) {
    $(modal).find("#id_source_type").change();
  });
        '''
        return context
'''
def configuration(request, instance_id):
    extra_questions = get_questions(request)
    form = project_forms.ConfigurationForm(request.POST or None, extra=extra_questions)
    if form.is_valid():
        for (question, answer) in form.extra_answers():
            LOG.info('Siamo dentro')
            pass
            #save_answer(request, question, answer)
        return redirect("create_user_success")
    redirect = reverse("horizon:project:instances:detail")
    return shortcuts.redirect(redirect)
    #return render_to_response(redirect, {'form': form})
'''

def console(request, instance_id):
    try:
        # TODO(jakedahn): clean this up once the api supports tailing.
        tail = request.GET.get('length', None)
        data = api.nova.server_console_output(request,
                                              instance_id,
                                              tail_length=tail)
    except Exception:
        data = _('Unable to get log for instance "%s".') % instance_id
        exceptions.handle(request, ignore=True)
    response = http.HttpResponse(content_type='text/plain')
    response.write(data)
    response.flush()
    return response


def vnc(request, instance_id):
    try:
        console = api.nova.server_vnc_console(request, instance_id)
        instance = api.nova.server_get(request, instance_id)
        return shortcuts.redirect(console.url +
                ("&title=%s(%s)" % (instance.name, instance_id)))
    except Exception:
        redirect = reverse("horizon:project:instances:index")
        msg = _('Unable to get VNC console for instance "%s".') % instance_id
        exceptions.handle(request, msg, redirect=redirect)


def spice(request, instance_id):
    try:
        console = api.nova.server_spice_console(request, instance_id)
        instance = api.nova.server_get(request, instance_id)
        return shortcuts.redirect(console.url +
                ("&title=%s(%s)" % (instance.name, instance_id)))
    except Exception:
        redirect = reverse("horizon:project:instances:index")
        msg = _('Unable to get SPICE console for instance "%s".') % instance_id
        exceptions.handle(request, msg, redirect=redirect)


def rdp(request, instance_id):
    try:
        console = api.nova.server_rdp_console(request, instance_id)
        instance = api.nova.server_get(request, instance_id)
        return shortcuts.redirect(console.url +
                ("&title=%s(%s)" % (instance.name, instance_id)))
    except Exception:
        redirect = reverse("horizon:project:instances:index")
        msg = _('Unable to get RDP console for instance "%s".') % instance_id
        exceptions.handle(request, msg, redirect=redirect)


class UpdateView(workflows.WorkflowView):
    workflow_class = project_workflows.UpdateInstance
    success_url = reverse_lazy("horizon:project:instances:index")

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context["instance_id"] = self.kwargs['instance_id']
        return context

    @memoized.memoized_method
    def get_object(self, *args, **kwargs):
        instance_id = self.kwargs['instance_id']
        try:
            return api.nova.server_get(self.request, instance_id)
        except Exception:
            redirect = reverse("horizon:project:instances:index")
            msg = _('Unable to retrieve instance details.')
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        initial = super(UpdateView, self).get_initial()
        initial.update({'instance_id': self.kwargs['instance_id'],
                'name': getattr(self.get_object(), 'name', '')})
        return initial


class RebuildView(forms.ModalFormView):
    form_class = project_forms.RebuildInstanceForm
    template_name = 'project/instances/rebuild.html'
    success_url = reverse_lazy('horizon:project:instances:index')

    def get_context_data(self, **kwargs):
        context = super(RebuildView, self).get_context_data(**kwargs)
        context['instance_id'] = self.kwargs['instance_id']
        context['can_set_server_password'] = api.nova.can_set_server_password()
        return context

    def get_initial(self):
        return {'instance_id': self.kwargs['instance_id']}


class DecryptPasswordView(forms.ModalFormView):
    form_class = project_forms.DecryptPasswordInstanceForm
    template_name = 'project/instances/decryptpassword.html'
    success_url = reverse_lazy('horizon:project:instances:index')

    def get_context_data(self, **kwargs):
        context = super(DecryptPasswordView, self).get_context_data(**kwargs)
        context['instance_id'] = self.kwargs['instance_id']
        context['keypair_name'] = self.kwargs['keypair_name']
        return context

    def get_initial(self):
        return {'instance_id': self.kwargs['instance_id'],
                'keypair_name': self.kwargs['keypair_name']}


class DetailView(tabs.TabView):
    tab_group_class = project_tabs.InstanceDetailTabs
    template_name = 'project/instances/detail.html'
    redirect_url = 'horizon:project:instances:index'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["instance"] = self.get_data()
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            instance_id = self.kwargs['instance_id']
            instance = api.nova.server_get(self.request, instance_id)
            instance.volumes = api.nova.instance_volumes_list(self.request,
                                                              instance_id)
            # Sort by device name
            instance.volumes.sort(key=lambda vol: vol.device)
            instance.full_flavor = api.nova.flavor_get(
                self.request, instance.flavor["id"])
            instance.security_groups = api.network.server_security_groups(
                self.request, instance_id)
        except Exception:
            redirect = reverse(self.redirect_url)
            exceptions.handle(self.request,
                              _('Unable to retrieve details for '
                                'instance "%s".') % instance_id,
                                redirect=redirect)
            # Not all exception types handled above will result in a redirect.
            # Need to raise here just in case.
            raise exceptions.Http302(redirect)
        try:
            api.network.servers_update_addresses(self.request, [instance])
        except Exception:
            exceptions.handle(
                self.request,
                _('Unable to retrieve IP addresses from Neutron for instance '
                  '"%s".') % instance_id, ignore=True)
        return instance

    def get_tabs(self, request, *args, **kwargs):
        instance = self.get_data()
        return self.tab_group_class(request, instance=instance, **kwargs)


class ResizeView(workflows.WorkflowView):
    workflow_class = project_workflows.ResizeInstance
    success_url = reverse_lazy("horizon:project:instances:index")

    def get_context_data(self, **kwargs):
        context = super(ResizeView, self).get_context_data(**kwargs)
        context["instance_id"] = self.kwargs['instance_id']
        return context

    @memoized.memoized_method
    def get_object(self, *args, **kwargs):
        instance_id = self.kwargs['instance_id']
        try:
            instance = api.nova.server_get(self.request, instance_id)
            flavor_id = instance.flavor['id']
            flavors = self.get_flavors()
            if flavor_id in flavors:
                instance.flavor_name = flavors[flavor_id].name
            else:
                flavor = api.nova.flavor_get(self.request, flavor_id)
                instance.flavor_name = flavor.name
        except Exception:
            redirect = reverse("horizon:project:instances:index")
            msg = _('Unable to retrieve instance details.')
            exceptions.handle(self.request, msg, redirect=redirect)
        return instance

    @memoized.memoized_method
    def get_flavors(self, *args, **kwargs):
        try:
            flavors = api.nova.flavor_list(self.request)
            return SortedDict((str(flavor.id), flavor) for flavor in flavors)
        except Exception:
            redirect = reverse("horizon:project:instances:index")
            exceptions.handle(self.request,
                _('Unable to retrieve flavors.'), redirect=redirect)

    def get_initial(self):
        initial = super(ResizeView, self).get_initial()
        _object = self.get_object()
        if _object:
            initial.update({'instance_id': self.kwargs['instance_id'],
                'name': getattr(_object, 'name', None),
                'old_flavor_id': _object.flavor['id'],
                'old_flavor_name': getattr(_object, 'flavor_name', ''),
                'flavors': self.get_flavors()})
        return initial
