import pygame

class Button:
    """A clickable button for menus"""
    def __init__(self, x, y, width, height, text, color=(100, 150, 255), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hovered = False
        self.active_color = (150, 200, 255)
        self.idle_color = color
    
    def draw(self, surface, font):
        """Draw the button on the surface"""
        current_color = self.active_color if self.hovered else self.idle_color
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
        
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def update(self, mouse_pos):
        """Update hover state based on mouse position"""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        """Check if button was clicked"""
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0]


class MainMenu:
    """Main menu screen shown at game startup"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.active = True
        
        # Create buttons
        button_width = 200
        button_height = 60
        center_x = width // 2 - button_width // 2
        
        self.start_button = Button(center_x, height // 2 - 80, button_width, button_height, "START GAME")
        self.options_button = Button(center_x, height // 2 + 0, button_width, button_height, "OPTIONS")
        self.quit_button = Button(center_x, height // 2 + 80, button_width, button_height, "QUIT")
        self.buttons = [self.start_button, self.options_button, self.quit_button]
    
    def handle_input(self):
        """Handle menu input and return action"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        for button in self.buttons:
            button.update(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_pressed):
                if button == self.start_button:
                    self.active = False
                    return "start"
                elif button == self.options_button:
                    self.active = False
                    return "options"
                elif button == self.quit_button:
                    return "quit"
        
        return None
    
    def draw(self, surface):
        """Draw the main menu"""
        if not self.active:
            return
        
        # Background
        surface.fill((30, 30, 30))
        
        # Title
        font_large = pygame.font.Font(None, 80)
        title = font_large.render("GAME", True, (255, 200, 50))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 4))
        surface.blit(title, title_rect)
        
        # Buttons
        font_button = pygame.font.Font(None, 40)
        for button in self.buttons:
            button.draw(surface, font_button)
