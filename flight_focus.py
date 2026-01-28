#!/usr/bin/env python3
"""
FlightFocus Pro - Fedora Edition (v1.2)
- Fixed: Plane orientation now follows Great Circle bearing correctly.
- Fixed: Window maximize behavior and layout scaling.
- Optimized: Fedora GNOME theme integration.
"""

import os
import sys
import math
from datetime import datetime, timedelta

# --- FEDORA-SPECIFIC OPTIMIZATIONS ---
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox --disable-software-rasterizer"
os.environ["QT_QPA_PLATFORMTHEME"] = "gnome" 

# --- FEDORA GNOME THEME COLORS ---
FEDORA_COLORS = {
    "background": "#2d2d2d",      # Dark Grey (Window)
    "surface": "#3d3d3d",         # Lighter Grey (Cards/Widgets)
    "primary": "#367bf0",         # Fedora Blue
    "secondary": "#2ec27e",       # Fedora Green
    "accent": "#f9f06b",          # Fedora Yellow
    "text": "#f6f5f4",            # White/Grey Text
    "text_secondary": "#deddda",  # Muted Text
    "border": "#5e5c64",          # Border Grey
    "success": "#57e389",
    "warning": "#f8e45c",
    "error": "#ff7b63"
}

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QPushButton, 
                             QStackedWidget, QFrame, QGridLayout, QGroupBox,
                             QScrollArea, QButtonGroup, QSizePolicy)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon

# --- REAL WORLD ROUTES ---
REAL_WORLD_FLIGHTS = {
    # Short Flights (25-90 mins)
    "🇬🇧 LONDON → 🇫🇷 PARIS": { "coords": [51.4700, -0.4543, 49.0097, 2.5479], "real_duration": 85, "distance_km": 344, "aircraft": "Airbus A320", "callsign": "BAF123" },
    "🇺🇸 NY (JFK) → 🇺🇸 WASHINGTON": { "coords": [40.6413, -73.7781, 38.9531, -77.4565], "real_duration": 75, "distance_km": 333, "aircraft": "Boeing 737", "callsign": "DAL456" },
    "🇦🇪 DUBAI → 🇶🇦 DOHA": { "coords": [25.2532, 55.3657, 25.2609, 51.5651], "real_duration": 70, "distance_km": 379, "aircraft": "Airbus A320", "callsign": "QTR789" },
    "🇯🇵 TOKYO → 🇰🇷 SEOUL": { "coords": [35.5494, 139.7798, 37.4602, 126.4407], "real_duration": 135, "distance_km": 1157, "aircraft": "Boeing 787", "callsign": "JAL234" },
    "🇩🇪 BERLIN → 🇨🇿 PRAGUE": { "coords": [52.3667, 13.5033, 50.1008, 14.2600], "real_duration": 65, "distance_km": 280, "aircraft": "Airbus A319", "callsign": "BER567" },
    
    # Medium Flights (90-180 mins)
    "🇪🇸 MADRID → 🇮🇹 ROME": { "coords": [40.4839, -3.5679, 41.8003, 12.2389], "real_duration": 145, "distance_km": 1365, "aircraft": "Airbus A321", "callsign": "IBE345" },
    "🇺🇸 SEATTLE → 🇺🇸 SAN FRANCISCO": { "coords": [47.4502, -122.3088, 37.6213, -122.3790], "real_duration": 125, "distance_km": 1090, "aircraft": "Boeing 737", "callsign": "UAL678" },
    "🇮🇳 MUMBAI → 🇦🇪 DUBAI": { "coords": [19.0896, 72.8656, 25.2532, 55.3657], "real_duration": 180, "distance_km": 1934, "aircraft": "Boeing 777", "callsign": "UAE901" },
    "🇬🇧 LONDON → 🇹🇷 ISTANBUL": { "coords": [51.4700, -0.4543, 41.2768, 28.7293], "real_duration": 235, "distance_km": 2502, "aircraft": "Airbus A330", "callsign": "THY123" },
    
    # Long Flights (180-360 mins)
    "🇺🇸 NEW YORK → 🇬🇧 LONDON": { "coords": [40.6413, -73.7781, 51.4700, -0.4543], "real_duration": 415, "distance_km": 5566, "aircraft": "Boeing 777", "callsign": "BAW001" },
    "🇯🇵 TOKYO → 🇸🇬 SINGAPORE": { "coords": [35.5494, 139.7798, 1.3644, 103.9915], "real_duration": 440, "distance_km": 5328, "aircraft": "Boeing 787", "callsign": "SIA012" },
    "🇩🇪 FRANKFURT → 🇺🇸 NEW YORK": { "coords": [50.0379, 8.5622, 40.6413, -73.7781], "real_duration": 510, "distance_km": 6205, "aircraft": "Airbus A380", "callsign": "DLH403" },
    
    # Ultra Long Haul (360+ mins)
    "🇺🇸 LOS ANGELES → 🇦🇺 SYDNEY": { "coords": [33.9416, -118.4085, -33.9399, 151.1753], "real_duration": 900, "distance_km": 12051, "aircraft": "Boeing 787", "callsign": "QFA012" },
    "🇬🇧 LONDON → 🇦🇺 PERTH": { "coords": [51.4700, -0.4543, -31.9385, 115.9672], "real_duration": 1020, "distance_km": 14498, "aircraft": "Boeing 787", "callsign": "QFA009" },
    "🇶🇦 DOHA → 🇳🇿 AUCKLAND": { "coords": [25.2609, 51.5651, -37.0082, 174.7850], "real_duration": 960, "distance_km": 14535, "aircraft": "Boeing 777", "callsign": "QTR920" }
}

FOCUS_PRESETS = [
    ("Quick Focus", 25), ("Standard Session", 40), ("Deep Work", 60), ("Extended Focus", 90),
    ("Movie Length", 120), ("Study Block", 180), ("Work Shift", 240), ("Marathon", 360)
]

# --- MAP TEMPLATE ---
MAP_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body, html { height: 100%; margin: 0; background-color: #2d2d2d; font-family: 'Cantarell', sans-serif; }
        #map { height: 100%; width: 100%; background: #2d2d2d; }
        
        .plane-wrapper { 
            width: 56px; height: 56px; display: block; 
            transition: transform 0.1s linear; /* Faster update for smoother turns */
            filter: drop-shadow(0 0 12px rgba(54, 123, 240, 0.8)); 
        }
        
        .progress-label { position: absolute; background: rgba(45, 45, 45, 0.95); color: #f6f5f4; padding: 6px 12px; border-radius: 6px; font-size: 13px; font-weight: bold; white-space: nowrap; transform: translate(-50%, -60px); border: 2px solid #367bf0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); }
        .info-panel { position: absolute; top: 20px; right: 20px; background: rgba(45, 45, 45, 0.95); border: 2px solid #5e5c64; border-radius: 12px; padding: 20px; color: #f6f5f4; font-size: 14px; min-width: 240px; backdrop-filter: blur(10px); z-index: 1000; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); }
        .route-info { margin: 8px 0; color: #deddda; line-height: 1.5; }
        .flight-id { font-size: 18px; font-weight: bold; color: #57e389; margin-bottom: 12px; border-bottom: 2px solid #5e5c64; padding-bottom: 8px; }
        .fedora-header { position: absolute; top: 20px; left: 20px; background: rgba(54, 123, 240, 0.9); color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold; font-size: 16px; z-index: 1000; box-shadow: 0 4px 12px rgba(54, 123, 240, 0.4); }
    </style>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>
<body>
    <div id="map"></div>
    <div class="fedora-header">✈️ FlightFocus Pro - Fedora Edition</div>
    <div class="info-panel">
        <div class="flight-id">✈️ FLIGHT_ID_VAL</div>
        <div class="route-info">📏 Distance: DISTANCE_VAL km</div>
        <div class="route-info">🛩️ Aircraft: AIRCRAFT_VAL</div>
        <div class="route-info">🕐 Real Duration: DURATION_VAL</div>
        <div class="route-info">📍 Route: START_CITY → END_CITY</div>
        <div class="route-info">⚡ Speed: SPEED_VAL</div>
    </div>
    <script>
        var startLat = START_LAT_VAL; var startLng = START_LNG_VAL;
        var endLat = END_LAT_VAL; var endLng = END_LNG_VAL;
        var focusDuration = FOCUS_DURATION_VAL; 
        var realDuration = REAL_DURATION_VAL;
        var speedMultiplier = (realDuration / focusDuration).toFixed(1);
        var animationDuration = realDuration / speedMultiplier;

        var map = L.map('map', { zoomControl: true, attributionControl: false, fadeAnimation: true, zoomAnimation: true }).setView([startLat, startLng], 3);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { maxZoom: 19, subdomains: 'abcd' }).addTo(map);

        // --- GREAT CIRCLE CALCULATION ---
        function toRad(deg) { return deg * Math.PI / 180; }
        function toDeg(rad) { return rad * 180 / Math.PI; }

        // Calculate Bearing (Direction) between two points
        function calculateBearing(lat1, lon1, lat2, lon2) {
            var phi1 = toRad(lat1), lambda1 = toRad(lon1);
            var phi2 = toRad(lat2), lambda2 = toRad(lon2);
            var y = Math.sin(lambda2 - lambda1) * Math.cos(phi2);
            var x = Math.cos(phi1) * Math.sin(phi2) - Math.sin(phi1) * Math.cos(phi2) * Math.cos(lambda2 - lambda1);
            var theta = Math.atan2(y, x);
            return (toDeg(theta) + 360) % 360;
        }

        var routeCoordinates = [];
        var steps = 150; // More steps for smoother curve
        for(var i = 0; i <= steps; i++) {
            var f = i / steps;
            var lat = startLat + (endLat - startLat) * f;
            var lng = startLng + (endLng - startLng) * f;
            // Handle date line crossing simply for visualization
            if(Math.abs(endLng - startLng) > 180) {
                if(startLng < 0) startLng += 360; if(endLng < 0) endLng += 360;
                lng = startLng + (endLng - startLng) * f; if(lng > 180) lng -= 360;
            }
            routeCoordinates.push([lat, lng]);
        }

        var pathLine = L.polyline(routeCoordinates, { color: '#367bf0', weight: 4, opacity: 0.9, dashArray: '12, 12', lineCap: 'round', lineJoin: 'round' }).addTo(map);
        map.fitBounds(pathLine.getBounds(), {padding: [120, 120]});

        // SVG Plane pointing UP (North) by default
        var svgPlane = `<div class="plane-wrapper"><svg viewBox="0 0 24 24" fill="#367bf0" xmlns="http://www.w3.org/2000/svg"><path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/></svg></div>`;
        var planeIcon = L.divIcon({ html: svgPlane, className: 'plane-icon', iconSize: [56, 56], iconAnchor: [28, 28] });
        var marker = L.marker([startLat, startLng], {icon: planeIcon}).addTo(map);

        var progressLabel = L.divIcon({ html: '<div class="progress-label">DEPARTING FROM FEDORA WORKSTATION</div>', className: '', iconSize: [0, 0] });
        var progressMarker = L.marker([startLat, startLng], { icon: progressLabel }).addTo(map);

        var startTime = Date.now();
        var endTime = startTime + (animationDuration * 1000);

        function animate() {
            var now = Date.now();
            var remaining = endTime - now;
            var progress = 1 - (remaining / (animationDuration * 1000));
            
            if (progress >= 1) {
                marker.setLatLng([endLat, endLng]);
                progressMarker.setLatLng([endLat, endLng]);
                document.querySelector('.progress-label').textContent = 'ARRIVED ✓ FOCUS COMPLETE';
                
                // Final rotation adjustment
                var finalBearing = calculateBearing(routeCoordinates[steps-1][0], routeCoordinates[steps-1][1], endLat, endLng);
                var el = document.querySelector('.plane-wrapper');
                if(el) el.style.transform = `rotate(${finalBearing}deg)`;
                return;
            }
            
            var currentLat = startLat + (endLat - startLat) * progress;
            var currentLng = startLng + (endLng - startLng) * progress;
            
            // Calculate NEXT position slightly ahead to get tangent bearing
            var nextProgress = Math.min(progress + 0.01, 1);
            var nextLat = startLat + (endLat - startLat) * nextProgress;
            var nextLng = startLng + (endLng - startLng) * nextProgress;
            
            // Calculate bearing based on geographic coordinates
            var bearing = calculateBearing(currentLat, currentLng, nextLat, nextLng);
            
            marker.setLatLng([currentLat, currentLng]);
            progressMarker.setLatLng([currentLat, currentLng]);
            
            // Update Rotation
            var el = document.querySelector('.plane-wrapper');
            if(el) el.style.transform = `rotate(${bearing}deg)`;
            
            var percent = Math.round(progress * 100);
            var hours = Math.floor(focusDuration / 3600);
            var minutes = Math.floor((focusDuration % 3600) / 60);
            document.querySelector('.progress-label').textContent = 'FEDORA FOCUS: ' + percent + '% | Time: ' + hours + 'h ' + minutes + 'm';
            
            requestAnimationFrame(animate);
        }
        setTimeout(animate, 1000);
    </script>
</body>
</html>
"""

class FlightCard(QFrame):
    """Custom widget for displaying flight information"""
    selected = pyqtSignal(str)
    
    def __init__(self, flight_name, flight_data, focus_time):
        super().__init__()
        self.flight_name = flight_name
        self.flight_data = flight_data
        self.focus_time = focus_time
        
        # Flexible height to prevent squashing
        self.setMinimumHeight(130)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        self.setStyleSheet(f"""
            FlightCard {{
                background-color: {FEDORA_COLORS['surface']};
                border: 2px solid {FEDORA_COLORS['border']};
                border-radius: 12px;
                padding: 0px;
            }}
            FlightCard:hover {{
                border-color: {FEDORA_COLORS['primary']};
                background-color: #454545;
            }}
            FlightCard[selected="true"] {{
                border-color: {FEDORA_COLORS['success']};
                background-color: #3a4a3a;
                border-width: 3px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header row
        header_layout = QHBoxLayout()
        self.flight_label = QLabel(flight_name)
        self.flight_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {FEDORA_COLORS['text']};")
        self.flight_label.setWordWrap(True)
        
        time_label = QLabel(f"🕐 {self.format_duration(flight_data['real_duration'])}")
        time_label.setStyleSheet(f"font-size: 14px; color: {FEDORA_COLORS['accent']}; font-weight: bold;")
        
        header_layout.addWidget(self.flight_label, stretch=1)
        header_layout.addWidget(time_label)
        
        # Details row
        details_layout = QGridLayout()
        details_layout.setHorizontalSpacing(15)
        details_layout.setVerticalSpacing(4)
        
        details_layout.addWidget(QLabel(f"📏 {flight_data['distance_km']:,} km"), 0, 0)
        details_layout.addWidget(QLabel(f"🛩️ {flight_data['aircraft']}"), 0, 1)
        details_layout.addWidget(QLabel(f"📡 {flight_data['callsign']}"), 1, 0)
        details_layout.addWidget(QLabel(f"⚡ {self.calculate_speed_multiplier():.1f}x speed"), 1, 1)
        
        # Apply style to all labels in grid
        for i in range(details_layout.count()):
            widget = details_layout.itemAt(i).widget()
            if widget:
                widget.setStyleSheet(f"color: {FEDORA_COLORS['text_secondary']}; font-size: 13px;")

        # Select button
        self.select_btn = QPushButton("SELECT FLIGHT")
        self.select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.select_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {FEDORA_COLORS['primary']}; color: white; border: none;
                border-radius: 6px; padding: 8px 12px; font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #4a8bf8; }}
        """)
        self.select_btn.clicked.connect(self.on_select)
        
        layout.addLayout(header_layout)
        layout.addLayout(details_layout)
        layout.addWidget(self.select_btn)
        self.setLayout(layout)
        
    def format_duration(self, minutes):
        return f"{minutes // 60}h {minutes % 60:02d}m"
    
    def calculate_speed_multiplier(self):
        return self.flight_data['real_duration'] / self.focus_time
    
    def on_select(self):
        self.selected.emit(self.flight_name)
    
    def set_selected(self, selected):
        self.setProperty("selected", selected)
        self.style().polish(self)

class FlightFocusPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlightFocus Pro - Fedora Edition")
        
        # KEY FIX: Standard resize behavior. Removed restrictions that break maximization.
        self.resize(1100, 800)
        self.setMinimumSize(800, 600)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.selected_focus_time = 60
        self.selected_flight = None
        self.flight_cards = []
        self.time_button_group = QButtonGroup(self)
        self.time_button_group.setExclusive(True)
        
        self.setup_fedora_theme()
        self.init_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_telemetry)
        
    def setup_fedora_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {FEDORA_COLORS['background']}; font-family: 'Cantarell', 'Ubuntu', sans-serif; }}
            QLabel {{ color: {FEDORA_COLORS['text']}; font-family: 'Cantarell'; }}
            QGroupBox {{
                color: {FEDORA_COLORS['primary']}; font-weight: bold; font-size: 14px;
                border: 2px solid {FEDORA_COLORS['border']}; border-radius: 12px; margin-top: 10px; padding-top: 20px;
            }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 8px; background-color: {FEDORA_COLORS['background']}; }}
            QScrollArea {{ border: none; background: transparent; }}
            QScrollBar:vertical {{ border: none; background: {FEDORA_COLORS['surface']}; width: 10px; border-radius: 5px; margin: 0; }}
            QScrollBar::handle:vertical {{ background: {FEDORA_COLORS['border']}; border-radius: 5px; min-height: 20px; }}
            QScrollBar::handle:vertical:hover {{ background: {FEDORA_COLORS['primary']}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main Layout
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.pages = QStackedWidget()
        self.layout.addWidget(self.pages)
        
        self.setup_page = QWidget()
        self.flight_page = QWidget()
        
        self.init_setup_page()
        self.init_flight_page()
        
        self.pages.addWidget(self.setup_page)
        self.pages.addWidget(self.flight_page)

    def init_setup_page(self):
        main_layout = QVBoxLayout(self.setup_page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header_container = QFrame()
        header_container.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {FEDORA_COLORS['primary']}, stop:1 {FEDORA_COLORS['secondary']});")
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        title_box = QHBoxLayout()
        header = QLabel("✈️ FlightFocus Pro")
        header.setStyleSheet("font-size: 32px; font-weight: 900; color: white;")
        badge = QLabel("  Fedora Workstation  ")
        badge.setStyleSheet("font-size: 12px; background: rgba(0,0,0,0.2); color: white; border-radius: 10px; padding: 4px 8px;")
        
        title_box.addWidget(header)
        title_box.addWidget(badge)
        title_box.addStretch()
        header_layout.addLayout(title_box)
        main_layout.addWidget(header_container)

        # Scrollable Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)

        # Time Selection
        time_group = QGroupBox("⏱️ STEP 1: SELECT DURATION")
        time_layout = QGridLayout()
        time_layout.setSpacing(15)
        
        for i, (name, minutes) in enumerate(FOCUS_PRESETS):
            btn = QPushButton(f"{name}\n{minutes} min")
            btn.setMinimumHeight(70)
            btn.setProperty("minutes", minutes)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            border_col = FEDORA_COLORS['border']
            if minutes > 180: border_col = FEDORA_COLORS['error']
            elif minutes > 90: border_col = FEDORA_COLORS['warning']
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {FEDORA_COLORS['surface']}; border: 2px solid {border_col};
                    border-radius: 12px; color: {FEDORA_COLORS['text']}; font-weight: bold;
                }}
                QPushButton:checked {{ background-color: #2a3a2a; border-color: {FEDORA_COLORS['success']}; }}
                QPushButton:hover {{ background-color: #454545; border-color: {FEDORA_COLORS['primary']}; }}
            """)
            
            self.time_button_group.addButton(btn)
            btn.clicked.connect(lambda checked, m=minutes: self.on_focus_time_selected(m))
            time_layout.addWidget(btn, i // 4, i % 4)
            if minutes == 60: btn.setChecked(True)

        time_group.setLayout(time_layout)
        content_layout.addWidget(time_group)

        # Custom Time Input
        custom_layout = QHBoxLayout()
        self.custom_time_input = QComboBox()
        self.custom_time_input.setEditable(True)
        self.custom_time_input.addItems([str(i) for i in range(10, 721, 5)])
        self.custom_time_input.setCurrentText("60")
        self.custom_time_input.setFixedSize(120, 45)
        self.custom_time_input.setStyleSheet(f"background: {FEDORA_COLORS['surface']}; color: white; border: 2px solid {FEDORA_COLORS['border']}; border-radius: 8px; padding-left: 10px;")
        
        custom_btn = QPushButton("Set Custom Time")
        custom_btn.setFixedSize(150, 45)
        custom_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        custom_btn.setStyleSheet(f"background: {FEDORA_COLORS['surface']}; color: white; border: 2px solid {FEDORA_COLORS['border']}; border-radius: 8px; font-weight: bold;")
        custom_btn.clicked.connect(self.on_custom_time_set)
        
        custom_layout.addWidget(QLabel("Or Custom Minutes:"))
        custom_layout.addWidget(self.custom_time_input)
        custom_layout.addWidget(custom_btn)
        custom_layout.addStretch()
        content_layout.addLayout(custom_layout)

        # Flight List
        self.flights_group = QGroupBox("✈️ STEP 2: SELECT FLIGHT")
        self.flights_layout = QVBoxLayout()
        self.flights_layout.setSpacing(12)
        self.flights_group.setLayout(self.flights_layout)
        
        content_layout.addWidget(self.flights_group)
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Footer
        footer_container = QFrame()
        footer_container.setStyleSheet(f"background-color: {FEDORA_COLORS['surface']}; border-top: 1px solid {FEDORA_COLORS['border']};")
        footer_layout = QVBoxLayout(footer_container)
        footer_layout.setContentsMargins(30, 20, 30, 20)
        
        self.start_btn = QPushButton("🚀 BEGIN FOCUS JOURNEY")
        self.start_btn.setEnabled(False)
        self.start_btn.setMinimumHeight(60)
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {FEDORA_COLORS['primary']}, stop:1 {FEDORA_COLORS['secondary']});
                color: white; border: none; border-radius: 12px; font-size: 18px; font-weight: 900; letter-spacing: 1px;
            }}
            QPushButton:hover {{ transform: translateY(-2px); }}
            QPushButton:disabled {{ background: {FEDORA_COLORS['border']}; color: {FEDORA_COLORS['text_secondary']}; }}
        """)
        self.start_btn.clicked.connect(self.start_flight)
        
        self.status_label = QLabel("🐧 Fedora Workstation Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("margin-top: 10px; color: #888;")
        
        footer_layout.addWidget(self.start_btn)
        footer_layout.addWidget(self.status_label)
        main_layout.addWidget(footer_container)
        
        self.update_available_flights(show_all=True)

    def on_focus_time_selected(self, minutes):
        self.selected_focus_time = minutes
        self.status_label.setText(f"⏱️ Selected focus time: {minutes} minutes")
        self.update_available_flights()

    def on_custom_time_set(self):
        self.time_button_group.setExclusive(False)
        for btn in self.time_button_group.buttons(): btn.setChecked(False)
        self.time_button_group.setExclusive(True)
        try:
            self.selected_focus_time = int(self.custom_time_input.currentText())
            self.update_available_flights()
        except:
            self.custom_time_input.setCurrentText("60")

    def update_available_flights(self, show_all=False):
        while self.flights_layout.count():
            item = self.flights_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.flight_cards.clear()
        
        matching = []
        if show_all:
            matching = list(REAL_WORLD_FLIGHTS.items())
        else:
            for name, data in REAL_WORLD_FLIGHTS.items():
                dur = data['real_duration']
                if (self.selected_focus_time * 0.3) <= dur <= (self.selected_focus_time * 2.0):
                    matching.append((name, data))
            matching.sort(key=lambda x: abs(x[1]['real_duration'] - self.selected_focus_time))
            if not matching:
                all_f = list(REAL_WORLD_FLIGHTS.items())
                all_f.sort(key=lambda x: abs(x[1]['real_duration'] - self.selected_focus_time))
                matching = all_f[:3]

        self.flights_group.setTitle(f"✈️ STEP 2: SELECT FLIGHT ({len(matching)} AVAILABLE)")
        
        for name, data in matching:
            card = FlightCard(name, data, self.selected_focus_time)
            card.selected.connect(self.on_flight_selected)
            self.flights_layout.addWidget(card)
            self.flight_cards.append(card)
            
        if self.flight_cards: self.on_flight_selected(matching[0][0])

    def on_flight_selected(self, flight_name):
        self.selected_flight = flight_name
        for card in self.flight_cards:
            card.set_selected(card.flight_name == flight_name)
        
        self.start_btn.setEnabled(True)
        data = REAL_WORLD_FLIGHTS[flight_name]
        speed = data['real_duration'] / self.selected_focus_time
        self.start_btn.setText(f"🚀 BEGIN JOURNEY ({self.selected_focus_time}m Focus ➔ {data['real_duration']}m Flight)")
        self.status_label.setText(f"✅ Selected: {flight_name} • Sim Speed: {speed:.1f}x")

    def init_flight_page(self):
        # KEY FIX: Layout stretch factors ensure map takes all available space
        layout = QVBoxLayout(self.flight_page)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("background: #2d2d2d;")
        # stretch=1 makes web_view consume all extra vertical space on maximize
        layout.addWidget(self.web_view, stretch=1) 
        
        dashboard = QFrame()
        dashboard.setStyleSheet(f"background: {FEDORA_COLORS['surface']}; border-top: 3px solid {FEDORA_COLORS['primary']};")
        dashboard.setFixedHeight(140)
        
        dash_layout = QGridLayout(dashboard)
        dash_layout.setContentsMargins(40, 20, 40, 20)
        
        self.val_time = QLabel("00:00:00")
        self.val_progress = QLabel("0%")
        self.val_alt = QLabel("0 ft")
        self.val_dist = QLabel("0 km")
        
        for lbl, color in [(self.val_time, 'success'), (self.val_progress, 'primary'), (self.val_alt, 'warning'), (self.val_dist, 'accent')]:
            lbl.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {FEDORA_COLORS[color]};")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        headers = ["TIME REMAINING", "PROGRESS", "ALTITUDE", "DISTANCE LEFT"]
        for i, text in enumerate(headers):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {FEDORA_COLORS['text_secondary']}; font-weight: bold; font-size: 12px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dash_layout.addWidget(lbl, 0, i)
            
        dash_layout.addWidget(self.val_time, 1, 0)
        dash_layout.addWidget(self.val_progress, 1, 1)
        dash_layout.addWidget(self.val_alt, 1, 2)
        dash_layout.addWidget(self.val_dist, 1, 3)
        
        layout.addWidget(dashboard)

    def start_flight(self):
        if not self.selected_flight: return
        data = REAL_WORLD_FLIGHTS[self.selected_flight]
        
        self.total_seconds = self.selected_focus_time * 60
        self.remaining_seconds = self.total_seconds
        real_seconds = data['real_duration'] * 60
        self.total_dist_km = data['distance_km']
        
        html = MAP_HTML_TEMPLATE
        flight_parts = self.selected_flight.split(" → ")
        
        replacements = {
            "START_LAT_VAL": str(data['coords'][0]), "START_LNG_VAL": str(data['coords'][1]),
            "END_LAT_VAL": str(data['coords'][2]), "END_LNG_VAL": str(data['coords'][3]),
            "FOCUS_DURATION_VAL": str(self.total_seconds), "REAL_DURATION_VAL": str(real_seconds),
            "DISTANCE_VAL": f"{data['distance_km']:,}", "AIRCRAFT_VAL": data['aircraft'],
            "FLIGHT_ID_VAL": data['callsign'], "DURATION_VAL": f"{data['real_duration']} min",
            "START_CITY": flight_parts[0][2:], "END_CITY": flight_parts[1][2:],
            "SPEED_VAL": f"{(real_seconds/self.total_seconds):.1f}x"
        }
        
        for k, v in replacements.items(): html = html.replace(k, v)
        
        self.web_view.setHtml(html)
        self.pages.setCurrentIndex(1)
        self.timer.start(1000)
        self.update_telemetry()

    def update_telemetry(self):
        if self.remaining_seconds <= 0:
            self.timer.stop()
            self.val_time.setText("00:00:00"); self.val_progress.setText("100%")
            self.val_alt.setText("ARRIVED ✓"); self.val_dist.setText("0 km")
            return

        self.remaining_seconds -= 1
        progress = (self.total_seconds - self.remaining_seconds) / self.total_seconds
        
        m, s = divmod(self.remaining_seconds, 60)
        h, m = divmod(m, 60)
        self.val_time.setText(f"{h:02}:{m:02}:{s:02}")
        self.val_progress.setText(f"{progress*100:.0f}%")
        
        alt = 38000
        if progress < 0.1: alt = 38000 * (progress * 10)
        elif progress > 0.9: alt = 38000 * ((1 - progress) * 10)
        self.val_alt.setText(f"{int(alt):,} ft")
        self.val_dist.setText(f"{int(self.total_dist_km * (1 - progress)):,} km")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FlightFocus Pro")
    app.setStyle('Fusion')
    font = QFont("Cantarell", 10)
    app.setFont(font)
    window = FlightFocusPro()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
