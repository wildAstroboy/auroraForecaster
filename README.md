# Aurora Tracker

A small Python tool that pulls real-time space-weather data from NOAA's Space
Weather Prediction Center, finds where aurora visibility is currently most
likely, and renders it as an interactive map centered on your own location.

**Status: 🚧 Work in progress.** Core NOAA data fetching and map rendering
work, but the project has some rough edges and unfinished pieces — see
[Known Issues](#known-issues--todo) below.

## Features

- Fetches the latest OVATION aurora forecast (lat/lon/probability grid) from
  NOAA
- Fetches planetary K-index (current + forecast) and X-ray solar flare data
  from NOAA
- Auto-detects your approximate location via IP geolocation
- Renders an interactive dark-mode world map (Plotly density map) showing
  aurora probability, with your location pinned
- Opens the generated map in your default browser

## Project Structure

`main.py` and `map.py` import from `clients/` and `map/` packages
respectively, so the intended layout is:

```
.
├── main.py                # Entry point — builds the map and opens it
├── requirements.txt       # Python dependencies
├── clients/
│   └── NOAA_data.py       # NOAA SWPC API clients (Kp index, X-ray flares, aurora forecast)
└── map/
    ├── map.py             # Builds the Plotly map (create_map)
    └── aurora_location.html   # Generated output map (created at runtime)
```

## Setup

1. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python main.py
```

This will:
1. Fetch the latest aurora probability grid from NOAA
2. Geolocate your machine via IP
3. Build an interactive map and save it to `map/aurora_location.html`
4. Open the map in your default browser

## Data Sources

- **NOAA Space Weather Prediction Center** — [services.swpc.noaa.gov](https://services.swpc.noaa.gov/)
  - Planetary K-index (current + forecast)
  - X-ray flare data (latest + 7-day)
  - OVATION aurora probability grid

## Known Issues / TODO
- No tests yet.