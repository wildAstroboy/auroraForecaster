# 🌌 Aurora Borealis Real-Time Forecast Dashboard

An interactive, single-page geospatial dashboard that visualizes real-time solar activity and aurora visibility chances. Built with Python using **Plotly Graph Objects**, **SciPy**, and live data feeds from the **NOAA Space Weather Prediction Center (SWPC)**.

The dashboard renders as one dark-themed Plotly figure with three tabs — **Aurora Chance**, **KP Index**, and **X-Ray Flux** — that swap in and out via trace-visibility toggling, so the whole thing ships as a single static HTML file.

---

## 🚀 Key Features

*   **Smooth Geographic Contours**: Translates coarse 1-degree global telemetry from NOAA into continuous auroral ovals using localized **Gaussian spatial filtering**.
*   **Tabbed Single-Figure Dashboard**: One Plotly figure with in-page tabs for the aurora map, the Kp index timeline, and X-ray flux — no page reloads, just trace visibility swaps.
*   **Value-Mapped Timeline Engine**: Kp Index bar chart color-coded row-by-row according to active aviation and power grid storm thresholds.
*   **X-Ray Flux Monitoring**: Plots GOES-18 and GOES-19 short- and long-wavelength X-ray flux on a log-scale timeline.
*   **Latest Alerts Banner**: Surfaces the most recent NOAA space weather alert as an annotation above the map.
*   **Automated Localization**: Resolves client network endpoints via IP geocoding to overlay a "You Are Here" waypoint pin.
*   **Fully Interactive Standalone Build**: Compiles into a single static HTML page supporting pan, scroll-zoom, and tab switching — no server required.

---

## 🛠️ Architecture & Data Pipeline

```
[ NOAA SWPC API ] ──> [ Fortran-Order Matrix Reshape ] ──> [ SciPy Gaussian Blur ] ──> [ Plotly Figure w/ Tabbed updatemenus ] ──> [ HTML Export ]
```

1. **Telemetry Ingestion**: Pulls the live 30-minute aurora tracking grid, the Kp forecast, the latest space weather alert, and GOES-18/19 X-ray flux (primary + secondary, short + long wavelength) from NOAA SWPC.
2. **Matrix Alignment**: Reconstructs the aurora coordinate array into an explicit 181 × 360 column-major (Fortran order) grid matrix to prevent spatial shearing artifacts across oceans.
3. **Spatial Blending**: Filters the grid via `scipy.ndimage.gaussian_filter` to smooth jagged pixel drop-off into natural atmospheric color shapes.
4. **Layout Assembly**: Builds every trace (density map, location pin, Kp bars, four X-ray flux lines) into a single `go.Figure`, then uses `updatemenus` buttons to toggle trace visibility and swap axis/mapbox/title config between the three tabs.
5. **Map Tiles**: Renders a `carto-darkmatter` base style plus an authenticated CARTO raster tile overlay (requires `CARTO_API_KEY`).

---

## 📂 Project Structure

```text
├── clients/
│   └── NOAA_data.py           # NoaaData class — pulls aurora, Kp, alerts, and X-ray data from NOAA
├── map/
│   ├── aurora_location.html   # Generated dashboard output (created at runtime)
│   └── map.py                 # create_map() — builds the tabbed Plotly figure
├── main.py                    # Fetches data, checks for failures, builds and opens the dashboard
├── .env                       # Local only, not committed — holds CARTO_API_KEY
├── requirements.txt           # Dependency constraints
└── README.md                  # System documentation
```

---

## 💻 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/wildAstroboy/auroraForecast.git
cd auroraForecast
```

### 2. Install Dependencies
Ensure you have Python 3.10+ installed, then:
```bash
pip install -r requirements.txt
```

### 3. Set Up Your CARTO API Key
The map's base tile layer uses an authenticated CARTO raster endpoint. Create a `.env` file in the project root:
```text
CARTO_API_KEY=your_carto_api_key_here
```
`main.py` loads this via `python-dotenv` at startup — the dashboard will still build without it, but the raster tile layer won't load.

### 4. Run the Pipeline
```bash
python main.py
```
This fetches live NOAA payloads, builds the dashboard, and opens `map/aurora_location.html` in your default browser.

---

## 📊 Visual Reference Configurations

### Aurora Probability Tiers (Map Layer Colorbar)
*   🟢 **Green (10%–39%)**: Low/unsettled peripheral auroral activity glow.
*   🟪 **Purple (40%–74%)**: Active visibility potential. High chance of photographic capture.
*   🔴 **Red (75%–100%)**: Intense/storm-level overhead visible aurora display.

<img width="1714" height="956" alt="Screenshot 2026-08-27 at 11 12 10 AM" src="https://github.com/user-attachments/assets/857f63a1-7681-4322-8b47-81ef67909202" />

### Kp Index Threat Scale (Timeline Bars)

| Kp Metric | Associated Color | Status Condition |
| :--- | :--- | :--- |
| **$\ge$ 9** | 🟤 Dark Red | G5 Extreme Geomagnetic Storm |
| **8** | 🔴 Red | G4 Severe Geomagnetic Storm |
| **7** | 🟠 Orange | G3 Strong Geomagnetic Storm |
| **6** | 🟡 Light Orange | G2 Moderate Geomagnetic Storm |
| **5** | 🟡 Yellow | G1 Minor Storm Threshold |
| **< 5** | 🟢 Bright Green | Quiet / Unsettled Background |

<img width="1715" height="957" alt="Screenshot 2026-08-27 at 11 12 24 AM" src="https://github.com/user-attachments/assets/1e30c226-feb1-4c65-8d5a-6b0e848776e3" />

### X-Ray Flux Tab
Plots four series — GOES-18 Short, GOES-18 Long, GOES-19 Short, GOES-19 Long — on a log-scale Y axis (Watts/m²), letting you cross-check flare activity against the primary and secondary GOES satellites.

---

## 📝 License

Distributed under the MIT License.

---

## 📡 Data Sourcing Acknowledgments
* Data feeds provided by the **National Oceanic and Atmospheric Administration (NOAA) Space Weather Prediction Center**.
* Map tiles styled via **Carto Darkmatter**, with raster tiles served by CARTO.