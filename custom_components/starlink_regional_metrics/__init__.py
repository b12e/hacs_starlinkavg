"""The Starlink Regional Metrics integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import aiohttp

_LOGGER = logging.getLogger(__name__)

DOMAIN = "starlink_regional_metrics"
PLATFORMS = [Platform.SENSOR]

API_URL = "https://api.starlink.com/public-files/metrics_residential.json"
UPDATE_INTERVAL = timedelta(days=7)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Starlink Regional Metrics from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = StarlinkMetricsCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class StarlinkMetricsCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Starlink metrics data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.region_id = entry.data["region_id"]

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Error fetching data: {response.status}")

                    data = await response.json()

                    # Search in both admin0Metrics and admin1Metrics
                    region_data = None
                    if "admin0Metrics" in data and self.region_id in data["admin0Metrics"]:
                        region_data = data["admin0Metrics"][self.region_id]
                    elif "admin1Metrics" in data and self.region_id in data["admin1Metrics"]:
                        region_data = data["admin1Metrics"][self.region_id]

                    if region_data is None:
                        raise UpdateFailed(f"Region ID {self.region_id} not found in API data")

                    return region_data

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err
