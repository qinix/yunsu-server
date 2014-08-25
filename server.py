#!/usr/bin/env python

from __future__ import with_statement
import sys
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json

try:
    import gevent
    import gevent.monkey
    gevent.monkey.patch_all(dns=gevent.version_info[0] >= 1)
except ImportError:
    gevent = None
    print >>sys.stderr, 'warning: gevent not found, using threading instead'

import socket
import select
import SocketServer
import struct
import os
import logging
import getopt
import encrypt
from apscheduler.scheduler import Scheduler
import redis
from pymongo import MongoClient

sched = Scheduler()

def send_all(sock, data):
    bytes_sent = 0
    while True:
        r = sock.send(data[bytes_sent:])
        if r < 0:
            return r
        bytes_sent += r
        if bytes_sent == len(data):
            return bytes_sent


class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True


class Socks5Server(SocketServer.StreamRequestHandler):
    def handle_tcp(self, sock, remote):
        traffic = 0
        try:
            fdset = [sock, remote]
            while True:
                r, w, e = select.select(fdset, [], [])
                if sock in r:
                    data = self.decrypt(sock.recv(4096))
                    if len(data) <= 0:
                        break
                    traffic = traffic + len(data)
                    result = send_all(remote, data)
                    if result < len(data):
                        raise Exception('failed to send all data')
                if remote in r:
                    data = self.encrypt(remote.recv(4096))
                    if len(data) <= 0:
                        break
                    traffic = traffic + len(data)
                    result = send_all(sock, data)
                    if result < len(data):
                        raise Exception('failed to send all data')
        finally:
            sock.close()
            remote.close()
        return traffic

    def encrypt(self, data):
        return self.encryptor.encrypt(data)

    def decrypt(self, data):
        return self.encryptor.decrypt(data)

    def handle(self):
        try:
            self.encryptor = encrypt.Encryptor(KEY, METHOD)
            sock = self.connection
            redis_conn = redis.Redis(connection_pool=REDISPOOL)
            iv_len = self.encryptor.iv_len()
            if iv_len:
                self.decrypt(sock.recv(iv_len))
            token = self.decrypt(sock.recv(32))
            if self.auth_token(token) != True:
                send_all(sock, 'NOTRAFFIC')
                sock.close()
                return
            logging.info('token: \'%s\'' % (token))
            addrtype = ord(self.decrypt(sock.recv(1)))
            if addrtype == 1:
                addr = socket.inet_ntoa(self.decrypt(self.rfile.read(4)))
            elif addrtype == 3:
                addr = self.decrypt(
                    self.rfile.read(ord(self.decrypt(sock.recv(1)))))
            elif addrtype == 4:
                addr = socket.inet_ntop(socket.AF_INET6,
                                        self.decrypt(self.rfile.read(16)))
            else:
                # not support
                logging.warn('addr_type not support')
                return
            port = struct.unpack('>H', self.decrypt(self.rfile.read(2)))
            try:
                logging.info('connecting %s:%d' % (addr, port[0]))
                remote = socket.create_connection((addr, port[0]))
            except socket.error, e:
                # Connection refused
                logging.warn(e)
                return
            traffic = self.handle_tcp(sock, remote)
            redis_conn.incrby("yunsu:tokens:%s" % token, traffic)
        except socket.error, e:
            logging.warn(e)

    def auth_token(self, token):
        redis_conn = redis.Redis(connection_pool=REDISPOOL)
        if redis_conn.exists("yunsu:tokens:%s" % token):
            return True
        elif USERS.find_one({"token": token})["available"]:
            redis_conn.set("yunsu:tokens:%s" % token, "0")
            redis_conn.expire("yunsu:tokens:%s" % token, "7200")
            return True
        else:
            return False

@sched.interval_schedule(minutes=1)
def per_minute():
    rds = redis.Redis(connection_pool=REDISPOOL)
    for key in rds.keys('yunsu:tokens:*'):
        token = key.split(':')[2]
        ttl = rds.ttl(key) or "7200"
        traffic = rds.getset(key, "0")
        rds.expire(key, ttl)
        if traffic != "0":
            USERS.update({"token":token}, {"$inc": {"used_traffic": int(traffic)}})

def main():
    global SERVER, PORT, KEY, METHOD, USERS, REDISPOOL

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')

    config_path = 'config_server.json'
    if config_path:
        with open(config_path, 'rb') as f:
            config = json.load(f)
        logging.info('loading config from %s' % config_path)

    SERVER = '0.0.0.0'
    PORT = 8387
    KEY = 'yunsu'
    USERS = MongoClient(config['mongo'])["yunsu"]["users"]
    METHOD = config.get('method', None)
    REDISPOOL = redis.ConnectionPool()

    per_minute()
    sched.start()

    encrypt.init_table(KEY, METHOD)
    try:
        server = ThreadingTCPServer((SERVER, PORT), Socks5Server)
        logging.info("starting server at %s:%d" % tuple(server.server_address[:2]))
        server.serve_forever()
    except socket.error, e:
        logging.error(e)

if __name__ == '__main__':
    main()
