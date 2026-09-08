import math


def hex_cells(side_length: int) -> list[tuple[int, int]]:
    """Every valid axial (q, r) on a side-length-n hex-hex board."""
    radius = side_length - 1
    cells = []
    for q in range(-radius, radius + 1):
        for r in range(-radius, radius + 1):
            s = -q - r
            if max(abs(q), abs(r), abs(s)) <= radius:
                cells.append((q, r))
    return cells


def axial_to_pixel(q: int, r: int, hex_size: float) -> tuple[float, float]:
    """Pixel center of a pointy-top hex cell at axial (q, r), for a given hex_size (center-to-corner radius)."""
    x = hex_size * (math.sqrt(3) * q + math.sqrt(3) / 2 * r)
    y = hex_size * (1.5 * r)
    return x, y


def hex_corners(center_x: float, center_y: float, hex_size: float) -> list[tuple[float, float]]:
    """The 6 corner points of a pointy-top hexagon centered at (center_x, center_y)."""
    corners = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        corners.append((center_x + hex_size * math.cos(angle), center_y + hex_size * math.sin(angle)))
    return corners


def pixel_to_axial(x: float, y: float, hex_size: float) -> tuple[int, int]:
    """Axial (q, r) of the cell nearest to pixel (x, y) -- the inverse of axial_to_pixel."""
    r_frac = (2.0 / 3.0) * y / hex_size
    q_frac = x / (hex_size * math.sqrt(3)) - r_frac / 2.0
    return _round_to_axial(q_frac, r_frac)


def _round_to_axial(q_frac: float, r_frac: float) -> tuple[int, int]:
    """Rounds fractional cube coordinates to the nearest valid (integer) hex cell."""
    s_frac = -q_frac - r_frac
    q, r, s = round(q_frac), round(r_frac), round(s_frac)

    q_diff = abs(q - q_frac)
    r_diff = abs(r - r_frac)
    s_diff = abs(s - s_frac)

    if q_diff > r_diff and q_diff > s_diff:
        q = -r - s
    elif r_diff > s_diff:
        r = -q - s

    return int(q), int(r)
