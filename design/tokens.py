
"""Tokens de design: fonte única de verdade para cores e medidas."""

# Cores extraídas da logo Tour 360 VR
BRAND = {
    "blue":   "#4AA3DA",
    "orange": "#FFA733",
    "green":  "#9DBE5A",
    "coral":  "#F76C4A",
    "red":    "#FF3131",
}

COLORS = {
    # Base dark
    "bg":            "#0B0E14",
    "bg_glow":       "#16213A",
    # Superfícies de vidro
    "glass":         "rgba(22, 31, 48, 0.55)",
    "glass_strong":  "rgba(22, 31, 48, 0.82)",
    "glass_hover":   "rgba(37, 45, 66, 0.70)",
    "border":        "rgba(255, 255, 255, 0.10)",
    "border_hover":  "rgba(255, 255, 255, 0.30)",
    # Texto
    "text":          "#E6EDF7",
    "text_strong":   "#FFFFFF",
    "text_muted":    "#8E9BAE",
    # Acentos
    "accent":        BRAND["blue"],
    "accent_2":      BRAND["orange"],
    "success":       BRAND["green"],
    "warning":       BRAND["orange"],
    "danger":        BRAND["red"],
}

GRADIENT_BRAND = (
    f"linear-gradient(90deg, {BRAND['orange']}, {BRAND['blue']}, "
    f"{BRAND['green']}, {BRAND['coral']})"
)

RADIUS = {"sm": "8px", "md": "12px", "lg": "18px", "pill": "999px"}
BLUR = "18px"
SHADOW = {
    "sm": "0 2px 8px rgba(0, 0, 0, 0.25)",
    "md": "0 8px 32px rgba(0, 0, 0, 0.35)",
    "glow": f"0 0 18px rgba(74, 163, 218, 0.35)",
}
SPACING = {"xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "36px"}
FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
