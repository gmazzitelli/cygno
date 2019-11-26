#!/usr/bin/env python2
#
# G. Mazzitelli and I. Abritta Febraury 2019
# Tool to Upload/Download Files into/from the Swift Cloud
#
import re
import sys
import os

import numpy as np
import commands
import time
import datetime
import platform

def mv_file(filein, fileout):
    command = '/bin/mv ' + filein + ' ' + fileout
    return os.system(command)

def mk_dir(filedir):
    command = '/bin/mkdir -p ' + filedir
    return os.system(command)

def mk_symlink(folderdir,filedir):
    command = '/bin/ln -s ' + folderdir + ' ' + filedir
    return os.system(command)

def rm_symlink(filedir):
    if platform.system() == 'Darwin':
        command = '/bin/unlink '+ filedir
    else:
        command = '/usr/bin/unlink '+ filedir
    return os.system(command)

def rm_dir(filein):
    command = '/bin/rm -r ' + filein
    return os.system(command)

def cp_file(filein, fileout):
    command = '/bin/cp '+ filein + ' ' + fileout
    return os.system(command)

def rm_file(filein):
    command = '/bin/rm ' + filein
    return os.system(command)

def get_pwd():
    command = '/bin/pwd'
    status, output = commands.getstatusoutput(command)
    return output

def get_file(DIRTAG,NAME):
    cloud = 'https://swift.cloud.infn.it:8080/v1/AUTH_1e60fe39fba04701aa5ffc0b97871ed8/Cygnus'
    command = '/usr/bin/wget ' + cloud + '/' + DIRTAG + '/' + NAME
    return os.system(command)

def grep_file(what, filein):
    command = '/usr/bin/grep ' + what + ' ' + filein
    status, output = commands.getstatusoutput(command)
    return output

def append2file(line, filein):
    command = 'echo '+ line + ' >> '+filein
    return os.system(command)

def swift_auth():
    # https://docs.openstack.org/python-swiftclient/latest/service-api.html
    # https://docs.openstack.org/python-swiftclient/

    import swiftclient
    from keystoneauth1 import session
    from keystoneauth1.identity import v3

    
    # Read Write account
    OS_REGION_NAME='lnf'
    OS_USER_DOMAIN_NAME='default'
    OS_PROJECT_DOMAIN_NAME='default'
    OS_PROJECT_NAME='cygnus-default'
    OS_IDENTITY_API_VERSION='3'
    OS_PASSWORD='bayRonPeOcan9Quiufvecfevesyailb7'
    OS_AUTH_TYPE='password'
    OS_AUTH_STRATEGY='keystone'
    OS_AUTH_URL='https://keystone.cloud.infn.it:5000/v3/'
    OS_USERNAME='cygnus'
    OS_STORAGE_URL='https://swift.cloud.infn.it:8080/v1/AUTH_1e60fe39fba04701aa5ffc0b97871ed8'

    _auth = v3.Password(
        user_domain_name    = OS_USER_DOMAIN_NAME,
        project_domain_name = OS_PROJECT_DOMAIN_NAME,
        project_name        = OS_PROJECT_NAME,
        username            = OS_USERNAME,
        password            = OS_PASSWORD,
        auth_url            = OS_AUTH_URL
    )
    _os_options={
        'region_name' : OS_REGION_NAME, 
        'object_storage_url': OS_STORAGE_URL
    }
    # Create session
    keystone_session = session.Session(auth = _auth)

    # Create swiftclient Connection
    swift = swiftclient.Connection(session      = keystone_session, 
                                    auth_version = OS_IDENTITY_API_VERSION,
                                    os_options   = _os_options
                                    )
    return swift

def swift_put(file_name):
    container_name = 'Cygnus'
    with open(file_name, 'rb') as data:
        swift = swift_auth()
        swift.put_object(container_name, file_name, data)
    return 
                
            
if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='cygno_repo.py [OPTION1,..,OPTIONN]\n\nP.S. To guarantee the correct working of this code, it should be placed in the same folder where the data is or will be. \n\nExample of use:\n\t [upload]    cygno_repo.py -d Data -t LAB -f put -n histograms_Run0000X.root \n\t [download]  cygno_repo.py -d Data -t LAB -f get -n histograms_Run0000X.root \n\n Swift Storage:\n The Swift Storage is set to store four different kind of data as explained below:\n\t-Data: where the experimental data should be stored and have being divided in four sub directories: \n\t\t-LAB: Data taken at Frascati with LEMON;\n\t\t-LTD: Long-Term Data taken at Frascati;\n\t\t-FNG: Data taken with the Frascati Neutron Generator;\n\t\t-MAN: Data taken at Frascati with MANGO;\n\t-Simulation: where the Monte Carlo simulated data should be stored;\n\t-Reconstruction: where the reco files should be stored;\n\t-Analysis: where codes can be stored.')
    parser.add_option('-d','--dest', dest='dest', type="string", default='Data', help='Directory where the data will be stored on the Swift Cloud;');
    parser.add_option('-t','--tag', dest='tag', type='string', default='', help='Sub directory where the data will be stored on the Swift Cloud;');
    parser.add_option('-f','--function', dest='function', type='string', default='put', help='put/get file on the Swift Cloud;');
    parser.add_option('-n','--name', dest='filename', type='string', default='', help='Filename [get] or path/filename[put] to the desired file.');
    #parser.add_option('-h', '--help', help='Show this help message');
    (options, args) = parser.parse_args()

    if (options.filename == '') or (options.dest == ''):
        print('Filename/Directory is necessary to run this script')
        exit()
    else:
        if options.function == 'put':
            pwddir  = get_pwd()
            print(pwddir)
            if options.tag == '':
                FILEDIR = pwddir + '/' + options.dest
                FILEDIRCL = options.dest
            else:
                FILEDIR = pwddir + '/' + options.dest + '/' + options.tag
                FILEDIRCL = options.dest + '/' + options.tag
            FILE = options.filename
    
            FILENAME = FILE.split('/')[-1]
            DIRS = FILE.split('/')
            DIR = pwddir + '/'
            for i in range(0,len(DIRS)-1):
                if i > 0:
                    DIR = DIR + '/' + DIRS[i]
                else:
                    DIR = DIR + DIRS[i]
            
    
            print("Cloud dir: " + FILEDIR)
            print("Name of the file: " + FILENAME)    
            print("File directory: " + DIR)
            print('Preparing to upload file into the Cloud')
            
            if options.tag == '':
                mk_symlink(DIR,FILEDIR)
            else:
                mk_dir(options.dest)
                mk_symlink(DIR+'/',FILEDIR)
                
            print ("Starting pushing on swift: ", FILENAME)
            swift_put(FILEDIRCL + '/'+ FILENAME)
            print ("Pushed: ", FILEDIRCL + '/'+ FILENAME)
    
            rm_symlink(FILEDIR)
            if options.tag != '':
                rm_dir(pwddir + '/' + options.dest)
        else:
            print('Preparing to download file from the Cloud')
            
            if options.tag == '':
                FILEDIR = options.dest
            else:
                FILEDIR = options.dest + '/' + options.tag
            FILE = options.filename
            get_file(FILEDIR,FILE)
