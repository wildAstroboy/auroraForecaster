# 🌌 Aurora Borealis Real-Time Forecast Dashboard

An interactive, high-resolution geospatial dashboard that visualizes real-time solar activity and aurora visibility chances. Built with Python using **Plotly Graph Objects**, **SciPy**, and live data feeds from the **NOAA Space Weather Prediction Center (SWPC)**.

The interface is optimized as a single-page dark dashboard featuring a smooth, downsampled contour map of aurora visibility coupled with a color-coded geomagnetic storm historical timeline (`Kp Index`).

---

## 🚀 Key Features

*   **Smooth Geographic Contours**: Translates coarse 1-degree global telemetry from NOAA into continuous auroral ovals using localized **Gaussian spatial filtering**.
*   **Widescreen Grid Optimization**: Allocates 75% of vertical screen space to the living map environment while managing performance by decimation logic.
*   **Value-Mapped Timeline Engine**: Features a Kp Index bar chart color-coded row-by-row according to active aviation and power grid storm thresholds.
*   **Automated Localization**: Resolves client network endpoints seamlessly using IP geocoding to overlay a precise "You Are Here" waypoint marker pin.
*   **Fully Interactive Standalone Build**: Compiles directly into a compressed, performant, static HTML page supporting native pan, scroll-zoom, and responsive layout structures.
*   **Latest Alerts Section**: Shows real-time notifications, warnings, and watches for solar and geomagnetic activity.

---

## 🛠️ Architecture & Data Pipeline

[ NOAA SWPC API ] ──> [ Fortran-Order Matrix Reshape ] ──> [ SciPy Gaussian Blur ] ──> [ Plotly Canvas Subplots ] ──> [ HTML Export ]

1. **Telemetry Ingestion**: Grabs the live 30-minute aurora tracking arrays (65,160 geographic coordinate pairs).
2. **Matrix Alignment**: Reconstructs data rows into an explicit 181 × 360 column-major (Fortran Order) grid matrix to prevent spatial shearing artifacts across oceans.
3. **Spatial Blending**: Filters coordinate indices via `scipy.ndimage.gaussian_filter` to smooth jagged pixel drop-off cells into natural atmospheric color shapes.
4. **Layout Assembly**: Integrates modern Mapbox renderers alongside standard Cartesian graph objects into a unified dashboard layout frame.

---

## 📂 Project Structure

```text
├── clients/
│   └── NOAA_data.py           # Pulls the required data from NOAA
├── map/
│   └── aurora_location.html   # Main dashboard export target
│   └── map.py                 # Dashboard creation
├── main.py                    # Data fetching, pipeline smoothing, and layout composition
├── requirements.txt           # Active dependency constraints
└── README.md                  # System documentation
```

---

## 💻 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/wildAstroboy/auroraForecaster.git
cd auroraForecaster
```

### 2. Install Required Dependencies
Ensure you have Python 3.10+ installed. Install the verified framework constraints:
```bash
pip install -r requirements.txt
```

*Note: Your `requirements.txt` should contain:*
```text
pandas
numpy
requests
plotly
geocoder
scipy
```

### 3. Execute the Application Pipeline
Run the script locally to pull live NOAA payloads and generate your visualization:
```bash
python main.py
```

Open the newly generated `map/aurora_location.html` file directly in any modern desktop browser to navigate the interface.

---

## 📊 Visual Reference Configurations

### Aurora Probability Tiers (Map Layer Colorbar)
*   🟢 **Green (10%–39%)**: Low/Unsettled peripheral auroral activity glow.
*   🟪 **Purple (40%–74%)**: Active visibility potential. High chance of photographic capture.
*   🔴 **Red (75%–100%)**: Intense/Storm-level overhead visible aurora display.

<img width="1730" height="966" alt="Screenshot 2026-08-26 at 4 36 37 PM" src="https://github.com/user-attachments/assets/e5b8d027-155c-407f-8833-4c3ab59bbc13" />

### Kp Index Threat Scale (Timeline Bars)

| Kp Metric | Associated Color | Status Condition |
| :--- | :--- | :--- |
| **$\ge$ 9** | 🟤 Dark Red | G5 Extreme Geomagnetic Storm |
| **8** | 🔴 Red | G4 Severe Geomagnetic Storm |
| **7** | 🟠 Orange | G3 Strong Geomagnetic Storm |
| **6** | 🟡 Light Orange | G2 Moderate Geomagnetic Storm |
| **5** | 🟡 Yellow | G1 Minor Storm Threshold |
| **< 5** | 🟢 Bright Green | Quiet / Unsettled Background |

<img width="1730" height="973" alt="Screenshot 2026-08-26 at 4 36 45 PM" src="https://github.com/user-attachments/assets/ed79c5af-a812-4e3b-b99e-58a6c470789c" />

---

## 📝 License

Distributed under the MIT License.

---

## 📡 Data Sourcing Acknowledgments
* Data feeds provided by the **National Oceanic and Atmospheric Administration (NOAA) Space Weather Prediction Center**.
* Map tiles styled via open-source **Carto Darkmatter** canvas configurations.
