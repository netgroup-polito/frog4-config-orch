#!/usr/bin/env python
import sys
from django.core.management import execute_from_command_line
from configuration_service_core import messaging
from threading import Thread
import os
version = '1.0'


if __name__ == "__main__":

    if sys.argv[1] == "runserver":
        import logging
        from configparser import SafeConfigParser

        i = 1
        confFile = None
        for param in sys.argv:
            if param == "--d":
                if len(sys.argv) > i:
                    confFile = sys.argv[i]
                    break
                else:
                    print ("Wrong params usage --d [conf-file]")
                    os.exit(1)
            i = i + 1
        parser = SafeConfigParser()
        if confFile is not None:
            parser.read(confFile)
        else:
            confFile = "config/default-config.ini"
            parser.read(confFile)
        os.environ.setdefault("CONFIGURATION_SERVICE_CONFIG_FILE", confFile)
        logging.basicConfig(filename=parser.get('logging', 'filename'), format='%(asctime)s %(levelname)s:%(message)s',
                            level=parser.get('logging', 'level'))
        addr = parser.get('rest_server', 'address')
        port = parser.get('rest_server', 'port')
        params = []
        params.append(sys.argv[0])
        params.append(sys.argv[1])
        params.append(addr + ":" + str(port))
        '''
        django generate two threads executing manage.py in order to manage reload, --noreload avoid the creation of the second thread
        so that the message bus singleton object is created only one time
        '''
        params.append("--noreload")

        logging.info('Running \'Configuration service\' with version %s', version)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_config.settings")
        worker = Thread(target=messaging.MessageBus)
        worker.start()
        execute_from_command_line(params)

    else:
        os.environ.setdefault("CONFIGURATION_SERVICE_CONFIG_FILE", "config.default-config.ini")
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_config.settings")
        execute_from_command_line(sys.argv)
