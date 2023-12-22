import asyncio


def clear(alias):
    alias, r, t = alias.partition("\n")
    return alias


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

        async def write(self, message):
            self.writer.write(message.encode())
            await self.writer.drain()

    def valid(self, alias):
        return not alias in self.clients.items()

    async def broadcast(self, message, sender=None, returning=False):
        if sender is None:
            sender = ''
        for elt in self.clients:
            print(returning, sender.alias, elt, not (returning and sender == elt))
            if not (returning and sender == elt):
                await self.clients[elt].write(message)

    async def register_client(self, reader, writer):
        print('New connection:')
        alias = (await reader.readline()).decode()
        alias = clear(alias)
        print(alias)
        if self.valid(alias):
            clt = Server.Client(alias, reader, writer)
            self.clients[alias] = clt
            await clt.write(f"#alias {alias}\n")
            await asyncio.sleep(0.01)
            await self.clients_list(clt)
            await asyncio.sleep(0.01)
            await self.broadcast(f"#connected {alias}\n", clt, True)
            print('fin connection')
        else:
            await self.clients[alias].write("#error invalid_alias\n")

    async def handle_client(self, reader, writer):
        client_alias = await self.register_client(reader, writer)
        while client_alias in self.clients:
            print('début boucle')
            request = (await reader.readline()).decode()
            print(request)
            await self.process_request(request, client_alias)

    async def start_server(self):
        self.server = await asyncio.start_server(self.handle_client, self.ip, self.port)

    async def process_request(self, request, sender):
        if request.startswith("/"):
            message = request.partition(' ')
            if message[0] in self.client_commands.keys():
                self.client_commands[message[0]](message, sender)
            else:
                await sender.write('#error invalid_command\n')
        else:
            await self.broadcast(message=request, sender=sender)

    async def alias(self, message, sender):
        await sender.write("#alias " + message[2] + '\n')
        await self.broadcast("#renamed " + sender.alias + ' ' + message[2] + '\n', sender.alias)
        self.clients.pop(sender.alias)
        self.clients[message[2]] = sender

    async def clients_list(self, sender):
        ret = ""
        print(self.clients)
        for elt in self.clients:
            print(elt)
            ret += elt + " "
        await sender.write('#list ' + ret + '\n')

    async def private_message(self, message, sender):
        reciev, sep, send = message[2].partition
        if reciev not in self.clients.keys():
            await sender.write('#error invalid_recipient\n')
        elif send == '' or send is None:
            await sender.write('#error missing_argument\n')
        else:
            await sender.write(reciev)

    async def quit(self, message, sender):
        sender.writer.close()
        sender.reader.close()
        self.clients.pop(sender.alias)
        await self.broadcast(message, sender)


async def main():
    s = Server('127.0.0.1', 8888)
    await s.start_server()
    async with s.server:
        await s.server.serve_forever()
        print(s.clients)


asyncio.run(main())
