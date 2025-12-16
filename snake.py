import random
import pygame

#צבעים
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

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
        self._last_x_change = self._x_change
        self._last_y_change = self._y_change
        self._grow_next_frame = False
    #תנועה
    def move(self, x_change, y_change):
        # מניעת תנועה בכיוון הפוך (למשל, מ-ימין ל-שמאל או מ-מעלה ל-מטה מיידית)
        if (x_change * -1) == self._last_x_change or (y_change * -1) == self._last_y_change:
            return # אם הכיוון הפוך, מתעלם מהקלט

        self._last_x_change = self._x_change # שומר את הכיוון הנוכחי כ"אחרון"
        self._last_y_change = self._y_change
        self._x_change = x_change
        self._y_change = y_change

    def update(self):
        #תנועת פיקסלים

        # Removing last segment if we don't grow -> delete
        if not self._grow_next_frame:
            old_segment = self._segments.pop()
            self._sprites.remove(old_segment)
        else:
            #grow -> not delete, מאפסים לפעם הבאה
            self._grow_next_frame = False

        # Adding a new segment
        x = self._segments[0].rect.x + self._x_change
        y = self._segments[0].rect.y + self._y_change
        segment = SnakeSegment(x, y)

        self._segments.insert(0, segment)
        self._sprites.add(segment)

        #עדכון כיוון
        self._last_x_change = self._x_change
        self._last_y_change = self._y_change
        
    def draw(self, screen):
        self._sprites.draw(screen)
    #התרסק
    def has_collided_with(self, other_sprite):
        return len(pygame.sprite.spritecollide(other_sprite, self._sprites, False)) > 0
    
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
        pygame.display.set_caption('SnapSnake')

        #יצירת ערוצי שמע:
        pygame.mixer.set_num_channels(2) # שני ערוצים: אחד לרקע, אחד לאפקטים
        self._background_channel = pygame.mixer.Channel(0) # ערוץ 0 לרקע
        self._effects_channel = pygame.mixer.Channel(1)    # ערוץ 1 לאפקטים
        self._background_channel.set_volume(0.2)
        self._effects_channel.set_volume(0.4)
        
        # טעינת צלילים
        self._game_sound = pygame.mixer.Sound('Sounds\\background.mpeg')
        self._death_sound = pygame.mixer.Sound('Sounds\\fail.mpeg')
        self._ate_sound = pygame.mixer.Sound('Sounds\\ate.mpeg')

        self._game_over_time = None
        self._game_over_reason = None

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
                self._background_channel.stop() # עצירה מלאה של הרקע
                self._effects_channel.play(self._death_sound) #הפעלת צליל מוות
                #עיכוב של 2.1 שניות
                self._game_over_time = pygame.time.get_ticks() + 2100
                self._game_over_reason = "Reason: Manual exit, clicked the X app button."
                return
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
                    self._background_channel.stop() # עצירה מלאה של הרקע
                    self._effects_channel.play(self._death_sound) #הפעלת צליל מוות
                    self._game_over_time = pygame.time.get_ticks() + 2100
                    self._game_over_reason = "Reason: Manual exit, clicked the Q button."
                    return
                if event.key == pygame.K_c:
                    main()

    def _update(self):
        if self._game_over_time is not None:
            # בדיקת סגירת משחק אחרי טיימר (Game Over)
            if pygame.time.get_ticks() > self._game_over_time:
                self._done = True
                return
            else:
                return
        
        self._snake.update()
        #מזמן תפוחים
        if self._apple is None:
            self._apple = Apple(
                random.randint(0, self._SCREEN_WIDTH - Segment._WIDTH),
                random.randint(0, self._SCREEN_HEIGHT - Segment._HEIGHT)
            )

        # Check collision between our Snake and the apple
        if self._snake.has_collided_with(self._apple):
            #stops background music
            self._background_channel.pause()
            #runs the apple eating sound
            self._effects_channel.play(self._ate_sound)

            self._score += 1
            self._apple = None
            self._snake._grow_next_frame = True
            #self._game_over_time = pygame.time.get_ticks() + 500

        # Check of game is over by self crash
        head = self._snake._segments[0] #בודק מהראש החדש
        for segment in self._snake._segments[1:]:  # לולאה על כל המקטעים חוץ מהראש
            if head.rect.x == segment.rect.x and head.rect.y == segment.rect.y: #יש מפגש
                #stops background music
                self._background_channel.pause()
                #runs the death sound
                self._effects_channel.play(self._death_sound)
                self._game_over_time = pygame.time.get_ticks() + 2100
                self._game_over_reason = "Reason: Hit itself."
                return

        # Check of game is over by bounds crash
        if self._snake.is_out_of_bounds(0, 0, self._SCREEN_WIDTH, self._SCREEN_HEIGHT):
            #stops background music
            self._background_channel.pause()
            #runs the death sound
            self._effects_channel.play(self._death_sound)
            self._game_over_time = pygame.time.get_ticks() + 2100
            self._game_over_reason = "Reason: Hit an edge."
            return

        #אם הצלילים האחרים כבויים, להפעיל את הרקע
        if not self._effects_channel.get_busy():
            #הפעלת רקע
            self._background_channel.unpause()

    #להריץ מסך
    def _render(self):
        self._screen.fill(BLACK)
        self._snake.draw(self._screen)

        if self._apple is not None:
            self._screen.blit(self._apple.image, (self._apple.rect.x, self._apple.rect.y))

        if self._game_over_time is not None: # משחק נגמר
            self._screen.blit(self._font.render("GAME OVER!", False, GREEN), (200, 150))
            self._screen.blit(self._font.render(self._game_over_reason, False, GREEN), (200, 180))
            self._screen.blit(self._font.render("Click 'c' to restart.", False, GREEN), (200, 210))

        texture_surface = self._font.render('{0}'.format(self._score), False, GREEN)
        self._screen.blit(texture_surface, (20, 20))

        pygame.display.flip()

    #מציירת
    def run(self):
        #loops=-1 - ניגון אינסופי
        self._background_channel.play(self._game_sound, loops=-1)
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