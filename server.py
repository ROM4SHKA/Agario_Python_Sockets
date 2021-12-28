
import socket
import random
import pygame

WIDTH_ROOM, HEIGHT_ROOM = 5000, 5000
WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW = 300, 300
FPS = 100
START_SIZE = 50
FOOD_SIZE = 15
FOODS_AMOUNT = (WIDTH_ROOM * HEIGHT_ROOM) // 70000
colours = {'0': (255, 255, 0), '1': (255, 0, 0), '2': (0, 255, 0),
           '3':(0, 255,255), '4': (255, 34, 178)}

def new_r(R,r):
    return (R**2 + r**2)**0.5
def find(strn):
    first_o = None
    for i in range(len(strn)):
        if strn[i]=='<':
            first_o =i
        if strn[i] =='>' and first_o !=None:
            close = i
            res = strn[first_o+1: close]
            res = list(map(int, res.split(',')))
            return res
    return  ''

class Food():
    def __init__(self, x,y,r, c):
        self.x = x
        self.y = y
        self.r = r
        self.colour = c

class Player():
    def __init__(self, conn, addr, x, y, r, colour):
        self.conn = conn
        self.addr = addr
        self.x = x
        self.y = y
        self.r = r
        self.colour = colour
        self.w_vision = 1000
        self.h_vision = 800
        self.errors = 0
        self.abs_speed = 1
        self.speed_x = 0
        self.speed_y = 0
    def change_speed(self, v):
        if v[0] == 0 and v[1] == 0:
            pass
        else:
            len_vector = (v[0]**2 + v[1]**2) ** 0.5
            v = (v[0]/len_vector, v[1]/len_vector)
            v = (v[0] * self.abs_speed, v[1] * self.abs_speed)
            self.speed_x, self.speed_y = v[0], v[1]

    def update(self):
        if self.x - self.r <= 0:
            if self.speed_x >= 0:
                self.x += self.speed_x
        else:
            if self.x + self.r >= WIDTH_ROOM:
                if self.speed_x <= 0:
                    self.x += self.speed_x
            else:
                self.x += self.speed_x

        if self.y - self.r <= 0:
            if self.speed_y >= 0:
                self.y += self.speed_y
        else:
            if self.y + self.r >= HEIGHT_ROOM:
                if self.speed_y <= 0:
                    self.y += self.speed_y
            else:
                self.y += self.speed_y

        self.abs_speed = 50 / (self.r ** 0.5)


main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(('localhost', 10000))
main_socket.setblocking(0)
main_socket.listen(5)

players = []

foods = [Food(random.randint(0, WIDTH_ROOM), random.randint(0, HEIGHT_ROOM), FOOD_SIZE, str(random.randint(0,4))) for i in range(FOODS_AMOUNT)]

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
        #print("NewPlayer", address)
        new_socket.setblocking(0)
        new_player = Player(new_socket, address,
                            random.randint(0, WIDTH_ROOM),
                            random.randint(0, HEIGHT_ROOM),
                            START_SIZE, str(random.randint(0,4)))
        print(new_player.colour)
        mes = str(new_player.r)+' '+new_player.colour
        new_player.conn.send(mes.encode())
        players.append(new_player)

    except:
        pass

    for p in players:
        try:
            data = p.conn.recv(1024)
            data = data.decode()
            data = find(data)

            p.change_speed(data)
        except:
            pass
        p.update()

    visible_players = [[] for i in range(0,len(players))]
    for i in range(len(players)):
        for k in range(len(foods)):
            dist_x = foods[k].x - players[i].x
            dist_y = foods[k].y - players[i].y

            if ((abs(dist_x)<= (players[i].w_vision)//2+foods[k].r) and (abs(dist_y)<= (players[i].h_vision)//2+foods[k].r)):
                if (dist_x ** 2 + dist_y ** 2) ** 0.5 <= players[i].r and foods[k].r!= 0:
                    players[i].r = new_r(players[i].r, foods[k].r)
                    foods[k].r = 0
                if foods[i].r!= 0:
                    _x = str(round(dist_x))
                    _y = str(round(dist_y))
                    _r = str(round(foods[k].r))
                    _c = foods[k].colour
                    visible_players[i].append(_x+' '+_y+' '+_r+' '+_c)
        for j in range(i+1, len(players)):
            dist_x = players[j].x - players[i].x
            dist_y = players[j].y - players[i].y


            if ((abs(dist_x)<= (players[i].w_vision)//2+players[j].r) and (abs(dist_y)<= (players[i].h_vision)//2+players[j].r)):
                if (dist_x**2+dist_y**2)**0.5 <= players[i].r and players[i].r> 1.1*players[j].r:
                    players[i].r = new_r(players[i].r, players[j].r)
                    players[j].r, players[j].speed_y, players[j].speed_x = 0 , 0 , 0

                _x = str(round(dist_x))
                _y = str(round(dist_y))
                _r = str(round(players[j].r))
                _c = players[j].colour
                visible_players[i].append(_x+' '+_y+' '+_r+' '+_c)
            if ((abs(dist_x) <= (players[j].w_vision) // 2 + players[i].r) and (
                    abs(dist_y) <= (players[j].h_vision) // 2 + players[i].r)):
                if (dist_x**2+dist_y**2)**0.5 <= players[j].r and players[j].r> 1.1*players[i].r:
                    players[j].r = new_r(players[j].r, players[i].r)
                    players[i].r, players[i].speed_y, players[i].speed_x = 0 , 0 , 0
                _x = str(round(-dist_x))
                _y = str(round(-dist_y))
                _r = str(round(players[i].r))
                _c = players[i].colour
                visible_players[j].append(_x + ' ' + _y + ' ' + _r + ' ' + _c)

    responce = ['' for i in range (len(players))]
    for i in range(len(players)):
        radius = str(round(players[i].r))
        visible_players[i] = [radius] + visible_players[i]
        responce[i] = '<'+(','.join(visible_players[i]))+'>'


    for i in range(len(players)):
        try:
            players[i].conn.send(responce[i].encode())
            players[i].errors = 0
        except:
            players[i].errors += 1

    for p in players:
        if p.errors == 500 or p.r == 0:
            p.conn.close()
            players.remove(p)
    for f in foods:
        if f.r == 0:
             foods.remove(f)

    sc.fill('grey15')
    for p in players:
        x = round(p.x * WIDTH_SERVER_WINDOW / WIDTH_ROOM)
        y = round(p.y*HEIGHT_SERVER_WINDOW/ HEIGHT_ROOM)
        r = round(p.r * WIDTH_SERVER_WINDOW / WIDTH_ROOM)

        pygame.draw.circle(sc, colours[p.colour], (x, y), r)
    pygame.display.update()


pygame.quit()
main_socket.close()