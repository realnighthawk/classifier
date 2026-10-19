from state import MAX_EARLIER_CHARS, MAX_TEXT_CHARS, state_for


def test_a_request_with_nothing_before_it_is_the_state():
    assert state_for("keep dining under $200", None) == "keep dining under $200"


def test_a_long_previous_message_never_pushes_the_new_request_out():
    state = state_for("keep dining under $200", "x" * 5000)
    assert state == "Earlier request: " + "x" * MAX_EARLIER_CHARS + "\nNew request: keep dining under $200"


def test_the_new_request_is_bounded_too():
    assert len(state_for("y" * 5000, None)) == MAX_TEXT_CHARS


if __name__ == "__main__":
    test_a_request_with_nothing_before_it_is_the_state()
    test_a_long_previous_message_never_pushes_the_new_request_out()
    test_the_new_request_is_bounded_too()
    print("ok")
