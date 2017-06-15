from datetime import datetime, timedelta
from pymongo import MongoClient, errors

class MongoQueue():

    OUTSTANDING = 1 #initial
    PROCESSING = 2  #downloading..
    COMPLETE =3    #finished

    def __init__(self, db, collection, timeout=300):
        self.client = MongoClient('localhost', 27017)

        self.Client = self.client[db]
        self.db = self.Client[collection]

        self.timeout = timeout

    def __bool__(self):

        record = self.db.find_one({'status':{'$ne':self.COMPLETE}})
        return True if record else False

    def push(self, url):  # 添加新的URL进队列
        try:
            self.db.insert({'_id': url, 'status': self.OUTSTANDING})
            print(url, "插入队列成功")
        except errors.DuplicateKeyError as e: #报错则代表已经存在于队列中
            print(url, "已经存在与队列中")
            pass

    def mypush(self, url, filename):  # 添加新的URL进队列
        try:
            self.db.insert({'_id': url, 'belongtoFile': filename,'status': self.OUTSTANDING})
            print(url, "插入队列成功")
        except errors.DuplicateKeyError as e: #报错则代表已经存在于队列中
            print(url, "已经存在与队列中")
            pass

    def push_imgurl(self, title, url):
        try:
            self.db.insert({'_id':title,'status': self.OUTSTANDING, 'url': url})
            print('图片地址插入成功')
        except errors.DuplicateKeyError as e:
            print('地址已经存在了')
            pass

    def pop(self):
        record = self.db.find_and_modify(query={'status': self.OUTSTANDING}, update={'$set':{
            'status':self.PROCESSING, 'timestamp':datetime.now()}
        })    #默认了PROCESSING一定成功? no!
        if record:
            return record['_id']
        else:
            self.repair()
            raise KeyError


    def pop_title(self, url):
        record = self.db.find_one({'_id':url})
        return record['主题']

    def pop_belongtoFile(self, url):
        record = self.db.find_one({'_id':url})
        return record['belongtoFile']

    def peek(self):
        record = self.db.find_one({'status': self.OUTSTANDING})
        if record:
            return record['_id']

    def complete(self, url):
        self.db.update({'_id': url}, {'$set':{'status': self.COMPLETE}})

    #mydefine
    def reset(self,url):
        self.db.update({'_id': url}, {'$set':{'status': self.OUTSTANDING}})

    def repair(self):
        record = self.db.find_and_modify(query={'timestamp':{'$lt':datetime.now() - timedelta(seconds=self.timeout)},
                                                'status':{'$ne':self.COMPLETE}
                                                }, update={'$set':{'status':self.OUTSTANDING}})
        if record:
            print('重置URL状态', record['_id'])

    def clear(self):
        self.db.drop()

    #pop测试 看看






