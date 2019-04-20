import pygame, random, math

pygame.init()

class Laser:
    """Laser object represent the projectiles fired by the Zapper"""
    def __init__(self, center, images, rotation = 0):
        self.images = images
        testSurf = pygame.Surface((32, 16))
        self.size = pygame.transform.rotate(testSurf, -rotation).get_size()
        rect = pygame.Rect((0, 0), self.size)
        rect.center = center
        self.pos = list(rect.topleft)
        self.phase = random.randint(1, 5)
        self._phase_speed = 0.01
        self.phase_time = 0
        self.time_passed = 0
        self.speed = 1200    # Speed in pixels per second
        self.dead = False
        self.damage = 1
        self.laserType = "laser"
        self.hits = 0
        self.rotation = rotation
        self.green = False

    def get_rect(self):
        """Returns a pygame.Rect object representing this Laser"""
        rect = pygame.Rect((0, 0), self.size)
        rect.topleft = self.pos
        return rect

    def draw(self, surf):
        """Render Laser"""
        surf.blit(pygame.transform.rotate(self.images[f"{self.laserType}{self.phase}"], -self.rotation), self.pos)

    def update(self, time_passed):
        """Update Laser"""
        self.phase_time += time_passed
        if self.phase_time >= self._phase_speed:
            self.phase += 1
            self.phase_time = 0
        if self.phase == 6:
            self.phase = 1
        self.time_passed = time_passed
        self.pos[0] -= self.speed * self.time_passed * math.cos(math.radians(self.rotation + 90))
        self.pos[1] -= self.speed * self.time_passed * math.sin(math.radians(self.rotation + 90))
        display_rect = pygame.Rect((0, 0), (800, 600))
        if not display_rect.colliderect(self.get_rect()):
            self.dead = True

class GreenLaser(Laser):
    def __init__(self, center, images, rotation = 0):
        super().__init__(center, images, rotation)
        self.damage = 5
        self.laserType = "greenlaser"
        self.green = True


