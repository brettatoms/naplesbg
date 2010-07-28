import fileinput
import os
import sys
import time

email = 'brettatoms@gmail.com'
accession_export = "c:\\accessions.txt"
plant_export = "c:\\plants.txt"
base_url = "http://naplesbg.appspot.com"
#base_url = "http://localhost:8080"

def upload():
    """
    Upload accession and plant data
    """
    def fix_accession_file():
        f = fileinput.input(accession_export, inplace=True)
        for line in f:
            if f.isfirstline():
                line = line.replace('#RCD', 'NUM_RCD')            
                line = line.replace('PSOURCE_ACC_#', 'PSOURCE_ACC_NUM')
                line = line.replace('RECEIVED AS', 'RECEIVED_AS')
                line = line.replace('COMMON_NAME(S)', 'COMMON_NAMES')
            sys.stdout.write(line)
        f.close()

    def fix_plant_file():
        f = fileinput.input(plant_export, inplace=True)
        for line in f:
            if f.isfirstline():
                line = line.replace('ACCESSION_#', 'ACCESSION_NUM')            
                line = line.replace('#_PL', 'NUM_PL')
            sys.stdout.write(line)
        f.close()

    # TODO: need to convert headers of converted files
    args = {'email': email, 'base_url': base_url, 'app_id': 'naplesbg'}
    cmd = 'appcfg.py --email=%(email)s upload_data --config_file=naplesbg/bulkloader.yaml --filename="%(filename)s" --kind=%(kind)s --url=%(base_url)s/remote_api naplesbg'

    fix_accession_file()
    args.update({'filename': accession_export, 'kind': 'Accession'})
    os.system(cmd % args)

    fix_plant_file()
    args.update({'filename': plant_export, 'kind': 'Plant'})
    os.system(cmd % args)

    #os.system('appcfg.py --email=%(email)s update_indexes naplesbg' % args)


def deploy():
    cmd = 'appcfg.py --email=%s update naplesbg/' % email
    os.system(cmd)


def clear_datastore():
    sys.path.append("c:/Program Files/Google/google_appengine")
    sys.path.append("c:/Program Files/Google/google_appengine/lib/yaml/lib")
    sys.path.append(os.getcwd() + '/naplesbg')

    import getpass
    from google.appengine.ext.remote_api import remote_api_stub
    from google.appengine.ext import db
    from google.appengine.ext import db
    from naplesbg.model import Accession, Plant
    
    def auth_func():
        #return raw_input('Username:'), getpass.getpass('Password:')
        return email, getpass.getpass('Password:')
    
    app_id = 'naplesbg'
    host = '%s.appspot.com' % app_id
    remote_api_stub.ConfigureRemoteDatastore(app_id, '/remote_api', auth_func, 
                                             host)

    # delete all the accessions
    print 'deleting Accessions...'
    query = Accession.all()
    while True:
        sys.stdout.write('.')
        try:
            acc = query.fetch(500)
            if not acc:
                break
            db.delete(acc)
        except:
            sys.stdout.write('*')
            pass
        time.sleep(1)

    # delete all the plants
    sys.stdout.write('\ndeleting Plants...')
    query = Plant.all()
    while True:
        sys.stdout.write('.')
        try:
            plants = query.fetch(500)
            if not plants:
                break
            db.delete(plants)
        except:
            sys.stdout.write('*')
            pass
        time.sleep(1)


usage = """setup.py <command>
  - upload: upload new data files
  - deploy: update application at appengine server
  - clear_datastore: clear the production datastore
"""

if __name__ == '__main__':
    actions = {'upload': upload,
               'deploy': deploy,
               'update': deploy,
               'clear_datastore': clear_datastore}

    if len(sys.argv) < 2 or sys.argv[1] not in actions:
        print usage
        sys.exit(1)
    
    actions[sys.argv[1]]()
