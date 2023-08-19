import pygame
import cv2
import os

def generate_dict(path):
    result = {}
    for name in os.listdir(path):
        if name.endswith('.DS_Store'):
            continue
        subpath = os.path.join(path, name)
        if os.path.isdir(subpath):
            result[name] = generate_dict(subpath)
        else:
            result =[pygame.image.load(os.path.join(path, x)).convert_alpha() for x in os.listdir(path) if not x.endswith('.DS_Store')]
            break
    return result

width, height = 720, 720

BACKGROUND_IMAGE = pygame.image.load('bg.png')
screen = pygame.display.set_mode((width, height))
imgs = generate_dict('img')
pos = {
    'B':[100,400,-1],
    'A':[400,400,1]
}

pygame.init()
current_frame = 0

frames=[
    ['A',10,50,1,'idle','cry',"what's wrong"],
    ['B',60,100,-1,'idle','pround',''],
    ['A',100,150,-1,'idle','talking',''],
    ['B',160,200,1,'idle','talking','']
]

frame={
    'A': {'body':pygame.image.load('img/A/body/idle/shadiao1.png'),'face':pygame.image.load('img/A/face/talking/女-0002.png')},
    'B': {'body':pygame.image.load('img/B/body/idle/shadiao2.png'),'face':pygame.image.load('img/B/face/talking/女-0002.png')}
}

run = True
video_writer = cv2.VideoWriter('game_video.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (width, height))

while current_frame<200:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            run = True
        if event.type == pygame.QUIT:
            run = False

    screen.fill((0, 0, 0))

    # display the background image
    screen.blit(BACKGROUND_IMAGE, (0, 0))

    if run:
        for v in frames:
            k=v[0]
            if current_frame>=v[1] and current_frame<=v[2]:
                facing = v[3]
                bodyImgs=imgs[k]['body'][v[4]]
                faceImgs=imgs[k]['face'][v[5]]
                body = bodyImgs[current_frame % len(bodyImgs)]
                face = faceImgs[current_frame % len(faceImgs)]
                if facing == -1:
                    body = pygame.transform.flip(body, True, False)
                    face = pygame.transform.flip(face, True, False)
                frame[k]['body']=body
                frame[k]['face']=face
                print(current_frame,body,face)
            screen.blit(frame[k]['body'], (pos[k][0], pos[k][1]))
            screen.blit(frame[k]['face'], (pos[k][0], pos[k][1]-70))

        current_frame+=1

    # Update the display after each iteration of the while loop
    pygame.display.update()
    pygame_image = pygame.surfarray.array3d(screen)
    cv2_image = cv2.cvtColor(pygame_image, cv2.COLOR_RGB2BGR)
    rotated_frame = cv2.rotate(cv2_image, cv2.ROTATE_90_CLOCKWISE)
    video_writer.write(rotated_frame)

# Quit the program
pygame.quit()
video_writer.release()