import socket
import  time
import pygame

WIDTH = 1000
HEIGHT = 800
colours = {'0': (255, 255, 0), '1': (255, 0, 0), '2': (0, 255, 0),
           '3':(0, 255,255), '4': (255, 34, 178)}
def draw_opponents(data, screen):
    for i in range(len(data)):
        j = data[i].split(' ')

        x = WIDTH // 2 + int(j[0])
        y = HEIGHT // 2 + int(j[1])
        r = int(j[2])
        c = colours[j[3]]
        pygame.draw.circle(screen, c, (x, y), r)
def find(strn):
    first_o = None
    for i in range(len(strn)):
        if strn[i] == '<':
            first_o = i
        if strn[i] == '>' and first_o != None:
            close = i
            res = strn[first_o + 1: close]
            return res
    return ''


local_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
local_s.connect(('localhost', 10000))

my_colour = local_s.recv(16).decode()

pygame.init()
sc = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Agario')
v = []
old_v = [0,0]
is_game_running = True
while is_game_running:

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            is_game_running = False

    if pygame.mouse.get_focused():
        pos = pygame.mouse.get_pos()
        v = [pos[0] - WIDTH//2, pos[1]-HEIGHT//2]
        if v[0]**2 + v[1]**2 <= 50**2:
            v = [0, 0]

    if len(v) > 0 and v != old_v:
        old_v = v
        message = '<' + str(v[0])+',' + str(v[1])+'>'


        local_s.send(message.encode())

    data = local_s.recv(1024)
    data = data.decode()
    data = find(data)
    print('receive', data)
    data = data.split(',')

    sc.fill('grey50')
    pygame.draw.circle(sc, colours[my_colour], (WIDTH//2, HEIGHT//2), 50)
    if data!=['']:
        draw_opponents(data, sc)
    pygame.display.update()
pygame.quit()
#python client.py