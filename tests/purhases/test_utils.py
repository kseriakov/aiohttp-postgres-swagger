import pytest
from aiohttp.test_utils import make_mocked_request
from aiohttp.web import HTTPBadRequest

from purchases.utils import get_id_from_request


def test_get_id_from_request():
    id = 1
    request = make_mocked_request(method="GET", path="/", match_info={"id": id})
    getting_id = get_id_from_request(request)
    assert getting_id == id


def test_incorrect_get_id_from_request():
    request = make_mocked_request(method="GET", path="/", match_info={"id": ""})
    with pytest.raises(HTTPBadRequest):
        getting_id = get_id_from_request(request)
