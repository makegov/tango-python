"""Tests for the `exact` count opt-in on the list endpoints that report estimated counts"""

import inspect
from unittest.mock import Mock, patch

import pytest

from tango import TangoClient

METHODS = ["list_opportunities", "list_notices", "list_contracts", "list_idvs"]


def _mock(mock_request, count_type):
    response = Mock()
    response.is_success = True
    response.json.return_value = {"count": 12345, "next": None, "previous": None, "results": []}
    response.content = b"{}"
    response.headers = {"X-Results-CountType": count_type}
    mock_request.return_value = response


@pytest.mark.parametrize("method", METHODS)
class TestExactCount:
    @patch("tango.client.httpx.Client.request")
    def test_sends_exact_when_asked(self, mock_request, method):
        _mock(mock_request, "exact")
        page = getattr(TangoClient(api_key="k"), method)(exact=True)
        assert mock_request.call_args.kwargs["params"]["exact"] == "true"
        assert page.count == 12345

    @patch("tango.client.httpx.Client.request")
    def test_omits_exact_by_default(self, mock_request, method):
        _mock(mock_request, "approximate")
        getattr(TangoClient(api_key="k"), method)()
        assert "exact" not in mock_request.call_args.kwargs["params"]

    def test_exact_is_keyword_only(self, method):
        param = inspect.signature(getattr(TangoClient, method)).parameters["exact"]
        assert param.kind is inspect.Parameter.KEYWORD_ONLY
        assert param.default is False
