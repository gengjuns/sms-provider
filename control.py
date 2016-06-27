# -*- coding:utf8 -*-
#! /bin/env python

import top.api
import sys
import os
import json
import sys
import logging
from  logging.config import logging
default_encoding = 'utf-8'

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class HTTPHandle(BaseHTTPRequestHandler):
    logging.config.fileConfig("./logging.ini")
    logger = logging.getLogger(__name__)
    def sendSMS(self, body, tos):
        with open('./cfg.json', 'r') as f:
            data = json.load(f)
        appinfo = top.appinfo(data["app.key"], data["app.secret"])
        test = top.api.AlibabaAliqinFcSmsNumSendRequest()
        test.set_app_info(appinfo)
        test.sms_type = "normal"
        test.sms_free_sign_name = "注册验证"
        test.sms_param = "{\"code\":\"1234\",\"product\":\""+body+"\"}"
        test.rec_num = tos
        test.sms_template_code = "SMS_5940007"
        try:
            res = test.getResponse()
            print(res)
        except Exception, e:
            print(e)

    def transDicts(params):
        dicts = {}
        if len(params) == 0:
            return
        params = params.split('&')
        for param in params:
            dicts[param.split('=')[0]] = param.split('=')[1]
        return dicts

    def do_POST(self):
        self.logger.info("start to handle request")
        datas = self.rfile.read(int(self.headers['content-length']))
        #datas = urllib.unquote(datas).decode("utf-8", 'ignore')  # 指定编码方式
        self.logger.info("request: " + datas)
        request_data = self.transDicts(datas)
        #request_data = json.loads(datas,encoding="utf-8")
        sms_body = request_data.get("content")
        sms_tos = request_data.get("tos")
        self.sendSMS(sms_body,sms_tos)
        self.send_response(200)
        self.end_headers()
        self.logger.info("send successfully")


def port_to_pid(port):
    output = os.popen('lsof -i tcp:' + str(port))
    res = output.read()
    line = res.split("\n")
    if len(line) > 1:
        return line[1].split()[1]
    else:
        return 0

def kill_process(pid):
    if pid != 0:
        os.popen('kill -9 ' + pid)
    print "killed pid: " + pid


def main(argv):
    with open('./cfg.json', 'r') as f:
        data = json.load(f)

    port = data["port"];

    if len(argv) > 1:
        action = argv[1]
    else:
        action = ""

    if action == "" or action == "start":
        pid = port_to_pid(port)
        if pid != 0:
            print "sms provider has started already, pid: " + pid
            return
        http_server = HTTPServer(('127.0.0.1', port), HTTPHandle)
        http_server.serve_forever()
    elif action == "stop":
        pid = port_to_pid(port)
        kill_process(pid)
    elif action == "restart":
        pid = port_to_pid(port)
        kill_process(pid)
        http_server = HTTPServer(('127.0.0.1', port), HTTPHandle)
        http_server.serve_forever()

if __name__ == '__main__':
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    main(sys.argv)
