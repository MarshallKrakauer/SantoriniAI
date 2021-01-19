"""Button used in pygame selections."""
import pygame
import pygame.freetype

SIZE = (800, 600) #(width <-->, height)
SCREEN = pygame.display.set_mode(SIZE)

class Button(pygame.sprite.Sprite):
    """
    Button that grows in size when hovered over.

    Helps from: https://programmingpixels.com/handling-a-title-
                screen-game-flow-and-buttons-in-pygame.html
    Attributes

    mouse_over : bool
        Ture if a mouse is hovering over. used to make button larger
    images : list
        list of words that button will show
    rectangles : list
        list of background rectangles for words
    multiplier: float
        how much image increases when its moused over.
        multipler of 1 makes a static image
    """

    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb,
                 multiplier = 1.2):

        self.mouse_over = False  # indicates if the mouse is over the element
         # default image
        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb)

        # image when hovering over
        highlighted_image = create_surface_with_text(
            text=text,
            font_size=font_size * multiplier, text_rgb=text_rgb, bg_rgb=bg_rgb)

        self.images = [default_image, highlighted_image]

        self.rectangles = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]

        # Calls init on parent class
        super().__init__()

    @property
    def image(self):
        """
        Change between small and large button.

        Returns
        -------
        pygame image
            larger or smaller version of button
        """
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        """
        Change between small and large button.

        Sister function of image

        Returns
        -------
        pygame image
            larger or smaller version of button
        """
        return self.rectangles[1] if self.mouse_over else self.rectangles[0]

    def update(self, mouse_pos):
        """
        Change value of mouse_over, which is used for draw and check_press.

        Parameters
        ----------
        mouse_pos : tuple
            (x,y) coordinates of position
        """
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
        else:
            self.mouse_over = False

    def check_press(self, mouse_pos):
        """Check if user pressed the button."""
        return self.rect.collidepoint(mouse_pos)

    def draw(self):
        """Draws element onto a surface."""
        SCREEN.blit(self.image, self.rect)

def create_surface_with_text(text, font_size, text_rgb, bg_rgb):
    """Return surface with text written on."""
    font = pygame.freetype.SysFont("Courier", font_size, bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()