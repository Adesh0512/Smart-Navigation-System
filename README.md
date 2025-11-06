# 🗺️ Smart Campus Navigation System

Advanced pathfinding system with real-time traffic simulation, emergency routing, and interactive visualization.

## 📁 Project Structure

```
campus-navigation/
├── backend/
│   ├── campus_navigation.py    # Core pathfinding logic
│   ├── api.py                   # Flask REST API
│   ├── requirements.txt         # Python dependencies
│   └── test_api.py             # API tests
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── CampusNavigation.jsx
│   │   ├── App.jsx
│   │   └── index.jsx
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## 🚀 Features

### Core Features
- ✅ **Dijkstra's Algorithm** - Optimal pathfinding
- 🕒 **Traffic Simulation** - Dynamic weights based on time of day
- 🚨 **Emergency Routing** - Automatic nearest exit detection
- ⚠️ **Hazard Avoidance** - Mark dangerous zones
- 🚧 **Path Blocking** - Simulate construction/obstacles
- 📊 **Algorithm Visualization** - Step-by-step animation

### Emergency Features
- 🔥 Fire evacuation routing
- 🌊 Earthquake safe paths
- ⚠️ Security threat navigation
- 🏥 Medical emergency routes
- 500m hazard zone penalties
- Auto-detect nearest safe exit

## 📊 Data Structures Used

1. **Graph (Adjacency List)** - Campus map representation
2. **Priority Queue (Min-Heap)** - Dijkstra's algorithm
3. **Hash Map/Dictionary** - Distance tracking, path reconstruction
4. **Set** - Visited nodes, blocked paths, hazard zones
5. **Array** - Algorithm steps, final path

## 🔧 Backend Setup (Python)

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### requirements.txt
```
Flask==2.3.0
Flask-CORS==4.0.0
```

### Run Backend Server

```bash
python api.py
```

Server will start on `http://localhost:5000`

### Test the API

```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Get campus graph
curl http://localhost:5000/api/graph

# Find path (POST request)
curl -X POST http://localhost:5000/api/path \
  -H "Content-Type: application/json" \
  -d '{
    "start": "Main Gate",
    "end": "Hostel",
    "time_of_day": "morning",
    "emergency_mode": false
  }'
```

## 🎨 Frontend Setup (React)

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Or with yarn
yarn install
```

### package.json dependencies
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.263.1",
    "axios": "^1.4.0"
  },
  "devDependencies": {
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.14",
    "postcss": "^8.4.24"
  }
}
```

### Environment Variables

Create `.env` file in frontend directory:
```
REACT_APP_API_URL=http://localhost:5000/api
```

### Run Frontend

```bash
npm start
# Or
yarn start
```

App will open on `http://localhost:3000`

## 🔌 API Endpoints

### Graph Endpoints
```
GET  /api/health              - Health check
GET  /api/graph               - Get complete campus graph
GET  /api/nodes               - Get list of all nodes
```

### Pathfinding Endpoints
```
POST /api/path                - Find shortest path
POST /api/emergency/nearest-exit - Find nearest safe exit
```

**Request Body for /api/path:**
```json
{
  "start": "Main Gate",
  "end": "Hostel",
  "time_of_day": "morning",
  "emergency_mode": false,
  "track_steps": true
}
```

**Response:**
```json
{
  "path": ["Main Gate", "Library", "Computer Lab", "..."],
  "distance": 450,
  "steps": [...],
  "visited_nodes": [...]
}
```

### Path Blocking Endpoints
```
POST /api/paths/block         - Block a path
POST /api/paths/unblock       - Unblock a path
GET  /api/paths/blocked       - Get all blocked paths
```

### Hazard Zone Endpoints
```
POST /api/hazards/add         - Add hazard zone
POST /api/hazards/remove      - Remove hazard zone
POST /api/hazards/clear       - Clear all hazards
GET  /api/hazards             - Get all hazard zones
```

### Utility Endpoints
```
POST /api/reset               - Reset all constraints
```

## 💻 Usage Examples

### Python Backend Usage

```python
from campus_navigation import CampusGraph, PathFinder, TimeOfDay

# Initialize
campus = CampusGraph()
pathfinder = PathFinder(campus)

# Find normal path
result = pathfinder.dijkstra(
    start='Main Gate',
    end='Hostel',
    time_of_day=TimeOfDay.MORNING
)
print(f"Path: {' → '.join(result.path)}")
print(f"Distance: {result.distance}m")

# Block a path
pathfinder.block_path('Library', 'Computer Lab')

# Emergency evacuation
pathfinder.add_hazard_zone('Library')
nearest_exit, distance = pathfinder.find_nearest_exit('Lecture Hall')
print(f"Nearest exit: {nearest_exit} ({distance}m)")
```

### React Frontend Integration

```javascript
import axios from 'axios';

// Find path
const findPath = async () => {
  const response = await axios.post('http://localhost:5000/api/path', {
    start: 'Main Gate',
    end: 'Hostel',
    time_of_day: 'morning',
    emergency_mode: false
  });
  
  console.log('Path:', response.data.path);
  console.log('Distance:', response.data.distance);
};

// Emergency mode
const findNearestExit = async () => {
  const response = await axios.post('http://localhost:5000/api/emergency/nearest-exit', {
    start: 'Lecture Hall',
    time_of_day: 'afternoon'
  });
  
  console.log('Nearest exit:', response.data.nearest_exit);
};
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
python -m pytest test_api.py
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📱 Deployment

### Backend (Python)

**Option 1: Heroku**
```bash
heroku create campus-nav-api
git push heroku main
```

**Option 2: Docker**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "api.py"]
```

### Frontend (React)

**Option 1: Vercel**
```bash
npm install -g vercel
vercel deploy
```

**Option 2: Netlify**
```bash
npm run build
netlify deploy --prod --dir=build
```

## 🎯 Campus Locations

| Location | Type | Icon | Description |
|----------|------|------|-------------|
| Main Gate | Entrance | 🚪 | Primary entry/exit |
| Library | Academic | 📚 | Study area |
| Computer Lab | Lab | 💻 | IT facilities |
| Lecture Hall | Academic | 🎓 | Classrooms |
| Admin Block | Admin | 🏢 | Administrative offices |
| Cafeteria | Facility | ☕ | Food court |
| Sports Complex | Sports | ⚽ | Athletics area |
| Auditorium | Facility | 🎭 | Event venue |
| Hostel | Residence | 🏠 | Student housing |

## 🛠️ Customization

### Adding New Locations

**Backend (campus_navigation.py):**
```python
'New Building': Node(
    x=500, y=300,
    connections={
        'Library': Connection(100, TrafficMultiplier(1.2, 1.0, 1.1))
    },
    node_type=NodeType.ACADEMIC,
    icon='🏛️'
)
```

**Frontend (CampusNavigation.jsx):**
```javascript
'New Building': {
  x: 500, y: 300,
  connections: {
    'Library': { distance: 100, trafficMultiplier: {...} }
  },
  type: 'academic',
  icon: '🏛️'
}
```

### Modifying Traffic Patterns

Adjust traffic multipliers in connections:
```python
TrafficMultiplier(
    morning=1.5,    # 50% slower in morning
    afternoon=1.0,  # Normal speed
    evening=1.2     # 20% slower in evening
)
```

## 📈 Performance

- **Time Complexity**: O((V + E) log V) where V = nodes, E = edges
- **Space Complexity**: O(V)
- **Average Path Computation**: < 50ms
- **API Response Time**: < 100ms

## 🐛 Troubleshooting

### Backend Issues

**Port Already in Use:**
```bash
# Kill process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

**CORS Errors:**
- Ensure Flask-CORS is installed
- Check frontend API URL in .env file

### Frontend Issues

**API Connection Failed:**
- Verify backend is running
- Check REACT_APP_API_URL in .env
- Ensure no firewall blocking

**Dependencies Not Installing:**
```bash
rm -rf node_modules package-lock.json
npm install
```

## 📄 License

MIT License - feel free to use in your projects!

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📧 Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Email: support@example.com

## 🎓 Academic Use

Perfect for:
- Algorithm visualization projects
- Data structures courses
- Graph theory assignments
- Emergency management systems
- Campus navigation apps

---

**Built with ❤️ using Python, Flask, React, and Dijkstra's Algorithm**
