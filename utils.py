def rgb_to_hhss(r, g, b) -> int:
    """
    RGB (0..255 each) -> 16-bit 0xHHSS (Hue byte, Saturation byte), Value assumed = 255.
    No libraries.
    """
    # Clamp
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))

    # Normalize to 0..1
    r1, g1, b1 = r / 255.0, g / 255.0, b / 255.0
    cmax = max(r1, g1, b1)
    cmin = min(r1, g1, b1)
    delta = cmax - cmin

    # Hue in [0,1)
    if delta == 0:
        h = 0.0
    elif cmax == r1:
        h = ((g1 - b1) / delta) % 6.0
    elif cmax == g1:
        h = (b1 - r1) / delta + 2.0
    else:
        h = (r1 - g1) / delta + 4.0
    h = (h / 6.0) % 1.0  # normalize

    # Saturation in [0,1]
    s = 0.0 if cmax == 0 else (delta / cmax)

    # Map to bytes
    H = int(round(h * 255)) % 256  # wrap 1.0 -> 0
    S = int(round(s * 255))
    return (H << 8) | S
