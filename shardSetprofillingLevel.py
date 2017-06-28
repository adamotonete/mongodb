# -*- encoding: utf-8 -*-

import argparse
from pymongo import MongoClient

parser = argparse.ArgumentParser()

parser.add_argument("--database", "-d", type=str, required=False, default='test')
parser.add_argument("--username", "-u", type=str, required=False, default='')
parser.add_argument("--password", "-p", type=str, required=False, default='')
parser.add_argument("--host", "-host", type=str, required=False, default='localhost:27017')
parser.add_argument("--apply", "-apply", type=str, required=False, default=False)
parser.add_argument("--authenticationDatabase", "-authDB", type=str, required=False, default='admin')
parser.add_argument("--level", "-l", type=int, required=False, default=1)
parser.add_argument("--slowms", "-s", type=int, required=False, default=100)
args = parser.parse_args()

def checkShard (hostname, username, password, database, profiler, slowms):

    serverlist = []

    print 'Checking if host targed is a mongos or mongod ...'

    c = MongoClient(hostname, serverSelectionTimeoutMS=1000)
    if password <> '':
        db = c.get_database(str(args.authenticationDatabase))
        db.authenticate(username,password)
    db = c.get_database('admin')

    try:
        shards = db.command({'listShards': 1})
        #getting first and second replica node from each shard.
        for shard in shards['shards']:
            a = shard['host']
            server1 = a.split('/')[1].split(',')[0] # at least one server
            try:
                server2 = a.split('/')[1].split(',')[1] # we are using only the first connection here.
            except:
                server2 = None
            serverlist.append([server1, server2])
    except:
        shard = None
    if shard:
        print 'Shard found!\n'
        print 'Connecting to the replicasets:'
        for server in serverlist:
            checkReplicaset(hostname=server[0], username=username, password=password, database=database,
                            profiler=profiler, slowms=slowms)
    else:
        checkReplicaset(hostname=hostname,username=username, password=password, database=database, profiler=profiler, slowms=slowms)

def checkReplicaset (hostname, username, password, database, profiler, slowms):

    c = MongoClient(hostname, serverSelectionTimeoutMS=1000)
    if password <> '':
        db = c.get_database(args.authenticationDatabase)
        db.authenticate(username, password)
    db = c.get_database('local')

    replset = db.system.replset.find_one()

    if replset is None:
        print """This tool is designed to work only with shards and replicaset, for single instances please check:
    https://docs.mongodb.com/manual/tutorial/manage-the-database-profiler/"""
    else:
        print '\nReplicaset "%s" has been found, checking connection on all hosts:' % (str(replset['_id']))
        print 'Visible members:'
        for memb in replset['members']:
            if memb['hidden'] is False:
                print '  ' + str(memb['host']) + '  db : ' + database + getProfilingStatus(host=str(memb['host']), username=username, password=password,
                                                                    apply_changes=False, database=database, profile='', slowms='')
        if args.apply:

            if profiler == 2:
                print '\n------ changing profiler to {profiler : %s} on the following servers ------\n' % (profiler)
            else:
                print '\n------ changing profiler to {profiler : %s, slowms : %s} on the following servers ------\n' % (profiler, slowms)

            for memb in replset['members']:
                print 'Applying changes on %s ... ' % str(memb['host'])
                setProfilingStatus(host=str(memb['host']), username=username, password=password,
                                       apply_changes=True, database=database, profile=profiler, slowms=slowms)
            print '\nDone!'

def getProfilingStatus(host, username, password, database, apply_changes, profile, slowms):
    try:
        conn = MongoClient([host], serverSelectionTimeoutMS=500)
        if password <> '':
            db = conn.get_database(str(args.authenticationDatabase))
            db.authenticate(username, password)
        db2 = conn.get_database(str(database))
        db2.slave_ok
        if not apply_changes:
            current_status = db2.command({'profile': -1})
            return ' -> {profiler: ' + str(current_status['was']) + ', slowms: ' + str(current_status['slowms']) + '}'
        else:
            if profile == 2:
                return db2.command({'profile': profile})
            else:
                return db2.command({'profile': profile, 'slowms': slowms})
    except:
         print 'Unable to connect to %s, please check connection between this box and targert' % host


def setProfilingStatus(host, username, password, database, apply_changes, profile, slowms):
    getProfilingStatus(host, username, password, database, True, profile, slowms)


if int(args.level) not in [-1,0,1,2]:
    print 'Error, please use a valid profiler value [0-2]'
    exit(0)

checkShard(args.host,args.username, args.password,args.database, args.level, args.slowms)

