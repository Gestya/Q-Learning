import threading
import asyncio
import websockets


class Server(threading.Thread):
    def __init__(self, msg_queue):
        threading.Thread.__init__(self)
        self.CLIENTS = set()
        self.msg_queue = msg_queue
        self.start_server()

        listener_thread = threading.Thread(target=self.run, args=())
        listener_thread.daemon = True
        listener_thread.start()
        print('*** Server :: ctor *** Listener thread has been run')

        asyncio.get_event_loop().run_forever()

    def start_server(self):
        print('*** Server :: start_server *** Start WebSocket Server')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ws_server = websockets.serve(self.echo, 'localhost', 8765)
        asyncio.get_event_loop().run_until_complete(ws_server)
        print('*** Server :: start_server *** Server is running')

    async def echo(self, ws, path):
        print('*** Server :: echo ***')
        print('*** Server :: echo *** : path = ', path)
        self.__register_client(ws)
        async for message in ws:
            print(f'*** Server :: echo *** : msg -> {message}')
            self.msg_queue.push_to_inbox(message)

    def run(self):
        while True:
            msg = self.msg_queue.pop_from_outbox()
            if msg:
                asyncio.run(self.__notify_clients(msg))

    def __register_client(self, ws):
        print('*** Server :: register_client ***')
        self.CLIENTS.add(ws)

    async def __notify_clients(self, message):
        print('*** Server :: notify_users ***', message)
        if self.CLIENTS:  # asyncio.wait doesn't accept an empty list
            print('*** Server :: notify_users *** sent to client(s)')
            await asyncio.wait([client.send(message) for client in self.CLIENTS])