from ui.theme import font


# Rendering a glyph run and measuring a wrap are both expensive enough that a
# 5x5 board would drop below 10 FPS without these caches.
_CACHE_LIMIT = 2048
_RENDER_CACHE = {}
_WRAP_CACHE = {}


def _render(text, size, bold, color):
    key = (text, int(size), bool(bold), tuple(color))
    image = _RENDER_CACHE.get(key)
    if image is None:
        image = font(size, bold).render(text, True, color)
        if len(_RENDER_CACHE) >= _CACHE_LIMIT:
            _RENDER_CACHE.clear()
        _RENDER_CACHE[key] = image
    return image


def draw_text(surface, text, position, size=20, color=(255, 255, 255), bold=False, anchor="topleft"):
    image = _render(str(text), size, bold, color)
    rect = image.get_rect()
    setattr(rect, anchor, position)
    surface.blit(image, rect)
    return rect


def fit_text(text, max_width, size=20, bold=False):
    """Shorten text with an ellipsis until it fits inside max_width."""
    text = str(text)
    face = font(size, bold)
    if face.size(text)[0] <= max_width:
        return text
    trimmed = text
    while trimmed and face.size(f"{trimmed}…")[0] > max_width:
        trimmed = trimmed[:-1]
    return f"{trimmed}…" if trimmed else ""


def draw_text_fitted(
    surface, text, position, max_width, size=20, color=(255, 255, 255),
    bold=False, anchor="topleft",
):
    """Like draw_text, but never lets a long label bleed outside its box."""
    return draw_text(
        surface, fit_text(text, max_width, size, bold),
        position, size, color, bold, anchor,
    )


def wrap_lines(text, max_width, size=18, bold=False):
    key = (str(text), int(max_width), int(size), bool(bold))
    lines = _WRAP_CACHE.get(key)
    if lines is None:
        face = font(size, bold)
        words = str(text).split()
        result, current = [], ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if face.size(candidate)[0] <= max_width:
                current = candidate
            else:
                if current:
                    result.append(current)
                current = word
        if current:
            result.append(current)
        lines = tuple(result) or ("",)
        if len(_WRAP_CACHE) >= _CACHE_LIMIT:
            _WRAP_CACHE.clear()
        _WRAP_CACHE[key] = lines
    return list(lines)


def draw_wrapped(surface, text, rect, size=18, color=(255, 255, 255), bold=False, line_gap=5):
    y = rect.top
    for line in wrap_lines(text, rect.width, size, bold):
        image = _render(line, size, bold, color)
        surface.blit(image, (rect.left, y))
        y += image.get_height() + line_gap
        if y > rect.bottom:
            break
    return y
