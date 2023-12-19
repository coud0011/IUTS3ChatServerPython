import asyncio


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server = None
        self.clients = {}
        self.client_commands = {'/alias': self.alias, '/list': self.clients_list, '/private': self.private_message,
                                '/quit': self.quit}

    class Client:
        def __init__(self, alias, reader, writer):
            self.writer = writer
            self.reader = reader
            self.alias = alias

    def valid(self, alias):
        return not alias in self.clients.items()

    async def write(self, message, alias):
        self.clients[alias].writer.write(message.encode())
        await self.clients[alias].writer.drain()

    async def register_client(self, reader, writer):
        print('New connection:')
        alias = await reader.read()
        if self.valid(alias):
            clt = Server.Client(alias, reader, writer)
            self.clients[alias] = clt
            ret = ""
            for elt, key in self.clients.items():
                ret += elt + " "
            await self.clients[alias].write(f"#alias {alias}")
            await self.clients[alias].write(f"#list {ret}{alias}")
            await self.clients[alias].write(f"#connected {alias}")
        else:
            await self.clients[alias].write("#error invalid_alias")

    async def handle_client(self, reader, writer):
        request = reader.read()
        client_alias = await self.register_client(reader, writer)
        while client_alias in self.clients:
            await self.process_request(request, client_alias)

    async def start_server(self):
        self.server = await asyncio.start_server(self.handle_client, self.ip, self.port)

    async def process_request(self, request, sender):
        if request.startswith("/"):
            message = request.partition(' ')
            if message[0] in self.client_commands.keys():
                self.client_commands[message[0]](message, sender)
        else:
            await self.broadcast(message=request, sender=sender)

    async def broadcast(self, message, sender=None):
        if sender is None:
            sender = ''
        for elt in self.clients.keys():
            await self.write(message, elt)

    async def alias(self, message, sender):
        await self.write("#alias "+message[2], sender.alias)
        await self.broadcast("#renamed "+sender.alias+' '+message[2], sender.alias)
        self.clients.pop(sender.alias)
        self.clients[message[2]]=sender

    async def clients_list(self, message, sender):
        await self.write(message, sender.alias)

    async def private_message(self, message, sender):
        reciev, sep, send = message[2].partition
        if reciev not in self.clients.keys():
            await self.write('#error invalid_recipient', sender.alias)


    async def quit(self, message, sender):
        pass


async def main():
    s = Server('127.0.0.1', 8888)
    await s.start_server()
    async with s.server:
        await s.server.serve_forever()


asyncio.run(main())
