import socket
import  time
import pygame

WIDTH = 1000
HEIGHT = 800

local_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
local_s.connect(('localhost', 10000))

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
        print(message)

        local_s.send(message.encode())

    data = local_s.recv(1024)
    data = data.decode()

    sc.fill('grey50')
    pygame.draw.circle(sc, (255, 0, 0), (WIDTH//2, HEIGHT//2), 50)
    pygame.display.update()
pygame.quit()
#python client.py