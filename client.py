#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
import logging
import struct


log = logging.getLogger(__name__)


class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, master, message=None):
        self.master = master
        self.message = message

    def connection_made(self, transport):
        self.master.connected = True
        self.master.send(transport)
        if self.message:
            transport.write(self.message)
            log.info('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        log.info('Data received: {!r}'.format(data))

    def connection_lost(self, exc):
        self.master.connected = None
        log.info('The server closed the connection')



class DnsClient:

    def __init__(self, host, port, loop):
        self.host = host
        self.port = port
        self.loop = loop or asyncio.get_event_loop()

        self.connected = None
        self.transport = None

        self.loop.create_task(self._do_connect())

    async def _do_connect(self):
        while True:
            await asyncio.sleep(1)
            if self.connected:
                continue
            try:
                transport, protocol = await self.loop.create_connection(
                    lambda: EchoClientProtocol(self),
                    self.host,
                    self.port)
                log.info('Connection create on {}'.format(transport))
            except OSError:
                log.error('Server not up retrying in 5 seconds...')
            except Exception as e:
                log.error('Error when connect to server: {}'.format(e))

    def start(self):
        self._auto_loop()

    def _auto_loop(self):
        message = [b'\xff\xf4\x00\x10\x40\x40\x84']
        if self.transport:
            import random
            msg = random.choice(message)
            self.transport.write(msg)
            log.info('Data sent: {!r}'.format(msg))
        self.loop.call_later(20, self._auto_loop)

    def send(self, transport):
        self.transport = transport


if __name__ == "__main__":
    log = logging.getLogger("")
    formatter = logging.Formatter("%(asctime)s %(levelname)s " +
                                  "[%(module)s:%(lineno)d] %(message)s")
    # log the things
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(formatter)
    log.addHandler(ch)

    loop = asyncio.get_event_loop()

    dns = DnsClient('192.168.1.222', 4001, loop)
    dns.start()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
