"""Config flow for Starlink Regional Metrics integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

API_URL = "https://api.starlink.com/public-files/metrics_residential.json"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("region_id"): str,
        vol.Optional("region_name"): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    region_id = data["region_id"]

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    raise CannotConnect(f"API returned status {response.status}")

                api_data = await response.json()

                # Check if region exists in either admin0Metrics or admin1Metrics
                if "admin0Metrics" in api_data and region_id in api_data["admin0Metrics"]:
                    return {"title": f"Starlink Region {data.get('region_name', region_id)}"}
                elif "admin1Metrics" in api_data and region_id in api_data["admin1Metrics"]:
                    return {"title": f"Starlink Region {data.get('region_name', region_id)}"}
                else:
                    raise InvalidRegion(f"Region ID {region_id} not found in API data")

    except aiohttp.ClientError as err:
        raise CannotConnect(f"Error connecting to API: {err}") from err
    except Exception as err:
        _LOGGER.exception("Unexpected exception")
        raise CannotConnect(f"Unexpected error: {err}") from err


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Starlink Regional Metrics."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidRegion:
                errors["base"] = "invalid_region"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Prevent duplicate entries for the same region
                await self.async_set_unique_id(user_input["region_id"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "region_id_example": "dXJuOm1ieGJuZDpDaEpFOnY0"
            },
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidRegion(HomeAssistantError):
    """Error to indicate the region ID is invalid."""
