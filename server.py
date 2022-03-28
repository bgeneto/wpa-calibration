import json
import multiprocessing
import os
import time

import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import define, options

import serialworker

define("port", default=80, help="run on the given port", type=int)

clients = []

input_queue = multiprocessing.Queue()
output_queue = multiprocessing.Queue()


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        print('render html')
        self.render('index.html')


class StaticFileHandler(tornado.web.RequestHandler):
    def get(self):
        print('render js')
        self.render('websocket.js')


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


# check the queue for pending messages, and rely that to all connected clients
def checkQueue():
    if not output_queue.empty():
        message = output_queue.get()
        for c in clients:
            c.write_message(message)


if __name__ == '__main__':
    # start the serial worker in background (as a deamon)
    sp = serialworker.SerialProcess(input_queue, output_queue)
    sp.daemon = True
    sp.start()
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/", IndexHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {'path':  './'}),
            (r"/ws", WebSocketHandler)
        ]
    )
    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.listen(options.port)
    print("Listening on port:", options.port)

    mainLoop = tornado.ioloop.IOLoop().current()
    # adjust the scheduler_interval according to the frames sent by the serial port
    scheduler_interval = 10
    scheduler = tornado.ioloop.PeriodicCallback(
        checkQueue, scheduler_interval)
    scheduler.start()
    mainLoop.start()
