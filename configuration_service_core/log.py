import datetime

now = datetime.datetime.now()

file="/home/davide/Documenti/frog4-datastore/configuration_service/configuration_server/output.log2"

def print_log(line):
    #with open(file, "a") as myfile:
        #myfile.write( str(now) + ": " + line)
    try:
        myfile = open(file, "a")
        myfile.write( "\n" + now.strftime('%m/%d/%Y %H:%M:%S') + ": " + line)
        myfile.flush()
        myfile.close()
    except IOError:
        print("Could not open file!")
