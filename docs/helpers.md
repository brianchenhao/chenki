# Restaurant helpers

Chenki ships three pre-built helpers on `ChenkiClient` aimed at restaurant-domain workloads. Each one composes a prompt, sends it to the configured endpoint, and returns either a plain string or a typed dataclass.

All helpers are **prompt-injection-safe**: every user-supplied field is wrapped in `<user_content>` tags, with a final clause in the system prompt instructing the model to treat anything inside those tags as untrusted data. See [the prompts module](https://github.com/brianchenhao/chenki/blob/main/src/chenki/prompts/base.py) for the wrapping rule.

## `ask_about_menu`

Free-form Q&A grounded in a JSON menu.

```python
from chenki import ChenkiClient

client = ChenkiClient()

menu = [
    {"name": "Pad Thai",         "description": "stir-fried rice noodles with shrimp"},
    {"name": "Green Curry",      "description": "coconut curry with chicken and basil"},
    {"name": "Tom Yum",          "description": "hot-and-sour shrimp soup, mildly spicy"},
    {"name": "Mango Sticky Rice","description": "sweet sticky rice with mango"},
    {"name": "Spring Rolls",     "description": "crispy vegetable rolls"},
]

answer: str = client.ask_about_menu("Anything spicy and vegetarian?", menu)
print(answer)
```

**Return type:** `str` — a plain-English answer.

**Token budget:** target <1000 input tokens, <200 output tokens. Pass a short menu (a few dozen items max); long menus blow the context window on small models.

## `classify_dish`

Classify a single dish into structured fields. Returns a `DishClassification` dataclass.

```python
from chenki import ChenkiClient, DishClassification

client = ChenkiClient()

result: DishClassification = client.classify_dish(
    name="Nasi Lemak",
    description="rice with sambal, anchovies, peanuts, boiled egg",
)
print(result.cuisine)       # e.g. "Malaysian"
print(result.spice_level)   # one of: "none" | "mild" | "medium" | "hot"
print(result.dietary_tags)  # e.g. ["contains_egg", "contains_peanut"]
```

**Fields:**

| Field | Type | Constraints |
|---|---|---|
| `cuisine` | `str` | Free-form (e.g. `"Italian"`, `"Malay"`, `"Japanese"`). |
| `spice_level` | `Literal["none","mild","medium","hot"]` | Validated in `__post_init__`. |
| `dietary_tags` | `list[str]` | Free-form tags like `vegetarian`, `vegan`, `contains_egg`, `gluten_free`. |

**Robustness:** the helper retries once with a stricter prompt if the model's first response isn't valid JSON. If the retry also fails, it raises `ChenkiParseError` with the original raw text on `.raw`.

## `parse_order_text`

Extract a structured order from free-form text against a known menu. Returns a `ParsedOrder` dataclass.

```python
from chenki import ChenkiClient, ParsedOrder

client = ChenkiClient()

menu = [
    {"name": "Pad Thai",    "description": "stir-fried rice noodles"},
    {"name": "Green Curry", "description": "coconut chicken curry"},
]

order: ParsedOrder = client.parse_order_text(
    "Two pad thai, no peanuts. One green curry, mild. Dine in.",
    menu=menu,
)
for item in order.items:
    print(item.name, item.quantity, item.notes)
print("order notes:", order.notes)
```

**Fields:**

| Field | Type | Notes |
|---|---|---|
| `items` | `list[OrderItem]` | Each `OrderItem` has `name`, `quantity`, `notes`. |
| `notes` | `str` | Order-level notes (e.g. `"dine in"`, `"takeaway"`). |

**Robustness:** same retry-once-on-bad-JSON behaviour as `classify_dish`.

## Performance budget

These helpers were sized for the default Space (free HF tier, 2 vCPU, Qwen 2.5 1.5B Q4_K_M, ~20 tok/s output):

| Helper | Input tokens | Output tokens | Typical latency |
|---|---|---|---|
| `ask_about_menu` | <1000 | <200 | 8–25 s |
| `classify_dish` | <400 | <80 | 3–10 s |
| `parse_order_text` | <800 | <150 | 5–20 s |

If your prompt exceeds these budgets the helper is doing too much — split the work or summarise the menu first. The library will not refuse to send an oversize prompt, but the model's response quality drops sharply past ~1500 input tokens on small Qwen.

## Extending with your own templates

`RestaurantPrompts` is just one subclass of `PromptTemplate`. To register your own:

```python
from chenki import PromptTemplate, Message, ChenkiClient

class WinePairingPrompt(PromptTemplate):
    def build_messages(self, *, dish: str, options: list[str]):
        return [
            Message(role="system", content=(
                "Suggest one wine from the options list to pair with the dish. "
                "Answer in one short sentence."
            )),
            Message(role="user", content=(
                f"Dish: {self._wrap(dish)}\n"
                f"Options: {self._wrap_json(options)}"
            )),
        ]

client = ChenkiClient()
messages = WinePairingPrompt().render(dish="Steak frites", options=["Cabernet", "Riesling", "Pinot Noir"])
print(client.chat(messages).text)
```

`_wrap` and `_wrap_json` are the safe-wrapping helpers — always use them on user-supplied data, never raw f-strings.
