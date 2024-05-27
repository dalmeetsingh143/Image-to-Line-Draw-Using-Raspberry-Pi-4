from picamera2 import Picamera2
import pygame

pygame.init()
res = (800,600)
screen = pygame.display.set_mode(res)

camera = Picamera2()
camera.preview_configuration.main.size = res
camera.preview_configuration.main.format = 'BGR888'
camera.configure("preview")

#####################
# here configure still capture
capture_config = camera.create_still_configuration()
camera.still_configuration.main.size = (2500,2500)
#####################

camera.start()

while True:
##################################
# depress "a" key -> capture image
#################################
    events=pygame.event.get()
    for e in events:
        if (e.type == pygame.KEYDOWN and e.key == pygame.K_a):
            print("capture image")
            camera.switch_mode_and_capture_file(capture_config, "image.jpg")
            print("display image")
            img=pygame.image.load("aaaaa.jpg").convert()
            rect=img.get_rect()
            screen.blit(img, rect)
            pygame.display.update()
            print("display image 5s")
            time.sleep(5)

    array = camera.capture_array()
    img = pygame.image.frombuffer(array.data, res, 'RGB')
    screen.blit(img, (0, 0))
    pygame.display.update()