from config_orch_core.model.vnf import VNF
import fileinput

database = "my_db.txt"

class VnfRepo():

    def clean_db(self):
        open(database, 'w').close()

    def is_vnf_started(self, vnf):
        try:
            rows = self._read_file()
            for row in rows:
                tmp = row.split('#')
                triple = tmp[0].split(':')
                current_vnf = VNF(triple[0], triple[1], triple[2])
                if vnf.__eq__(current_vnf):
                    return True
            return False
        except IOError:
            raise IOError

    def get_started_vnf(self):
        try:
            rows = self._read_file()
            started_vnf = []
            for row in rows:
                tmp = row.split('#')
                triple = tmp[0].split(':')
                if len(tmp) == 2:
                    address = tmp[1]
                else:
                    address = None
                vnf = VNF(triple[0], triple[1], triple[2], address)
                started_vnf.append(vnf)
            return started_vnf
        except IOError:
            raise IOError

    def save_started_vnf(self, vnf):
        try:
            with open(database, 'a') as my_db:
                line = vnf.tenant_id+':'+vnf.graph_id+':'+vnf.vnf_id
                my_db.write(line+'\n')
            my_db.close()
        except Exception as e:
            raise IOError("Error during writing of my_db. File: " + database + " \n" + str(e))

    def save_management_address(self, vnf, address):
        try:
            for line in fileinput.input(database, inplace=1):
                old_row = vnf.tenant_id+':'+vnf.graph_id+':'+vnf.vnf_id
                new_row = vnf.tenant_id+':'+vnf.graph_id+':'+vnf.vnf_id+'#'+address
                print(line.replace(old_row, new_row))
        except Exception:
            raise Exception

    def get_management_address(self, vnf):
        try:
            rows = self._read_file()
            for row in rows:
                tmp = row.split('#')
                triple = tmp[0].split(':')
                current_vnf = VNF(triple[0], triple[1], triple[2])
                if current_vnf.__eq__(vnf):
                    if len(tmp) == 2:
                        address = tmp[1]
                        return address
                    else:
                        return None
        except IOError:
            raise IOError

    def _read_file(self):
        try:
            with open(database, 'r') as my_db:
                rows = my_db.readlines()
                lines = []
                for row in rows:
                    row = row.strip()
                    if not row.__eq__(''):
                        lines.append(row)
            my_db.close()
            return lines
        except Exception as e:
            raise IOError("Error during reading of my_db. File: " + database + " \n" + str(e))

