# Starlink Regional Metrics for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant integration that fetches regional average speeds and latency metrics from Starlink's public API.

## Features

- Fetches regional Starlink metrics including:
  - Latency (P20, P50/median, P80 percentiles)
  - Download speeds (P20, P50/median, P80 percentiles)
  - Upload speeds (P20, P50/median, P80 percentiles)
- Automatic weekly updates (Starlink themselves update the metrics once a month on an unknown date)
- Historical data recording to Home Assistant long-term statistics
- UI-based configuration via Config Flow
- Supports all regions available in Starlink's public metrics API

## Installation

### HACS (Recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed
2. Add this repository as a custom repository in HACS:
   - Click on HACS in the sidebar
   - Click on "Integrations"
   - Click the three dots in the top right corner
   - Select "Custom repositories"
   - Add `https://github.com/b12e/hacs_starlinkavg` as an Integration
3. Click "Download" on the Starlink Regional Metrics card
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/starlink_regional_metrics` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "Starlink Regional Metrics"
4. Enter your region ID (e.g., `dXJuOm1ieGJuZDpDaEpFOnY0`)
5. Optionally, enter a friendly name for your region
6. Click Submit

### Finding Your Region ID

#### Automatic
You can try to find your region by entering the values the Starlink website displays, using this tool: https://starlink-region-finder.b12e.be/

#### Manual
Your region ID can be found in the Starlink metrics API. To find available regions:

1. Visit https://api.starlink.com/public-files/metrics_residential.json
2. Search for your country or region
3. Copy the region identifier (the key before the metrics data)


Example region IDs:
- `dXJuOm1ieGJuZDpDaEpFOnY0` (example region)

## Sensors

The integration creates 9 sensors for your region:

### Latency Sensors
- `sensor.starlink_region_XXX_latency_p20` - 20th percentile latency (ms)
- `sensor.starlink_region_XXX_latency_p50` - Median latency (ms)
- `sensor.starlink_region_XXX_latency_p80` - 80th percentile latency (ms)

### Download Speed Sensors
- `sensor.starlink_region_XXX_download_speed_p20` - 20th percentile download (Mbps)
- `sensor.starlink_region_XXX_download_speed_p50` - Median download (Mbps)
- `sensor.starlink_region_XXX_download_speed_p80` - 80th percentile download (Mbps)

### Upload Speed Sensors
- `sensor.starlink_region_XXX_upload_speed_p20` - 20th percentile upload (Mbps)
- `sensor.starlink_region_XXX_upload_speed_p50` - Median upload (Mbps)
- `sensor.starlink_region_XXX_upload_speed_p80` - 80th percentile upload (Mbps)

## Data Updates

- The integration fetches new data every **7 days** (weekly)
- All sensor values are automatically recorded to Home Assistant's long-term statistics so you can track Starlink's progress in speeds for your region
- Historical data can be viewed in the sensor history and statistics graphs

## Percentile Explanation

The metrics use percentile rankings:
- **P20**: 20th percentile - represents slower connections in the region
- **P50**: 50th percentile (median) - represents typical performance
- **P80**: 80th percentile - represents faster connections in the region

This provides a comprehensive view of network performance across different conditions.

## Data Source

This integration uses Starlink's public metrics API:
- API URL: https://api.starlink.com/public-files/metrics_residential.json
- Data is provided by Starlink and updated periodically

## Troubleshooting

### Integration not showing up
- Ensure you've restarted Home Assistant after installation
- Check the Home Assistant logs for any error messages

### Region ID not found
- Verify your region ID exists in the API data
- Visit the API URL directly to confirm your region is listed

### No data updates
- The integration updates weekly by default
- Check the Home Assistant logs for any API connection errors
- Verify you have internet connectivity

## Support

For issues, feature requests, or questions:
- [Open an issue](https://github.com/b12e/hacs_starlinkavg/issues)

## License

This project is licensed under the MIT License.

## Disclaimer

This integration is not affiliated with, endorsed by, or in any way officially connected to Starlink or SpaceX. It uses publicly available data from Starlink's API.
