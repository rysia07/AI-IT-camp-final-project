import pygame

class Button:
    """A clickable button for the pause menu"""
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


class PauseMenu:
    """Pause menu that overlays the game"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.active = False
        
        # Create buttons
        button_width = 200
        button_height = 50
        center_x = width // 2 - button_width // 2
        
        self.resume_button = Button(center_x, height // 2 - 60, button_width, button_height, "RESUME")
        self.restart_button = Button(center_x, height // 2 + 20, button_width, button_height, "RESTART")
        self.buttons = [self.resume_button, self.restart_button]
    
    def toggle(self):
        """Toggle pause menu on/off"""
        self.active = not self.active
    
    def handle_input(self):
        """Handle pause menu input and return action"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        for button in self.buttons:
            button.update(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_pressed):
                if button == self.resume_button:
                    self.toggle()
                    return "resume"
                elif button == self.restart_button:
                    return "restart"
        
        return None
    
    def draw(self, surface):
        """Draw the pause menu overlay"""
        if not self.active:
            return
        
        # Semi-transparent dark overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Title
        font_large = pygame.font.Font(None, 64)
        title = font_large.render("PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 4))
        surface.blit(title, title_rect)
        
        # Buttons
        font_button = pygame.font.Font(None, 36)
        for button in self.buttons:
            button.draw(surface, font_button)
