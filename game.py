# Example file showing a basic pygame "game loop"
import pygame
import queue
import random

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
my_font = pygame.font.SysFont('Arial', 30)

INITIAL_PLAYER_X = 50
INITIAL_PLAYER_Y = screen.get_height() / 2
player_pos = pygame.Vector2(INITIAL_PLAYER_X, INITIAL_PLAYER_Y)
enemy_pos = pygame.Vector2(player_pos)
shadow_pos = pygame.Vector2(player_pos)
PLAYER_RADIUS = 20
FULL_ELLIPSE_X_DIAMETER = PLAYER_RADIUS * 4
FULL_ELLIPSE_Y_DIAMETER = PLAYER_RADIUS
player_x_diameter = PLAYER_RADIUS * 2
player_y_diameter = PLAYER_RADIUS * 2
PLAYER_SPEED = 900
time_since_updating_shadow = 0
animation_positions = queue.Queue()
vx = 0
vy = 0
player_angle = 0

dashing = False
extra_dash_direction = False
dash_target = (0, 0)
DASH_DISTANCE = 150
dash_percentage = 0
dash_reset = False

unclicked_d = False

particles = []
PARTICLE_SPEED = 100
PARTICLE_STOP_DELAY = 100
PARTICLE_LIFE_TIME = 300
PARTICLE_COLOR = "#22ff00"
time_after_stopping = PARTICLE_STOP_DELAY
player_particles = []
idle_player_particles = []
explosion_particles = []
aiming = True

img = pygame.image.load('enemy.png')
img = pygame.transform.scale(img, (PLAYER_RADIUS*2, PLAYER_RADIUS*2))
enemy_pos.x += 2 * DASH_DISTANCE

smoke_img = pygame.image.load('smoke1.png')
smoke_img = pygame.transform.scale(smoke_img, (PLAYER_RADIUS*2, PLAYER_RADIUS*2))
smoke_img.set_alpha(128)

class Particle:
    def __init__(self, x, y, vx, vy):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(vx, vy)

    def update(self, dt):
        #self.position += self.velocity * dt
        pass

def explosion():
    explosion_particles.append(Particle(*enemy_pos, 0, -50))



def create_particle(
    particle_x=None,
    particle_y=None,
    particle_life_time=PARTICLE_LIFE_TIME,
    particle_speed=PARTICLE_SPEED,
    particle_color=PARTICLE_COLOR
):
    if particle_x is None:
        particle_x = player_pos[0]
    if particle_y is None:
        particle_y = player_pos[1]
    particles = []
    particle_vx = 0
    particle_vy = 0

    independent_particle_vx = random.randint(0, 20) / 10 - 1
    independent_particle_vy = random.randint(0, 20) / 10 - 1
    particle_vx = independent_particle_vx# + player_vx
    particle_vy = independent_particle_vy# + player_vy
    l = (particle_vx**2 + particle_vy**2)**(1/2)
    if l == 0:
        l = 0.01
    # particle_x = particle_x + particle_vx/l*(PLAYER_RADIUS-5)
    # particle_y = particle_y + particle_vy/l*(PLAYER_RADIUS-5)

    particle = [
        [particle_x, particle_y],  # particle position
        [particle_vx, particle_vy], # particle velocity
        [0, particle_life_time],  # time since particle was created
        particle_speed,
        particle_color,
    ]
    return particle

def delete_expired_particles(particles):
    new_particles = []
    for p in particles:
        if p[2][0] < p[2][1]:
            new_particles.append(p)
    return new_particles

def delete_out_of_player_particles(particles, player_pos):
    new_particles = []
    for p in particles:
        distance_vector = [p[0][0] - player_pos.x, p[0][1] - player_pos.y]
        distance = (distance_vector[0]**2 + distance_vector[1]**2)**(1/2)
        if distance < PLAYER_RADIUS:
            new_particles.append(p)
    return new_particles

def dash(player_pos, vx, vy, player_angle, direction, aiming=False, reset=False):
    if not reset:
        dash_target = (
            player_pos[0] + direction * DASH_DISTANCE,
            (player_pos[1] - DASH_DISTANCE) if aiming else player_pos[1]
        )
    else:
        dash_target = (
            player_pos[0],
            player_pos[1] + DASH_DISTANCE
        )
    if PLAYER_RADIUS <= dash_target[0] <= screen.get_width() - PLAYER_RADIUS:
        if not reset:
            vx = direction
        else:
            vx = 0
        if aiming:
            vy = -1
            player_angle = 45 if vx > 0 else 135
        elif reset:
            vy = 1
            player_angle = 270
        else:
            vy = 0
            player_angle = 0
        return True, dash_target, vx, vy, player_angle
    return False, dash_target, vx, vy, player_angle

def draw_ellipse_angle(surface, color, rect, angle):
    target_rect = pygame.Rect(rect)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(shape_surf, color, (0, 0, *target_rect.size))
    rotated_surf = pygame.transform.rotate(shape_surf, angle)
    surface.blit(rotated_surf, rotated_surf.get_rect(center = target_rect.center))

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("#0a2104")




    # RENDER #############################
   
    # dots
    x = INITIAL_PLAYER_X
    while x < screen.get_width():
        pygame.draw.circle(screen, "white", (x, INITIAL_PLAYER_Y), 1)
        x += DASH_DISTANCE
    x = INITIAL_PLAYER_X
    while x < screen.get_width():
        pygame.draw.circle(screen, "white", (x, INITIAL_PLAYER_Y - DASH_DISTANCE), 1)
        x += DASH_DISTANCE
    x = INITIAL_PLAYER_X
    while x > 0:
        pygame.draw.circle(screen, "white", (x, INITIAL_PLAYER_Y), 1)
        x -= DASH_DISTANCE

    pygame.display.set_caption('Quick Start')
    # shadow
    shadow_color = "#179c03"  # "#144508"
    shadow_x_diameter = player_x_diameter-5
    shadow_y_diameter = player_y_diameter-5

    draw_ellipse_angle(
        screen,
        shadow_color,
        (
            shadow_pos[0] - shadow_x_diameter / 2,  # left of player
            shadow_pos[1] - shadow_y_diameter / 2,  # top of player
            shadow_x_diameter,
            shadow_y_diameter,
        ),
        player_angle
    )

    # enemy
    screen.blit(img, (enemy_pos.x - PLAYER_RADIUS, enemy_pos.y - PLAYER_RADIUS))

    # player
    player_color = "#0d2e05" #if (vx == 0 and vy == 0) else "#179c03"
    draw_ellipse_angle(
        screen,
        player_color,
        (
            player_pos[0] - player_x_diameter / 2,  # left of player
            player_pos[1] - player_y_diameter / 2,  # top of player
            player_x_diameter,
            player_y_diameter
        ),
        player_angle
    )

    # particles
    for p in particles:
        pygame.draw.rect(screen, p[4], pygame.Rect(p[0][0], p[0][1], 2, 2))  # player

    # smoke
    for p in explosion_particles:
        screen.blit(smoke_img, smoke_img.get_rect(center=p.position))


    # shoot lines
    if False: #aiming:
        #draw line from player to player_x + dash_target, player_y - dash_target
        pygame.draw.line(
            screen,
            "white",
            player_pos,
            (player_pos[0] + DASH_DISTANCE, player_pos[1] - DASH_DISTANCE)
        )
        #draw line from player to player_x - dash_target, player_y - dash_target
        pygame.draw.line(
            screen,
            "white",
            player_pos,
            (player_pos[0] - DASH_DISTANCE, player_pos[1] - DASH_DISTANCE)
        )



    text_surface = my_font.render(
        f'''
        ''',
        False, "white")
    screen.blit(text_surface, (0,0))

    # UPDATE #############################

    # shadow
    if not animation_positions.empty():
        time_since_updating_shadow += clock.get_time()
        if time_since_updating_shadow > 30:
            q_pos = animation_positions.get()
            shadow_pos.x = q_pos[0]
            shadow_pos.y = q_pos[1]
    else:
        time_since_updating_shadow = 0
        if shadow_pos != player_pos:
            shadow_pos.x = player_pos[0]
            shadow_pos.y = player_pos[1]



    # keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        if unclicked_a:
            if not dashing:
                dashing, dash_target, vx, vy, player_angle = dash(player_pos, vx, vy, player_angle, -1, aiming)
            else:
                extra_dash_direction = -1
        unclicked_a = False
    else:
        unclicked_a = True
    if keys[pygame.K_d]:
        if unclicked_d:
            if not dashing:
                dashing, dash_target, vx, vy, player_angle = dash(player_pos, vx, vy, player_angle, 1, aiming)
            else:
                extra_dash_direction = 1
        unclicked_d = False
    else:
        unclicked_d = True

    if keys[pygame.K_w]:
        vy = -1
        vx = 0
    if keys[pygame.K_s]:
        vy = 1
        vx = 0
    if keys[pygame.K_SPACE]:
        aiming = True
        if not dashing:
            vx = 0
            vy = 0
    else:
        aiming = True
    if keys[pygame.K_c]:
        player_pos[0] = INITIAL_PLAYER_X
        player_pos[1] = INITIAL_PLAYER_Y
        explosion()

    if player_pos[0] > screen.get_width() - PLAYER_RADIUS:
        vx = -1
    if player_pos[0] < PLAYER_RADIUS:
        vx = 1
    if player_pos[1] > screen.get_height() - PLAYER_RADIUS:
        vy = -1
    if player_pos[1] < PLAYER_RADIUS:
        vy = 1

    if extra_dash_direction and not dashing:
        dashing, dash_target, vx, vy, player_angle = dash(
            player_pos, vx, vy, player_angle, extra_dash_direction, aiming)
        extra_dash_direction = 0


    if dashing:
        if vx != 0:
            distance_left = dash_target[0] - player_pos[0]
        else:
            distance_left = dash_target[1] - player_pos[1]
        if (vx > 0 and distance_left <= 0) or \
        (vx < 0 and distance_left >= 0) or \
        (vy > 0 and distance_left <= 0):
            player_pos[0] = dash_target[0]
            player_pos[1] = dash_target[1]
            if vy < 0:
                dash_reset = True
                player_angle = 270
                dashing, dash_target, vx, vy, player_angle = dash(player_pos, vx, vy, player_angle, 0, reset=True)
            else:
                vx = 0
                vy = 0
                player_x_diameter = PLAYER_RADIUS * 2
                player_y_diameter = PLAYER_RADIUS * 2
                dashing = False
                player_angle = 0
        else:
            distance_left = abs(distance_left)
            dash_percentage_left = distance_left / DASH_DISTANCE
            dash_percentage = 1 - dash_percentage_left
            first_breakpoint = 0.5
            second_breakpoint = 0.75
            if dash_percentage < first_breakpoint:
                # linear transform into ellipse
                # x: player_radius->player_radius*2
                # y: player_radius->player_radius/2
                variance = FULL_ELLIPSE_X_DIAMETER - PLAYER_RADIUS * 2
                player_x_diameter = PLAYER_RADIUS * 2 + int(dash_percentage / first_breakpoint * variance)
                variance = PLAYER_RADIUS * 2 - FULL_ELLIPSE_Y_DIAMETER
                player_y_diameter = PLAYER_RADIUS * 2 - int(dash_percentage / first_breakpoint * variance)
            if dash_percentage > first_breakpoint:
                if not extra_dash_direction:
                    # linear reduction from 100% speed to 70%
                    v_max = 1
                    v_variation = 0.3
                    gradient = int(distance_left * 10 / (DASH_DISTANCE * (1 - first_breakpoint))) / 10 * v_variation
                    if vx > 0:
                        vx = v_max - v_variation + gradient
                    elif vx < 0:
                        vx = -(v_max - v_variation) - gradient
                    if vy > 0:
                        vy = v_max - v_variation + gradient
                    elif vy < 0:
                        vy = -(v_max - v_variation) - gradient
                # linear return to normal circle
                # x: player_radius*2->player_radius
                # y: player_radius/2->player_radius
                variance = FULL_ELLIPSE_X_DIAMETER - PLAYER_RADIUS * 2
                player_x_diameter = PLAYER_RADIUS * 2 + variance - int((dash_percentage - first_breakpoint) / first_breakpoint * variance)
                variance = PLAYER_RADIUS * 2 - FULL_ELLIPSE_Y_DIAMETER
                player_y_diameter = PLAYER_RADIUS * 2 - variance + int((dash_percentage - first_breakpoint) / first_breakpoint * variance)
            if dash_percentage > second_breakpoint:
                if not extra_dash_direction:
                    # linear reduction from 70% speed to 0
                    # add 50 to over shoot for smoother movement
                    # this line is a mess, maybe can be rethought to make it clearer,
                    # I won't bother right now, the movement is pretty smooth
                    v_max = 0.7
                    v_variation = 0.5
                    gradient = int(distance_left * 100 / (DASH_DISTANCE * (1 - second_breakpoint))) / 100 * v_variation
                    if vx > 0:
                        vx = v_max - v_variation + gradient
                    elif vx < 0:
                        vx = -(v_max - v_variation) - gradient
                    if vy > 0:
                        vy = v_max - v_variation + gradient
                    elif vy < 0:
                        vy = -(v_max - v_variation) - gradient


    if vx == 0 and vy == 0:
        if time_after_stopping < PARTICLE_STOP_DELAY:
            time_after_stopping += clock.get_time()
    else:
        time_after_stopping = 0

    # player position
    last_pos = tuple(player_pos)
    player_pos.x += PLAYER_SPEED * vx * dt
    player_pos.y += PLAYER_SPEED * vy * dt
    if tuple(player_pos) != last_pos:
        animation_positions.put((player_pos.x, player_pos.y))

    # particles
    if len(player_particles) < 180 and (True or vx != 0 or vy != 0 or time_after_stopping < PARTICLE_STOP_DELAY):
        for i in range(5):
            if time_after_stopping>0:
                if len(idle_player_particles) < 20:
                    idle_player_particles.append(create_particle(particle_speed=10, particle_life_time=PARTICLE_LIFE_TIME*4))
            else:
                player_particles.append(create_particle())

    particles = player_particles + idle_player_particles
    for p in particles:
        pvx = p[1][0]
        pvy = p[1][1]
        p[0][0] += p[3] * pvx * dt
        p[0][1] += p[3] * pvy * dt
        p[2][0] += clock.get_time()

    for p in explosion_particles:
        p.update(dt)

    if dashing:
        idle_player_particles = []
    player_particles = delete_expired_particles(player_particles)
    # idle_player_particles = delete_expired_particles(idle_player_particles)
    idle_player_particles = delete_out_of_player_particles(idle_player_particles, player_pos)








    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()