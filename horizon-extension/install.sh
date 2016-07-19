#!/bin/sh
echo "Installing configuration dashboard..."
rm -rf /usr/share/openstack-dashboard/openstack_dashboard/dashboards/project/instances
cp -r openstack_dashboard/dashboards/project/instances/ /usr/share/openstack-dashboard/openstack_dashboard/dashboards/project/instances
service apache2 restart
python /usr/share/openstack-dashboard/manage.py compress
service apache2 restart
echo "Installation completed!"
