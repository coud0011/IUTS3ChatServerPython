import asyncio

class Server:
    def __init__(self, ip, port):
        self.ip=ip
        self.port=port
        self.server=None
        self.clients={}
        self.client_commands={'/alias':self.alias, '/list':self.clients_list, '/private':self.private_message, '/quit':self.quit}

    class Client:
        def __init__(self, alias, reader, writer):
            self.writer=writer
            self.reader=reader
            self.alias=alias

    def valid(self,alias):
        return not alias in self.clients.items()

    async def write (self, message):
        self.writer.write(message.encode())
        await self.writer.drain()

    async def register_client(self, reader, writer):
        print('New connection:')
        alias=self.reader.read()
        if self.valid(alias):
            ret=""
            for elt in self.clients.items():
                ret+=elt+" "
            self.write(f"#alias {alias}")
            self.write(f"#list {ret}{alias}")
            self.write(f"#connected {alias}")
        else:
            self.write("#error invalid_alias")


    async def handle_client(self, reader, writer):
        request = None
        client_alias=await self.register_client(reader, writer)
        while

    async def start_server(self):
        self.server = await asyncio.start_server(self.handle_client, self.ip, self.port)

    async def process_request(self, request, sender):
        #à compléter

    async def broadcast (self, message, sender=None):
        #à compléter

async def main():
    s=Server('127.0.0.1',8888)
    await s.start_server()
    async with s.server:
        await s.server.serve_forever()

asyncio.run(main())

