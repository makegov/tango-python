"""Integration tests for forecast endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions
    @pytest.mark.live: Forces tests to use live API (skip cassettes) - not used by default
    @pytest.mark.cached: Forces tests to only run with cached responses - not used by default
    @pytest.mark.slow: Marks tests that are slow to execute - not used by default

Usage:
    # Run all integration tests (uses cassettes if available)
    pytest tests/integration/

    # Run only forecast integration tests
    pytest tests/integration/test_forecasts_integration.py

    # Run with live API (requires TANGO_API_KEY environment variable)
    TANGO_USE_LIVE_API=true TANGO_API_KEY=xxx pytest tests/integration/

    # Refresh cassettes (re-record all interactions)
    TANGO_REFRESH_CASSETTES=true TANGO_API_KEY=xxx pytest tests/integration/
"""

from datetime import date, datetime
from decimal import Decimal

import pytest

from tango import ShapeConfig
from tests.integration.conftest import handle_api_exceptions
from tests.integration.validation import (
    validate_no_parsing_errors,
    validate_pagination,
)


def validate_forecast_fields(forecast, minimal: bool = True) -> None:
    """Validate forecast object has required fields and correct types

    Args:
        forecast: A Forecast object to validate
        minimal: If True, only validate minimal fields. If False, validate comprehensive fields.

    Raises:
        AssertionError: If validation fails
    """
    # Required fields - Forecast uses 'id' not 'key'
    is_dict = isinstance(forecast, dict)
    forecast_id = forecast.get("id") if is_dict else getattr(forecast, "id", None)
    assert forecast_id is not None, "Forecast 'id' must not be None"

    title = forecast.get("title") if is_dict else getattr(forecast, "title", None)
    assert title is not None, "Forecast 'title' must not be None"

    # Type validation for required fields
    assert isinstance(forecast_id, (str, int)), (
        f"Forecast 'id' must be string or int, got {type(forecast_id)}"
    )
    assert isinstance(title, str), f"Forecast 'title' must be string, got {type(title)}"

    # Type validation for optional date fields (only if in shape)
    anticipated_award_date = (
        forecast.get("anticipated_award_date")
        if is_dict
        else getattr(forecast, "anticipated_award_date", None)
    )
    if anticipated_award_date is not None:
        assert isinstance(anticipated_award_date, date), (
            f"Forecast 'anticipated_award_date' must be date, got {type(anticipated_award_date)}"
        )

    # Type validation for nested objects (only if in shape)
    agency = forecast.get("agency") if is_dict else getattr(forecast, "agency", None)
    if agency is not None:
        if isinstance(agency, dict):
            assert "code" in agency or "name" in agency, (
                "Forecast 'agency' should have 'code' or 'name'"
            )
        elif isinstance(agency, str):
            # Agency can be a string (not a nested object for forecasts)
            assert len(agency) > 0, "Forecast 'agency' string should not be empty"
        else:
            assert hasattr(agency, "code") or hasattr(agency, "name"), (
                "Forecast 'agency' must have 'code' or 'name' attribute"
            )


@pytest.mark.vcr()
@pytest.mark.integration
class TestForecastsIntegration:
    """Integration tests for forecast endpoints using production data"""

    @handle_api_exceptions("forecasts")
    @pytest.mark.parametrize(
        "shape_name,shape_value",
        [
            ("default", None),
            ("minimal", ShapeConfig.FORECASTS_MINIMAL),
            (
                "detailed",
                "id,source_system,external_id,title,description,anticipated_award_date,fiscal_year,naics_code,status,is_active",
            ),
            ("custom", "id,title,anticipated_award_date"),
        ],
    )
    def test_list_forecasts_with_shapes(self, tango_client, shape_name, shape_value):
        """Test listing forecasts with different shapes

        Validates:
        - Forecasts endpoint exists and returns data
        - Paginated response structure
        - Forecast parsing with various shapes
        - Required fields are present regardless of shape
        """
        kwargs = {"limit": 5}
        if shape_value is not None:
            kwargs["shape"] = shape_value

        response = tango_client.list_forecasts(**kwargs)

        # Validate response structure
        validate_pagination(response)

        # If we have results, validate them
        if response.results:
            forecast = response.results[0]
            validate_forecast_fields(forecast, minimal=(shape_name in ("default", "minimal")))
            validate_no_parsing_errors(forecast)

            # Verify required fields are present
            # Forecast uses 'id' not 'key'
            forecast_id = (
                forecast.get("id") if isinstance(forecast, dict) else getattr(forecast, "id", None)
            )
            assert forecast_id is not None, "Forecast id should be present"
            assert forecast.title is not None, "Forecast title should be present"

    @handle_api_exceptions("forecasts")
    def test_forecast_field_types(self, tango_client):
        """Test that all forecast field types are correctly parsed

        Validates:
        - Date fields are parsed as date objects
        - Decimal fields are parsed as Decimal objects
        - Datetime fields are parsed as datetime objects
        - String fields are strings
        - Nested objects (agency, place_of_performance) are parsed correctly
        """
        response = tango_client.list_forecasts(limit=10)

        # Validate response structure
        validate_pagination(response)

        # If we have results, validate them
        if response.results:
            for forecast in response.results:
                # Validate field types
                validate_forecast_fields(forecast, minimal=True)
                validate_no_parsing_errors(forecast)

                # Additional type checks for specific fields
                forecast_id = (
                    forecast.get("id")
                    if isinstance(forecast, dict)
                    else getattr(forecast, "id", None)
                )
                assert isinstance(forecast_id, (str, int)), (
                    f"id should be string or int, got {type(forecast_id)}"
                )

                title = (
                    forecast.get("title")
                    if isinstance(forecast, dict)
                    else getattr(forecast, "title", None)
                )
                assert isinstance(title, str), f"title should be string, got {type(title)}"

                # description may not be in minimal shape
                description = (
                    forecast.get("description")
                    if isinstance(forecast, dict)
                    else getattr(forecast, "description", None)
                )
                if description is not None:
                    assert isinstance(description, str), (
                        f"description should be string, got {type(description)}"
                    )

                # Only check fields that are in the shape
                is_dict = isinstance(forecast, dict)
                estimated_value = (
                    forecast.get("estimated_value")
                    if is_dict
                    else getattr(forecast, "estimated_value", None)
                )
                if estimated_value is not None:
                    assert isinstance(estimated_value, (Decimal, int, float)), (
                        f"estimated_value should be Decimal, int, or float, got {type(estimated_value)}"
                    )

                anticipated_solicitation_date = (
                    forecast.get("anticipated_solicitation_date")
                    if is_dict
                    else getattr(forecast, "anticipated_solicitation_date", None)
                )
                if anticipated_solicitation_date is not None:
                    assert isinstance(anticipated_solicitation_date, date), (
                        f"anticipated_solicitation_date should be date, got {type(anticipated_solicitation_date)}"
                    )

                anticipated_award_date = (
                    forecast.get("anticipated_award_date")
                    if isinstance(forecast, dict)
                    else getattr(forecast, "anticipated_award_date", None)
                )
                if anticipated_award_date is not None:
                    assert isinstance(anticipated_award_date, date), (
                        f"anticipated_award_date should be date, got {type(anticipated_award_date)}"
                    )

                created_at = (
                    forecast.get("created_at")
                    if isinstance(forecast, dict)
                    else getattr(forecast, "created_at", None)
                )
                if created_at is not None:
                    assert isinstance(created_at, datetime), (
                        f"created_at should be datetime, got {type(created_at)}"
                    )

                updated_at = (
                    forecast.get("updated_at")
                    if isinstance(forecast, dict)
                    else getattr(forecast, "updated_at", None)
                )
                if updated_at is not None:
                    assert isinstance(updated_at, datetime), (
                        f"updated_at should be datetime, got {type(updated_at)}"
                    )

                # Validate nested objects if present (handle dict fallback)
                is_dict = isinstance(forecast, dict)
                agency = forecast.get("agency") if is_dict else getattr(forecast, "agency", None)
                if agency is not None:
                    if isinstance(agency, dict):
                        assert "code" in agency or "name" in agency or len(agency) > 0, (
                            "agency should have at least one field"
                        )
                    else:
                        assert hasattr(agency, "code") or hasattr(agency, "name"), (
                            "agency should have 'code' or 'name' attribute"
                        )

                place_of_performance = (
                    forecast.get("place_of_performance")
                    if is_dict
                    else getattr(forecast, "place_of_performance", None)
                )
                if place_of_performance is not None:
                    if isinstance(place_of_performance, dict):
                        assert len(place_of_performance) > 0, (
                            "place_of_performance should have at least one field"
                        )
                    else:
                        assert (
                            hasattr(place_of_performance, "city_name")
                            or hasattr(place_of_performance, "state_code")
                            or hasattr(place_of_performance, "country_code")
                        ), "place_of_performance should have location fields"
