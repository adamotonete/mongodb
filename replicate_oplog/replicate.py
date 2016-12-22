import os
import time
import pymongo
import logging
import bson
#import dateparser
import datetime

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from pymongo.errors import AutoReconnect


class Replicator:

    def __init__(self):

        self.logger = None
        self.logger = self.get_logger()
        
        self.origin_dump_dir=''
        self.origin_dump_oplog='%s/oplog.bson' % self.origin_dump_dir
        self.origin_host='localhost'
        self.origin_port=27017
        self.origin_replset=''

        self.dest_host='localhost'
        self.dest_port=27017
        self.dest_replset=''

        self.connections = {}
        self.last_dump_ts = None

        self.lockfile ='/home/percona/oplog.history' 

    def getLastTimestampSaved(self):

        last_ts = open(self.lockfile, 'r').read()
        last_seq = last_ts.strip()[21::].replace(')','').strip()
        last_ts = last_ts.strip()[10:20]

        valid_ts = self.getTimestampIsValidOrNew(last_ts)
        print last_seq
       
        last_ts_save = bson.timestamp.Timestamp(int(valid_ts), int(last_seq))

        return last_ts_save


    def getTimestampIsValidOrNew(self,test_ts):
        try:
            datetime.datetime.fromtimestamp(int(test_ts))
            return test_ts
        except:
            print 'error'
            return time.mktime(datetime.datetime(2016, 1, 1).timetuple())

    def get_logger(self):
        try:
            logging.basicConfig(
                level=logging.DEBUG,
                format='[%(asctime)s] [%(levelname)s] [%(processName)s] [%(module)s:%(funcName)s:%(lineno)d] %(message)s')
            return logging.getLogger(__name__)
        except Exception, e:
            print 'Problem setting up logger! Error: %s' % e
            exit(1)
    def do_mongorestore(self):
        try:
            self.logger.info('Importing dump of origin into destination: "%s:%i"' % (self.dest_host, self.dest_port))
            os_cmd='mongorestore --drop --oplogReplay --host %s/%s:%i --dir %s' % (self.dest_replset, self.dest_host, self.dest_port, self.origin_dump_dir)
            self.logger.debug('Running restore command: "%s"' % os_cmd)
            os.system(os_cmd)
        except Exception, e:
            self.logger.fatal('Failed to restore mongodump to destination! Error: "%s"' % e)
            exit(1)

    def get_connection(self, name, replset, host, port, force=False):
        try:
            self.logger.info('Getting connection to %s: "%s/%s:%i"' % (name, replset, host, port))
            if force or not name in self.connections:
                self.connections[name] = pymongo.MongoClient(
                    host='%s:%i' % (host, port),
                    replicaSet=replset,
                    readPreference='primary')
                self.logger.debug('Got connection to %s' % name)
            return self.connections[name]
        except Exception, e:
            self.logger.fatal('Unable to connect to the %s replicaset! Error: "%s"' % (name, e))
            exit(1)

    def last_oplog_timestamp(self):
        oplog = None
        try:
            if os.path.isfile(self.lockfile): #Im firs looking for the .lock file
                self.logger.info('Getting last bson-timestamp from previous oplog history file: "%s"' % self.lockfile)
                oplog = self.getLastTimestampSaved()
                self.last_dump_ts = oplog
            elif os.path.isfile(self.origin_dump_oplog):
                self.logger.info('Getting last bson-timestamp from oplog file: "%s"' % self.origin_dump_oplog)
                oplog = open(self.origin_dump_oplog)
                for change in bson.decode_file_iter(oplog):
                    self.last_dump_ts = change['ts']
                oplog.close()
            else:
                raise Exception, 'Could not find an oplog.bson or history file: "%s"!' % self.origin_dump_oplog, None
        except Exception, e:
            self.logger.fatal('Failed to restore mongodump to destination! Error: "%s"' % e)
            if oplog:
                oplog.close()
            exit(1)

        if self.last_dump_ts:
            self.logger.info('Last change ts: %s' % self.last_dump_ts)
            return self.last_dump_ts
        else:
            self.logger.fatal('Could not find starting timestamp for source oplog tailing! This means the backup contains zero oplog changes.')
            exit(1)

    def replicate(self, restore_database):
        origin = self.get_connection('origin', self.origin_replset, self.origin_host, self.origin_port)
        destination = self.get_connection('dest', self.dest_replset, self.dest_host, self.dest_port)
        if restore_database: 
            self.do_mongorestore()
        try:
            self.logger.info('Getting tailable-cursor on origin oplog')
            oplog = origin.local.oplog.rs
            last_oplog_ts = self.last_oplog_timestamp()
            cursor = oplog.find({'ts': {'$gt': last_oplog_ts}}, {"h" :0},
                                cursor_type=pymongo.CursorType.TAILABLE_AWAIT,
                                oplog_replay=True)
            self.logger.info('Got tailable-cursor on origin oplog. Docs to replay: %i' % cursor.count())
        except Exception, e:
            self.logger.fatal('Unable to get tailable-cursor on origin oplog! Error: "%s"' % e)
            exit(1)

        last_ts = None


        while cursor.alive:
            try:
                op = cursor.next()
                if last_ts != op['ts']:
                    print op['ts']

                    namespace = op['ns'].split('.')
                    database = namespace[0]
                    collection = list(namespace)
                    collection.remove(database)
                    collection = '.'.join(collection)

                    obj = op['o']

                    db2 = destination.get_database(database)

                    if op['op'] == 'i':
                        if (collection == 'system'):
                            print (obj)
                            db2.get_collection('system.indexes').insert(obj)
                            print 'Creating index..'
                        else:
        		    try:
                                #print 'inserting'  + obj
	       	                db2.get_collection(collection).save(obj)
	                    except:
				print '###### ERROR . in object ' + collection
                    if op['op'] == 'u':
                        print op['o2']
			where = op['o2']                      
                        try:
                            db2.get_collection(collection).update(where, obj)
                            #print('-> Update: ' + str(where['_id']))			
			except:
			    print('Failed to UPDATE')
                    if op['op'] == 'd':
                        db2.get_collection(collection).remove(obj)
                        #print('-> Delete: ' + str(obj['_id']) )
                    last_ts = op['ts']
                    print last_ts
                    oplogfile = open(self.lockfile, 'w')
                    oplogfile.truncate()
                    oplogfile.write(str(last_ts))
                    oplogfile.close()
            except (AutoReconnect, StopIteration):
                time.sleep(1)


if __name__ == "__main__":
    replicator = Replicator()
    replicator.replicate(False)


