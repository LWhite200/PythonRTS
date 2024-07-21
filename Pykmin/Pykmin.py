import pygame
import random
import math

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PYKMIN")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
PINK = (255, 192, 203)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
BROWN = (165, 42, 42)

AQUA = (0, 255, 255)
FUCHSIA = (255, 0, 255)
GRAY = (128, 128, 128)
LIME = (0, 255, 150)
MAROON = (128, 0, 0)
NAVY = (0, 0, 128)
OLIVE = (128, 128, 0)
SILVER = (192, 192, 192)
TEAL = (0, 128, 128)
CORAL = (255, 127, 80)
VIOLET = (238, 130, 238)
INDIGO = (75, 0, 130)
BEIGE = (245, 245, 220)
TURQUOISE = (64, 224, 208)


# Constants
THROW_LIMIT = 200  # Maximum throw distance
PIKMIN_RADIUS = 10
MIN_OVERLAP_DISTANCE = 1  # Minimum distance to avoid complete overlap
DIS_FROM_CAPTN = 37
THROW_SHRINK = 0

# Game objects
class Captain:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 20
        self.color = BLUE
        self.speed = 5
        self.direction = (1, 0)  # Initial direction

    def move(self, dx, dy):
        if dx != 0 or dy != 0:
            mag = math.sqrt(dx**2 + dy**2)
            dx, dy = dx / mag, dy / mag
            self.x += dx * self.speed
            self.y += dy * self.speed
            self.direction = (dx, dy)  # Update direction

    def draw(self):
        # Draw the main circle
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        # Draw the direction indicator (nose)
        nose_x = self.x + int(self.direction[0] * self.radius)
        nose_y = self.y + int(self.direction[1] * self.radius)
        pygame.draw.circle(screen, YELLOW, (nose_x, nose_y), 5)

class Pikmin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = PIKMIN_RADIUS
        self.color = RED
        self.speed = 5
        self.following = True
        self.heldObj = None
        self.target = None
        self.throwing = False

    def follow(self, target):
        if self.following and not self.heldObj:
            # Calculate the position slightly behind the target
            offset_distance = DIS_FROM_CAPTN  # Distance behind the player
            dx = target.direction[0] * -offset_distance
            dy = target.direction[1] * -offset_distance
            follow_x = target.x + dx
            follow_y = target.y + dy

            # Move towards the offset position
            move_dx = follow_x - self.x
            move_dy = follow_y - self.y
            dist = math.sqrt(move_dx**2 + move_dy**2)
            if dist > 5:
                self.x += int(move_dx / dist * self.speed)
                self.y += int(move_dy / dist * self.speed)

    def move_to_target(self):
        if self.target:
            dx = self.target[0] - self.x
            dy = self.target[1] - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 5:
                self.x += int(dx / dist * self.speed)
                self.y += int(dy / dist * self.speed)
                self.radius = max(2, int(self.radius * 0.95))  # Shrink while moving
            else:
                self.target = None
                self.radius = PIKMIN_RADIUS  # Reset size
                self.throwing = False

    def hold(self, obj):
        if self.heldObj:
            dx = onion.x - self.x
            dy = onion.y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 5:
                self.x += int(dx / dist * self.speed)
                self.y += int(dy / dist * self.speed)
                obj.x, obj.y = self.x, self.y
            else:
                self.heldObj = None
                obj.delivered = all(pikmin.heldObj != obj for pikmin in pikmin_list)  # Check if all Pikmin dropped the object

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

class Onion:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.radius = 30
        self.color = GREEN
        self.outline_thickness = 3  # Thickness of the outline

    def draw(self):
        # Draw the black outline
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius + self.outline_thickness)
        # Draw the Onion itself
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)


class Object:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.radius = 15
        self.color = BLACK
        self.pikmin_needed = random.randint(1, 3)
        self.delivered = False
        self.pikmin_carrying = 0

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        # Draw the number of Pikmin needed on top of the object
        font = pygame.font.Font(None, 24)
        text = font.render(str(self.pikmin_needed), True, WHITE)
        text_rect = text.get_rect(center=(self.x, self.y - self.radius - 10))
        screen.blit(text, text_rect)

    def can_be_carried_by(self, pikmin):
        return not self.delivered and self.pikmin_carrying < self.pikmin_needed

    def add_pikmin(self):
        self.pikmin_carrying += 1

    def remove_pikmin(self):
        self.pikmin_carrying -= 1

def is_overlapping(pikmin1, pikmin2):
    distance = math.sqrt((pikmin1.x - pikmin2.x) ** 2 + (pikmin1.y - pikmin2.y) ** 2)
    return distance < (pikmin1.radius + pikmin2.radius - MIN_OVERLAP_DISTANCE)

# Game variables
captain = Captain()
pikmin_list = [Pikmin(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)) for _ in range(5)]
onion = Onion()
objects = [Object() for _ in range(10)]
throwing_cursor = False

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(LIME)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                for pikmin in pikmin_list:
                    if not pikmin.following and not pikmin.heldObj and not pikmin.throwing:
                        pikmin.following = True
                        pikmin.x, pikmin.y = captain.x, captain.y
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for pikmin in pikmin_list:
                    if pikmin.following and math.sqrt((pikmin.x - captain.x) ** 2 + (pikmin.y - captain.y) ** 2) < 50:
                        # Calculate the throw limit position
                        dx = mouse_x - captain.x
                        dy = mouse_y - captain.y
                        dist = math.sqrt(dx**2 + dy**2)
                        if dist > THROW_LIMIT:
                            mouse_x = captain.x + int(dx / dist * THROW_LIMIT)
                            mouse_y = captain.y + int(dy / dist * THROW_LIMIT)
                        pikmin.target = (mouse_x, mouse_y)
                        pikmin.following = False
                        pikmin.throwing = True
                        break
            elif event.button == 3:  # Right click
                throwing_cursor = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:  # Right click
                throwing_cursor = False

    keys = pygame.key.get_pressed()
    dx = keys[pygame.K_d] - keys[pygame.K_a]
    dy = keys[pygame.K_s] - keys[pygame.K_w]
    captain.move(dx, dy)
    
    # Update cursor position based on mouse
    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - captain.x
    dy = mouse_y - captain.y
    dist = math.sqrt(dx**2 + dy**2)
    if dist > THROW_LIMIT:
        cursor_x = captain.x + int(dx / dist * THROW_LIMIT)
        cursor_y = captain.y + int(dy / dist * THROW_LIMIT)
    else:
        cursor_x = mouse_x
        cursor_y = mouse_y
    pygame.draw.circle(screen, BLACK, (cursor_x, cursor_y), 5)

    # Draw the recall circle when right-click is held down
    if throwing_cursor:
        # Calculate the position of the recall circle
        dx = mouse_x - captain.x
        dy = mouse_y - captain.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > THROW_LIMIT:
            recall_x = captain.x + int(dx / dist * THROW_LIMIT)
            recall_y = captain.y + int(dy / dist * THROW_LIMIT)
        else:
            recall_x = mouse_x
            recall_y = mouse_y
        
        # Draw the recall circle
        pygame.draw.circle(screen, BLACK, (recall_x, recall_y), 100, 1)
        for pikmin in pikmin_list:
            if math.sqrt((pikmin.x - recall_x) ** 2 + (pikmin.y - recall_y) ** 2) < 100:
                pikmin.following = True

    captain.draw()
    
    for pikmin in pikmin_list:
        if pikmin.heldObj:
            pikmin.hold(pikmin.heldObj)
        elif pikmin.throwing:
            pikmin.move_to_target()
        else:
            nearest_obj = None
            nearest_dist = float('inf')
            for obj in objects:
                if obj.can_be_carried_by(pikmin):
                    dist = math.sqrt((pikmin.x - obj.x) ** 2 + (pikmin.y - obj.y) ** 2)
                    if dist < nearest_dist and dist < 50:
                        nearest_dist = dist
                        nearest_obj = obj
            if nearest_obj:
                nearest_obj.add_pikmin()
                pikmin.heldObj = nearest_obj
                pikmin.following = False
            pikmin.follow(captain)
        pikmin.draw()

    onion.draw()
    
    for obj in objects:
        if not obj.delivered:
            obj.draw()

    # Prevent Pikmin from overlapping completely
    for i, pikmin1 in enumerate(pikmin_list):
        for pikmin2 in pikmin_list[i + 1:]:
            if is_overlapping(pikmin1, pikmin2):
                angle = math.atan2(pikmin2.y - pikmin1.y, pikmin2.x - pikmin1.x)
                pikmin1.x -= int(math.cos(angle) * 2)
                pikmin1.y -= int(math.sin(angle) * 2)
                pikmin2.x += int(math.cos(angle) * 2)
                pikmin2.y += int(math.sin(angle) * 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()