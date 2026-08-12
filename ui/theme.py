SCREEN_SIZE = (1280, 760)
FPS = 60
TITLE = "Griductive Solver"

BG = (17, 22, 35)
PANEL = (27, 35, 53)
PANEL_2 = (35, 45, 66)
TEXT = (236, 242, 255)
MUTED = (151, 165, 190)
ACCENT = (74, 222, 192)
ACCENT_2 = (107, 125, 255)
CRIMINAL = (236, 87, 100)
INNOCENT = (73, 196, 130)
WARNING = (244, 190, 76)
BORDER = (65, 81, 111)
CARD_BACK = (42, 53, 78)
WHITE = (255, 255, 255)


_FONT_CACHE = {}


def font(size, bold=False):
    """Return a cached font face.

    pygame.font.SysFont rescans the system font list on every call, which is
    far too slow to run once per drawn string.
    """
    import pygame

    key = (int(size), bool(bold))
    face = _FONT_CACHE.get(key)
    if face is None:
        face = pygame.font.SysFont("segoeui", int(size), bold=bold)
        _FONT_CACHE[key] = face
    return face

