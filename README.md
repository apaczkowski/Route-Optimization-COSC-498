# Mercury – Route Optimization Web App

A Flask-based travel route optimizer that helps users generate the most efficient travel path between multiple addresses. The app combines the Google Maps API and Python's PuLP linear programming library to determine the optimal driving route, complete with real-time distance, duration, cost estimates, and an interactive map.

🚀 **Features**
```
- 🧭 Optimizes travel routes based on user-input addresses
- 📍 Converts addresses to coordinates using Google Maps API
- 🚗 Calculates driving distance, time, and estimated fuel cost
- 🧠 Applies linear programming (PuLP) to find the shortest/fastest path
- 🗺️ Displays ordered stops, directions, and an embedded map
- 🖨️ Allows export of results as a PDF report (planned)
```
👥 **Target Audience**
```
Built for:
- Delivery drivers & couriers
- Field service technicians
- Travel/vacation planners
- Anyone needing an efficient multi-stop route
```
🛠️ **Tech Stack**
**Backend**: Python, Flask, PuLP (linear optimization)
**Frontend**: HTML, CSS, JavaScript
**APIs**: Google Maps (Geocoding, Directions, Maps Embed)
**Tools**: Git, PDF export libraries (TBD)

📁 **Project Structure**
```
Mercury/
├── Index.html # All-in-one HTML, CSS, and JavaScript UI
├── RPTotalTime.py # Flask backend and optimization logic
├── README.md # This file
└── Week 4 - Updated Design Plan.docx # Early design documentation
```
```
⚙️ **Setup Instructions**
1. **Clone the repository**
   ```bash
   git clone https://github.com/apaczkowski/COSC-498.git
   cd COSC-498
2. **Set up your environment**
   python -m venv venv
   source venv/bin/activate     # On Windows: venv\Scripts\activate
   pip install flask pulp requests
3. **Add your Google Maps API key**
   In RPTotalTime.py, replace YOUR_API_KEY_HERE with your actual key.
   Example:
    ```
    API_KEY = "your-real-api-key"
    ```
4. **Run the app**
   python mercury.py
5. **Open in your browser**
   http://127.0.0.1:5000/
```
📌 Planned Enhancements
```
** PDF/CSV export of travel report
** Turn-by-turn directions (formatted)
** Multi-vehicle route optimization
** Alternative transport modes (bike, walking, transit)
** User login and saved routes
```
🧠 What I Learned
```
** How to combine APIs and algorithms in a real-world Flask app
** Performing linear optimization using PuLP
** Managing dynamic forms and input validation with JavaScript
** Embedding and styling Google Maps with live data
** Structuring a full-stack Python project for clarity and maintainability
```
```
🧑‍💻 Author
Adam Paczkowski
📍 St. Louis, MO
https://github.com/apaczkowski
https://www.linkedin.com/in/adam-paczkowski-b841602b7/
```
