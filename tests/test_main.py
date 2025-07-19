from mestolo.main import flatten_list

def test_flatten_list():
    l = [[1], [2, 3]]
    out = flatten_list(l)
    assert out == [1, 2, 3]
