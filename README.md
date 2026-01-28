# ✈️ FlightFocus Pro - Fedora Edition

**A productivity-focused flight simulation timer optimized for Fedora Workstation.**

FlightFocus Pro turns your focus sessions into real-time flight simulations. Select a duration, pick a real-world flight path, and watch your plane travel from departure to destination as you work. The flight lands exactly when your timer hits zero.

## 🐧 Fedora Optimized Features
This edition has been specifically tuned for **Fedora Workstation (GNOME)**:
* **Native Theming:** Uses `QT_QPA_PLATFORMTHEME="gnome"` for seamless visual integration.
* **WebEngine Fixes:** Pre-configured environment variables (`QTWEBENGINE_DISABLE_SANDBOX`) to prevent rendering crashes common on Linux Wayland/X11 setups.
* **Adaptive Layout:** Responsive window sizing that handles tiling and maximization correctly.

## 🚀 Features
* **Real-World Telemetry:** Simulates altitude climbs, cruises, and descents.
* **Geodesic Navigation:** Plane icon orients correctly along the Great Circle path using real-time bearing calculations.
* **Focus Presets:** Quick selection for Pomodoro (25m), Deep Work (60m), and Marathon sessions.
* **Visual Progress:** Interactive map using Leaflet.js with live speed multipliers.

## 🛠️ Installation

### Prerequisites
You need Python 3 and the PyQt6 libraries.

```bash
# Install system dependencies (Fedora/RHEL)
sudo dnf install python3-pip

# Install Python requirements
pip install PyQt6 PyQt6-WebEngine
