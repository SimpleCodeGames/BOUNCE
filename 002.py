import pygame
import sys
import random
import math
import threading
import time

BG = (20, 20, 25)
CIRCLE_COLOR = (90, 90, 110)

tab_y = 500
tab_x = 500

center_x = tab_x // 2
center_y = tab_y // 2
radius = 200

uniform_radius = 14

# Ball index reference:
# [0]: x position
# [1]: y position
# [2]: x velocity (vx)
# [3]: y velocity (vy)
# [4]: radius (r)
# [5]: color tuple (RGB)
# [6]: trail list storing past (x, y) positions
balls = [
    [center_x - 40, center_y - 30, 5, -3, uniform_radius, (255, 0, 0), []],
    [center_x + 50, center_y + 20, -4, 6, uniform_radius, (255, 234, 0), []],
    [center_x, center_y + 60, 6, 3, uniform_radius, (0, 0, 255), []]
]

lock = threading.Lock()

def update_physics():
    while True:
        time.sleep(0.015)
        with lock:
            for b in balls:
                b[6].append((b[0], b[1]))
                if len(b[6]) > 15:
                    b[6].pop(0)

                b[0] += b[2]
                b[1] += b[3]
                
                dx = b[0] - center_x
                dy = b[1] - center_y
                dist = math.hypot(dx, dy)
                
                if dist + b[4] >= radius:
                    if dist > 0:
                        nx = dx / dist
                        ny = dy / dist
                    else:
                        nx, ny = 1, 0
                    
                    dot = b[2] * nx + b[3] * ny
                    b[2] = b[2] - 2 * dot * nx
                    b[3] = b[3] - 2 * dot * ny
                    
                    b[0] = center_x + nx * (radius - b[4])
                    b[1] = center_y + ny * (radius - b[4])
            
            for i in range(len(balls)):
                for j in range(i + 1, len(balls)):
                    b1 = balls[i]
                    b2 = balls[j]
                    
                    dx = b2[0] - b1[0]
                    dy = b2[1] - b1[1]
                    dist = math.hypot(dx, dy)
                    min_dist = b1[4] + b2[4]
                    
                    if dist < min_dist and dist > 0:
                        nx = dx / dist
                        ny = dy / dist
                        
                        overlap = min_dist - dist
                        b1[0] -= nx * overlap * 0.5
                        b1[1] -= ny * overlap * 0.5
                        b2[0] += nx * overlap * 0.5
                        b2[1] += ny * overlap * 0.5
                        
                        kx = b1[2] - b2[2]
                        ky = b1[3] - b2[3]
                        p = 2 * (nx * kx + ny * ky) / 2
                        
                        b1[2] -= p * nx
                        b1[3] -= p * ny
                        b2[2] += p * nx
                        b2[3] += p * ny

def draw(screen):
    pygame.draw.circle(screen, CIRCLE_COLOR, (center_x, center_y), radius, 4)
    for b in balls:
        trail_len = len(b[6])
        for idx, pos in enumerate(b[6]):
            alpha_ratio = (idx + 1) / trail_len
            trail_radius = max(1, int(b[4] * alpha_ratio * 0.8))
            
            surf_size = trail_radius * 2 + 2
            trail_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            alpha_val = int(120 * alpha_ratio)
            trail_color = (b[5][0], b[5][1], b[5][2], alpha_val)
            
            pygame.draw.circle(trail_surf, trail_color, (trail_radius + 1, trail_radius + 1), trail_radius)
            screen.blit(trail_surf, (int(pos[0]) - trail_radius - 1, int(pos[1]) - trail_radius - 1))

        pygame.draw.circle(screen, b[5], (int(b[0]), int(b[1])), b[4])

def main():
    pygame.init()
    pygame.display.set_caption("002")
    screen = pygame.display.set_mode((tab_x, tab_y))
    clock = pygame.time.Clock()

    physics_thread = threading.Thread(target=update_physics, daemon=True)
    physics_thread.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        screen.fill(BG)
        
        with lock:
            draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()