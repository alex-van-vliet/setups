def reset():
    return '\033[39m'


def rgb(r: int, g: int, b: int):
    if r < 0 or r > 255:
        raise ValueError('invalid red component')
    if g < 0 or g > 255:
        raise ValueError('invalid green component')
    if b < 0 or b > 255:
        raise ValueError('invalid blue component')
    return f'\033[38;2;{r};{g};{b}m'


def number(n: int):
    if n < 0 or n > 255:
        raise ValueError('invalid color number')
    return f'\033[38;5;{n}m'
