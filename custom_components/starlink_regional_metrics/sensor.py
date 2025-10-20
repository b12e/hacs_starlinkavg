"""Sensor platform for Starlink Regional Metrics."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime, UnitOfDataRate
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    get_last_statistics,
)

from . import StarlinkMetricsCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "latency_p20": {
        "name": "Latency P20",
        "unit": UnitOfTime.MILLISECONDS,
        "icon": "mdi:timer-outline",
        "device_class": SensorDeviceClass.DURATION,
    },
    "latency_p50": {
        "name": "Latency P50 (Median)",
        "unit": UnitOfTime.MILLISECONDS,
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
    },
    "latency_p80": {
        "name": "Latency P80",
        "unit": UnitOfTime.MILLISECONDS,
        "icon": "mdi:timer",
        "device_class": SensorDeviceClass.DURATION,
    },
    "download_p20": {
        "name": "Download Speed P20",
        "unit": UnitOfDataRate.MEGABITS_PER_SECOND,
        "icon": "mdi:download",
        "device_class": SensorDeviceClass.DATA_RATE,
    },
    "download_p50": {
        "name": "Download Speed P50 (Median)",
        "unit": UnitOfDataRate.MEGABITS_PER_SECOND,
        "icon": "mdi:download",
        "device_class": SensorDeviceClass.DATA_RATE,
    },
    "download_p80": {
        "name": "Download Speed P80",
        "unit": UnitOfDataRate.MEGABITS_PER_SECOND,
        "icon": "mdi:download",
        "device_class": SensorDeviceClass.DATA_RATE,
    },
    "upload_p20": {
        "name": "Upload Speed P20",
        "unit": UnitOfDataRate.MEGABITS_PER_SECOND,
        "icon": "mdi:upload",
        "device_class": SensorDeviceClass.DATA_RATE,
    },
    "upload_p50": {
        "name": "Upload Speed P50 (Median)",
        "unit": UnitOfDataRate.MEGABITS_PER_SECOND,
        "icon": "mdi:upload",
        "device_class": SensorDeviceClass.DATA_RATE,
    },
    "upload_p80": {
        "name": "Upload Speed P80",
        "unit": UnitOfDataRate.MEGABITS_PER_SECOND,
        "icon": "mdi:upload",
        "device_class": SensorDeviceClass.DATA_RATE,
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Starlink Regional Metrics sensors."""
    coordinator: StarlinkMetricsCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        StarlinkMetricsSensor(coordinator, entry, sensor_type)
        for sensor_type in SENSOR_TYPES
    ]

    async_add_entities(entities)


class StarlinkMetricsSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Starlink Regional Metrics sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: StarlinkMetricsCoordinator,
        entry: ConfigEntry,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.sensor_type = sensor_type
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_name = SENSOR_TYPES[sensor_type]["name"]
        self._attr_native_unit_of_measurement = SENSOR_TYPES[sensor_type]["unit"]
        self._attr_icon = SENSOR_TYPES[sensor_type]["icon"]
        self._attr_device_class = SENSOR_TYPES[sensor_type]["device_class"]
        self._region_id = entry.data["region_id"]

        # Device info for grouping sensors
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Starlink Region {entry.data.get('region_name', self._region_id)}",
            "manufacturer": "Starlink",
            "model": "Regional Metrics",
        }

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.sensor_type)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        super()._handle_coordinator_update()

        # Record to long-term statistics
        if self.coordinator.data is not None:
            self._async_record_statistics()

    def _async_record_statistics(self) -> None:
        """Record sensor data to long-term statistics."""
        value = self.native_value
        if value is None:
            return

        statistic_id = f"{DOMAIN}:{self.sensor_type}_{self._region_id}"

        # Create metadata
        metadata = StatisticMetaData(
            has_mean=True,
            has_sum=False,
            name=f"{self._attr_name}",
            source=DOMAIN,
            statistic_id=statistic_id,
            unit_of_measurement=self._attr_native_unit_of_measurement,
        )

        # Create statistics data point
        now = datetime.now()
        stat = StatisticData(
            start=now,
            mean=value,
            state=value,
        )

        # Add to long-term statistics
        async_add_external_statistics(
            self.hass,
            metadata,
            [stat],
        )

        _LOGGER.debug(
            "Recorded statistic for %s: %s %s",
            statistic_id,
            value,
            self._attr_native_unit_of_measurement,
        )
