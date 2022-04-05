#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""World Pendulum Alliance tides experiment (post processing).
This script reads and process the outputed data (csv files) generated
by the tides.py (unattended) script in order to calculate the average
pendulum period, corrected gravitational acceleration etc.
Author:   b g e n e t o @ g m a i l . c o m
History:  v1.0.0  Initial release
          v1.0.1  Configure options via config (ini) file
          v1.0.2  Using Bootstrap 5 theme
"""

import json
import multiprocessing
import os
import socket
import sys
import time
from configparser import ConfigParser

import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

import serialworker

__author__ = "Bernhard Enders"
__maintainer__ = "Bernhard Enders"
__email__ = "b g e n e t o @ g m a i l d o t c o m"
__copyright__ = "Copyright 2022, Bernhard Enders"
__license__ = "GPL"
__status__ = "Development"
__version__ = "1.0.2"
__date__ = "20220331"


clients = []

input_queue = multiprocessing.Queue()
output_queue = multiprocessing.Queue()


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class CalHandler(tornado.web.RequestHandler):
    def get(self):
        id = str(self.get_arguments("id")[0])
        self.render('cal%s.html'%id)

#class StaticFileHandler(tornado.web.RequestHandler):
#    def get(self):
#        self.render('websocket.js')


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print('DEBUG: new ws connection request')
        clients.append(self)
        self.write_message("..:: Serial device connected ::..")

    def on_message(self, message):
        print('DEBUG: tornado received from client: %s' % json.dumps(message))
        # self.write_message('ack')
        input_queue.put(message)

    def on_close(self):
        print('DEBUG: ws connection closed')
        clients.remove(self)

    async def aclose(self):
        self.close()
        await self._closed.wait()
        return self.close_code, self.close_reason


# check the queue for pending messages, and rely that to all connected clients
def check_queue():
    if not output_queue.empty():
        message = output_queue.get()
        for c in clients:
            c.write_message(message)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()

    return ip


def ini_config():
    '''
    Creates an initial config file with default values
    '''
    config = ConfigParser()
    config.add_section("config")
    config.set("config", "serial_port", "/dev/ttyS0")
    config.set("config", "baud_rate", "115200")
    config.set("config", "timeout", "1")
    config.set("config", "web_port", "8080")
    config.set("config", "web_ip", get_ip())

    with open(cfg_file, "w") as config_file:
        try:
            config.write(config_file)
        except Exception as e:
            print("Error creating initial config file. Check permissions.")


def get_config():
    '''
    Returns the config object
    '''
    if not os.path.isfile(cfg_file):
        ini_config()

    config = ConfigParser()

    try:
        config.read(cfg_file)
    except Exception as e:
        print(str(e))
        os._exit(os.EX_CONFIG)

    return config


def get_setting(section, setting):
    '''
    Return a setting value
    '''
    config = get_config()
    try:
        value = config.get(section, setting)
    except Exception as e:
        print(str(e))
        os._exit(os.EX_CONFIG)

    return value


def setup_ws(web_ip, web_port):
    # template and js files
    ws_template = os.path.join(
        script_dir, "static", "js", "websocket.template")
    ws_file = os.path.join(script_dir, "static", "js", "websocket.js")

    # check if websocket template file (provided) exists
    if not os.path.isfile(ws_template):
        print('FATAL: template file not found')
        os._exit(os.EX_CONFIG)

    # always write a new websocket javascript file based on ini settings
    with open(ws_template, 'r') as tf:
        data = tf.read()

    # user defined ip and port
    data = data.replace('<web_ip>', web_ip).replace(
        '<web_port>', str(web_port))

    # write up-to-date js file
    with open(ws_file, 'w') as js:
        js.write(data)


if __name__ == '__main__':
    # get user settings
    script_dir = os.path.dirname(sys.argv[0])
    if not len(script_dir):
        script_dir = '.' + os.sep
    cfg_file = os.path.join(script_dir, "config.ini")
    serial_port = get_setting("config", "serial_port")
    baud_rate = int(get_setting("config", "baud_rate"))
    timeout = int(get_setting("config", "timeout"))
    web_port = int(get_setting("config", "web_port"))
    web_ip = get_setting("config", "web_ip")

    # setup websockets with ip and port
    setup_ws(web_ip, web_port)

    # start the serial worker in background (as a deamon)
    sp = serialworker.SerialProcess(
        input_queue, output_queue, serial_port, baud_rate, timeout)
    sp.daemon = True
    sp.start()
    # tornado.options.parse_command_line()
    handlers = [
        (r"/", IndexHandler),
        (r"/cal", CalHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler,
         {'path':  './static'}),
        (r"/ws", WebSocketHandler)
    ]
    app = tornado.web.Application(
        handlers=handlers
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(web_port)
    print("INFO: Web server listening on {}:{}".format(web_ip, web_port))

    main_loop = tornado.ioloop.IOLoop().current()
    # adjust the scheduler_interval according to the frames sent by the serial port
    scheduler_interval = 100
    scheduler = tornado.ioloop.PeriodicCallback(
        check_queue, scheduler_interval)
    try:
        scheduler.start()
        main_loop.start()
    except:
        pass
    finally:
        input_queue.close()
        output_queue.close()
        sp.terminate()
        sp.join()
        scheduler.stop()
        http_server.stop()
        #for handler in handlers:
        #    handler.aclose()
        print('\nINFO: Web server stopped')
