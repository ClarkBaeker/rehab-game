import pygame

def render_text(surface, text, font_size, color, position):
    font = pygame.font.SysFont(None, font_size)
    text_surf = font.render(text, True, color)
    surface.blit(text_surf, position)

def render_centered_test(surface, text, font_size, color, position):
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    
    # Get the rect of the text surface
    text_rect = text_surface.get_rect(center=position)
    # Blit the text surface at the center of the screen
    surface.blit(text_surface, text_rect)

def load_image(path):
    return pygame.image.load(path)

def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except pygame.error:
        print(f"Could not load sound {path}")
        return None

