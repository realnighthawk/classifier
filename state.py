"""The text the model classifies. It was trained on short previous requests and over-weights a longer one: past
about 250 characters of "Earlier request" the label follows the old text and ignores the new request (a goal
request read as `conversation` 0.84 after a long agent note). So the previous request is cut short."""

MAX_EARLIER_CHARS = 160   # the request being continued: its start says what it was (250+ flips real cases)
MAX_TEXT_CHARS = 600


def state_for(text: str, earlier: str | None) -> str:
    text = text[:MAX_TEXT_CHARS]
    if not earlier:
        return text
    # continuation format the model was trained on
    return f"Earlier request: {earlier[:MAX_EARLIER_CHARS]}\nNew request: {text}"
