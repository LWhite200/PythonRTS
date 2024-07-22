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
TURQUOISE = (64, 224, 208)
LIME = (0, 255, 150)

# Constants
THROW_LIMIT = 200  # Maximum throw distance
PIKMIN_RADIUS = 10
MIN_OVERLAP_DISTANCE = 1  # Minimum distance to avoid complete overlap
DIS_FROM_CAPTN = 37
PIK_MOVE_OBJ_SPEED = 4

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
        self.color = PINK
        self.speed = 5
        self.following = False
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
        if not self.following and not self.heldObj and obj.can_be_carried_by(self):
            self.heldObj = obj
            obj.add_pikmin(self)
            self.following = False
            self.target = None  # Stop moving to target if holding an object

    def drop(self):
        if self.heldObj:
            self.heldObj.remove_pikmin(self)
            self.heldObj = None
            self.throwing = False
            self.following = True

    def draw(self):
        # Set the color based on the Pikmin's state
        if self.heldObj:
            self.color = RED
            outline = False
        elif self.following:
            self.color = RED
            outline = True
        else:
            self.color = PINK
            outline = True
        
        # Draw the outline if needed
        if outline:
            pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius + 2)
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)


class Onion:
    def __init__(self):
        # self.x = random.randint(50, WIDTH - 50)
        # self.y = random.randint(50, HEIGHT - 50)
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 30
        self.color = GREEN
        self.outline_thickness = 3  # Thickness of the outline

    def draw(self):
        # Create a surface with per-pixel alpha for transparency
        onion_surface = pygame.Surface((self.radius * 2 + self.outline_thickness * 2, self.radius * 2 + self.outline_thickness * 2), pygame.SRCALPHA)
        # Draw the transparent onion on the surface
        pygame.draw.circle(onion_surface, self.color + (100,), (self.radius + self.outline_thickness, self.radius + self.outline_thickness), self.radius)  # Adjust alpha value as needed
        
        # Draw the onion outline directly on the screen surface
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius + self.outline_thickness, self.outline_thickness)

        # Draw the transparent onion surface on the main screen surface
        screen.blit(onion_surface, (self.x - self.radius - self.outline_thickness, self.y - self.radius - self.outline_thickness))

class PikminSpawner:
    def __init__(self, onion, pikmin_list):
        self.onion = onion
        self.pikmin_list = pikmin_list

    def spawn_pikmin(self, count):
        for _ in range(count):
            # Spawn Pikmin close to the Onion
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0, 30)  # Adjust radius as needed
            spawn_x = int(self.onion.x + radius * math.cos(angle))
            spawn_y = int(self.onion.y + radius * math.sin(angle))
            self.pikmin_list.append(Pikmin(spawn_x, spawn_y))

class Object:
    def __init__(self, onion, pikmin_spawner):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.radius = 15
        self.color = TURQUOISE
        self.pikmin_needed = random.randint(1, 3)
        self.delivered = False
        self.pikmin_carrying = 0
        self.onion = onion
        self.pikmin_spawner = pikmin_spawner  # Reference to PikminSpawner
        self.carrying_pikmin = []

    def draw(self):
        if self.pikmin_carrying == 0:
            self.color = TURQUOISE
        elif self.pikmin_carrying >= self.pikmin_needed:
            self.color = WHITE
        else:
            self.color = BLUE

        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        font = pygame.font.Font(None, 24)
        text = font.render(str(self.pikmin_needed - self.pikmin_carrying), True, WHITE)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)
        
    def hold(self):
        if self.delivered or not self.pikmin_carrying:
            return

        if self.has_enough():
            dx = self.onion.x - self.x
            dy = self.onion.y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 5:
                move_x = int(dx / dist * PIK_MOVE_OBJ_SPEED)
                move_y = int(dy / dist * PIK_MOVE_OBJ_SPEED)
                self.x += move_x
                self.y += move_y
                # Move all Pikmin carrying this object
                for pikmin in self.carrying_pikmin:
                    pikmin.x += move_x
                    pikmin.y += move_y
            else:
                self.delivered = True
                for pikmin in self.carrying_pikmin:
                    pikmin.color = PINK
                    pikmin.heldObj = None
                    pikmin.following = False
                self.pikmin_spawner.spawn_pikmin(self.pikmin_needed)  # Spawn Pikmin

    def has_enough(self):
        return self.pikmin_needed <= self.pikmin_carrying

    def can_be_carried_by(self, pikmin):
        return not self.delivered and self.pikmin_carrying < self.pikmin_needed

    def add_pikmin(self, pikmin):
        self.pikmin_carrying += 1
        self.carrying_pikmin.append(pikmin)

    def remove_pikmin(self, pikmin):
        self.pikmin_carrying -= 1
        self.carrying_pikmin.remove(pikmin)

def is_overlapping(pikmin1, pikmin2):
    distance = math.sqrt((pikmin1.x - pikmin2.x) ** 2 + (pikmin1.y - pikmin2.y) ** 2)
    return distance < (pikmin1.radius + pikmin2.radius - MIN_OVERLAP_DISTANCE)

# Game variables
# Game variables
pikmin_list = []
onion = Onion()
captain = Captain()
pikmin_spawner = PikminSpawner(onion, pikmin_list)
pikmin_spawner.spawn_pikmin(5)  # Spawn initial Pikmin
objects = [Object(onion, pikmin_spawner) for _ in range(10)]
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
                pikmin.drop()
                pikmin.following = True  # Set to follow the captain again
                pikmin.target = None  # Clear any target they might have

    captain.draw()
    
    for pikmin in pikmin_list:
        if pikmin.throwing:
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
                pikmin.hold(nearest_obj)  # Use the hold method to update the object's state
        pikmin.follow(captain)
        pikmin.draw()
        
    # Update objects and handle their destruction
    for obj in objects[:]:
        obj.hold()
        obj.draw()
        if obj.delivered:
            objects.remove(obj)  # Remove the object from the game

    onion.draw()
    
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