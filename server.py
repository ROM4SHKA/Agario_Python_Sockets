import socket
import random
import pygame

WIDTH_ROOM, HEIGHT_ROOM = 5000, 5000
WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW = 400, 400
FPS = 100
START_SIZE = 15
colours = {'0': (255, 255, 0), '1': (255, 0, 0), '2': (0, 255, 0),
           '3':(0, 255,255), '4': (255, 34, 178)}
class Player():
    def __init__(self, conn, addr, x, y, r, colour):
        self.conn = conn
        self.addr = addr
        self.x = x
        self.y = y
        self.r = r
        self.colour = colour

        self.errors = 0

        self.speed_x = 5
        self.speed_y = 4
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y


main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(('localhost', 10000))
main_socket.setblocking(0)
main_socket.listen(5)

sockets = []
players = []
is_server_running = True
pygame.init()
sc = pygame.display.set_mode((WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW))
pygame.display.set_caption('Agario_Server')
clock = pygame.time.Clock()
while is_server_running:
    clock.tick(FPS)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            is_server_running = False
    try:
        new_socket, address = main_socket.accept()
        print("NewPlayer", address)
        new_socket.setblocking(0)
        new_player = Player(new_socket, address,
                            random.randint(0, WIDTH_ROOM),
                            random.randint(0, HEIGHT_ROOM),
                            START_SIZE, str(random.randint(0,4)))
        players.append(new_player)
        #sockets.append(new_socket)
    except:
        print("NoAvailable")

    for p in players:
        try:
            data = p.conn.recv(1024)
            data = data.decode()
            print("Receive", data)
        except:
            pass
    # for s in sockets:
    #     try:
    #         data =  s.recv(1024)
    #         data = data.decode()
    #         print("Receive", data)
    #     except:
    #         pass
    # for s in sockets:
    #     try:
    #         s.send('New state'.encode())
    #     except:
    #         sockets.remove(s)
    #         s.close()
    for p in players:
        try:
            p.conn.send('New state'.encode())
            p.errors = 0
        except:
            p.errors += 1
    for p in players:
        if p.errors == 400:
            p.conn.close()
            players.remove(p)

    sc.fill('grey15')
    for p in players:
        x = round(p.x * WIDTH_SERVER_WINDOW / WIDTH_ROOM)
        y = round(p.y*HEIGHT_SERVER_WINDOW/ HEIGHT_ROOM)
        r = round(p.r * WIDTH_SERVER_WINDOW / WIDTH_ROOM)

        pygame.draw.circle(sc, colours[p.colour], (x, y), r)
    pygame.display.update()


pygame.quit()
main_socket.close()