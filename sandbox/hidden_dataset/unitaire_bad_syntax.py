def test_add():
    assert add(2, 2) == 4

def test_divide():
    with pytest.raises(ValueError):
        divide(1, 0)