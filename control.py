# -*- coding:utf8 -*-
# ! /usr/bin/env python

import top.api
import sys
import os
import re
import json
import sys
import logging
from  logging.config import logging
from  Daemon import Daemon

default_encoding = 'utf-8'

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class SmsSender:
    def __init__(self,logger):
        #logging.config.fileConfig("./logging.ini")
        self.logger = logger

    def send(self, parameter, tos):

        self.logger.info("start to send")
        try:
            with open('./cfg.json', 'r') as f:
                data = json.load(f)
            appinfo = top.appinfo(data["app.key"], data["app.secret"])
            test = top.api.AlibabaAliqinFcSmsNumSendRequest()
            test.set_app_info(appinfo)
            test.sms_type = "normal"
            test.sms_free_sign_name = data["sms.sign.name"]
            test.sms_param = json.dumps(parameter)
            test.rec_num = tos
            test.sms_template_code = data["sms.template.code"]

            res = test.getResponse()
            #self.logger.info("end to send")
            # print "sms response: " + json.dumps(res)
            self.logger.info("sms response: " + json.dumps(res))

        except Exception, e:
            # print e
            self.logger.error(e)

class HTTPHandle(BaseHTTPRequestHandler):

    def transDicts(self, params):
        dicts = {}
        if len(params) == 0:
            return
        params = params.split('&')
        for param in params:
            dicts[param.split('=')[0]] = param.split('=')[1]
        return dicts

    def do_POST(self):
        logging.config.fileConfig("./logging.ini")
        logger = logging.getLogger(__name__)
        logger.info("start to handle request")
        datas = self.rfile.read(int(self.headers['content-length']))
        # datas = urllib.unquote(datas).decode("utf-8", 'ignore')  # 指定编码方式
        logger.info("request: " + datas)
        request_data = self.transDicts(datas)
        # request_data = json.loads(datas,encoding="utf-8")
        pattern = r"(\[.*?\])";
        guid = re.findall(pattern, request_data.get("content"), re.M)
        sms_params = {}
        if (len(guid) > 2):
            sms_params["priority"] = guid[0].replace('[', '').replace(']', '')
            sms_params["status"] = guid[1].replace('[', '').replace(']', '')
            sms_params["name"] = guid[2].replace('[', '').replace(']', '')

        sms_tos = request_data.get("tos")
        # self.logger.info("sms_body: " + guid)
        logger.info("sms_tos: " + sms_tos)
        sms_sender = SmsSender(logger)
        logger.info("sms_tossss: " + sms_tos)

        sms_sender.send(sms_params, sms_tos)
        #self.send_response(200)
        self.end_headers()
        #logger.info("send successfully")

#@Deprecated
def port_to_pid(port):
    output = os.popen('lsof -i tcp:' + str(port))
    res = output.read()
    line = res.split("\n")
    if len(line) > 1:
        return line[1].split()[1]
    else:
        return 0

#@Deprecated
def kill_process(pid):
    if pid != 0:
        os.popen('kill -9 ' + pid)
    print "killed pid: " + pid

#@Deprecated
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


class HttpServerDaemon(Daemon):
    def _run(self):
        with open('./cfg.json', 'r') as f:
            data = json.load(f)
        port = data["port"];
        http_server = HTTPServer(('127.0.0.1', port), HTTPHandle)
        self.logger.info('sms provider start runing')
        http_server.serve_forever()


if __name__ == '__main__':
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    daemon = HttpServerDaemon("./var/smsprovider.pid")
    if len(sys.argv) > 1:
        action = sys.argv[1]
    else:
        action = ""

    if action == "" or action == "start":
        daemon.start()
    elif action == "stop":
        daemon.stop()
    elif action == "restart":
        daemon.restart()
    elif action == "status":
        print daemon.status()
    else:
        print "Unknown command"
        print "usage: %s start|stop|restart|status" % sys.argv[0]
        sys.exit(2)
    sys.exit(0)
