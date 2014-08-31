#!/usr/bin/python
import time
import sys
from elasticsearch import Elasticsearch
from datetime import datetime
from pymongo import MongoClient

START = 85255
es = Elasticsearch()
client = MongoClient('mongodb://localhost:27017/')


def index(index_name):
    db = client['v2ex']['topic'] 
    cursor = db.find({"_id":{"$lt":START}}).sort([('_id',-1)]).batch_size(10)
    for item in cursor:
        item['created'] = item['created'] * 1000
        item['last_modified'] = item['last_modified'] * 1000
        item['last_touched'] = item['last_touched'] * 1000
        item['rcontent'] = get_replies(item['_id'])
        try:
            a = time.time()
            es.index(index=index_name, doc_type="topic", id=item['_id'], body=item)
            b = time.time()

        except Exception, e:
            print(e)
            time.sleep(5)
            continue
       
        info = "cost %d ms indexed\n"%((b-a)*1000)
        print(info)


def get_replies(topic_id):

    """
        return replies like:
            'username created content  [username created content ...]'
    """

    rcontent = u""
    db = client['v2ex']['reply']
    a = time.time()
    for r in db.find({"topic_id":topic_id}):
        rcontent += r['member']['username']     
        rcontent += " " + datetime.fromtimestamp(r['created']).strftime('%Y-%m-%d')
        rcontent += " " + r['content'] + "    "
    b=time.time()
    print("cost %d ms to find the [%d]."%((b-a)*1000, topic_id))
    return rcontent


if __name__ == '__main__':
    index(sys.argv[1])
