import random
import pygame
import time

#צבעים
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

#צלילים
pygame.mixer.init()
game_sound = pygame.mixer.Sound('Sounds\\background.mpeg')
game_sound.set_volume(0.1)
death_sound = pygame.mixer.Sound('Sounds\\fail.mpeg')
death_sound.set_volume(0.4)
ate_sound = pygame.mixer.Sound('Sounds\\ate.mpeg')
ate_sound.set_volume(0.4)


#יוצר ריבוע
class Segment(pygame.sprite.Sprite):
    _WIDTH = 10
    _HEIGHT = 10
    _MARGIN = 3

    def __init__(self, x, y, color):
        super().__init__()

        self.image = pygame.Surface([self._WIDTH, self._HEIGHT])
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

#תת-מחלקה דמות נחש
class SnakeSegment(Segment):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        super().__init__(self.x, self.y, WHITE)
        self.index = None
    
    def __str__(self):
        if self.index == None:
            return "i am the first snake part"
        return f"I am snake segment number: {self.index}"

#תת-מחלקה דמות תפוח
class Apple(Segment):
    def __init__(self, x, y):
        super().__init__(x, y, RED)

#מחלקה קוד נחש
class Snake(object):
    _STARTING_SEGMENTS = 10
#ממקם נחש
    def __init__(self, base_x, base_y):
        self._segments = []
        self._sprites = pygame.sprite.Group()
        for i in range(self._STARTING_SEGMENTS):
            x = base_x - (Segment._WIDTH + Segment._MARGIN) * i
            y = base_y
            segment = SnakeSegment(x, y)
            segment.index = i
            self._segments.append(segment)
            self._sprites.add(segment)
        self._x_change = Segment._WIDTH + Segment._MARGIN
        self._y_change = 0
#תנועה
    def move(self, x_change, y_change):
        self._x_change = x_change
        self._y_change = y_change

    def update(self):
        #תנועת פיקסלים
        # Removing last segment
        old_segment = self._segments.pop()
        self._sprites.remove(old_segment)

        # Adding a new segment
        x = self._segments[0].rect.x + self._x_change
        y = self._segments[0].rect.y + self._y_change
        segment = SnakeSegment(x, y)

        self._segments.insert(0, segment)
        self._sprites.add(segment)
        
    def draw(self, screen):
        self._sprites.draw(screen)
#התרסק
    def has_collided_with(self, other_sprite):
        return len(pygame.sprite.spritecollide(other_sprite, self._sprites, False)) > 0
#פיקסל מאחורה
    def add_back_segment(self):
        x = self._segments[-1].rect.x - self._x_change
        y = self._segments[-1].rect.y - self._y_change
        segment = SnakeSegment(x, y)

        self._segments.append(segment)
        self._sprites.add(segment)
#מחוץ לגבולות
    def is_out_of_bounds(self, min_x, min_y, max_x, max_y):
        x, y = self._segments[0].rect.x, self._segments[0].rect.y
        return x < min_x or y < min_y or x + Segment._WIDTH > max_x or y + Segment._HEIGHT > max_y

#המסך/המשחק
class SnakeGame(object):
    #גודל  מסך
    _SCREEN_WIDTH = 1535
    _SCREEN_HEIGHT = 790
    #מריץ שינויים
    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode([self._SCREEN_WIDTH, self._SCREEN_HEIGHT])
        pygame.display.set_caption('SNAPSnake')

        self._score = 0
        self._font = pygame.font.SysFont('Consolas', 18)
        self._clock = pygame.time.Clock()
        self._done = False
        self._snake = Snake(250, 30)
        self._apple = None
    #קלט מהמשתמש
    def _process_input(self):
        for event in pygame.event.get():
            #clicked on x?
            if event.type == pygame.QUIT:
                self._screen.blit(self._font.render("game over!", False, GREEN), (200, 150))
                self._screen.blit(self._font.render("clicked on the x.", False, GREEN), (200, 200))
                pygame.display.flip()
                game_sound.stop()
                death_sound.play()
                time.sleep(2.1)
                self._done = True
                break
            #else, is any key prassed?
            if event.type == pygame.KEYDOWN:
                moving_dictence = Segment._WIDTH + Segment._MARGIN
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self._snake.move(moving_dictence * -1, 0)
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self._snake.move(moving_dictence, 0)
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self._snake.move(0, moving_dictence * -1)
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self._snake.move(0, moving_dictence)
                if event.key == pygame.K_q:
                    self._screen.blit(self._font.render("game over!", False, GREEN), (200, 150))
                    self._screen.blit(self._font.render("clicked on q.", False, GREEN), (200, 200))
                    pygame.display.flip()
                    game_sound.stop()
                    death_sound.play()
                    time.sleep(2.1)
                    self._done = True
                if event.key == pygame.K_c:
                    main()

    def _update(self):
        self._snake.update()
#מזמן תפוחים
        if self._apple is None:
            self._apple = Apple(random.randint(0, self._SCREEN_WIDTH - Segment._WIDTH),
            random.randint(0, self._SCREEN_HEIGHT - Segment._HEIGHT))

        # Check collision between our Snake and the apple
        if self._snake.has_collided_with(self._apple):
            game_sound.stop()
            ate_sound.play()
            self._score += 1
            self._apple = None
            self._snake.add_back_segment()
            time.sleep(0.5)

# Check of game is over by self crash
        for segment in self._snake._segments[:-1]:
            if segment.x == self._snake._segments[-1].x and segment.y == self._snake._segments[-1].y:
                self._screen.blit(self._font.render("game over!", False, GREEN), (200, 150))
                self._screen.blit(self._font.render("hit itself.", False, GREEN), (200, 200))
                pygame.display.flip()
                game_sound.stop()
                death_sound.play()
                time.sleep(2.1)
                self._done = True
                break

# Check of game is over by bounds crash
        if self._snake.is_out_of_bounds(0, 0, self._SCREEN_WIDTH, self._SCREEN_HEIGHT):
            self._screen.blit(self._font.render("game over!", False, GREEN), (200, 150))
            self._screen.blit(self._font.render("hit an adge.", False, GREEN), (200, 200))
            pygame.display.flip()
            game_sound.stop()
            death_sound.play()
            time.sleep(2.1)
            self._done = True
#להריץ מסך
    def _render(self):
        self._screen.fill(BLACK)
        self._snake.draw(self._screen)

        if self._apple is not None:
            self._screen.blit(self._apple.image, (self._apple.rect.x, self._apple.rect.y))

        texture_surface = self._font.render('{0}'.format(self._score), False, GREEN)
        self._screen.blit(texture_surface, (20, 20))

        pygame.display.flip()
#מציירת
    def run(self):
        game_sound.play(loops = -1)
        while not self._done:
            self._process_input()
            self._update()
            self._render()
            #מגביל fps
            self._clock.tick(5)
        
#סוגר  את המשחק
    def quit(self):
        pygame.quit()
#הרצה של המשחק
def main():
    game = SnakeGame()
    game.run()
    game.quit()

if __name__ == '__main__':
    main()