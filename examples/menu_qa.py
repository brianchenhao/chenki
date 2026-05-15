"""Ask chenki-llm a free-form question about a small restaurant menu."""

from chenki import ChenkiClient

MENU = [
    {"name": "Pad Thai", "description": "Stir-fried rice noodles with shrimp"},
    {"name": "Green Curry", "description": "Coconut curry with chicken and basil"},
    {"name": "Tom Yum", "description": "Hot and sour shrimp soup, mildly spicy"},
    {"name": "Mango Sticky Rice", "description": "Sweet sticky rice with mango"},
    {"name": "Spring Rolls", "description": "Crispy vegetable rolls"},
]

client = ChenkiClient()
answer = client.ask_about_menu("Anything spicy and vegetarian?", MENU)
print(answer)
