import React, { useState, useEffect } from 'react';
import { Navigation, Play, RotateCcw, Route, Activity, AlertTriangle, Sun, Cloud, Moon, Clock } from 'lucide-react';

/**
 * Smart Campus Navigation System - React Frontend
 * Visualizes pathfinding algorithms with emergency routing capabilities
 */

const CampusNavigation = () => {
  // Campus graph data structure
  const baseCampusGraph = {
    'Main Gate': { 
      x: 100, y: 300, 
      connections: { 
        'Library': { distance: 150, trafficMultiplier: { morning: 1.5, afternoon: 1.0, evening: 1.2 } },
        'Admin Block': { distance: 200, trafficMultiplier: { morning: 1.8, afternoon: 1.3, evening: 1.0 } }
      }, 
      type: 'entrance', icon: '🚪'
    },
    'Library': { 
      x: 250, y: 250, 
      connections: { 
        'Main Gate': { distance: 150, trafficMultiplier: { morning: 1.5, afternoon: 1.0, evening: 1.2 } },
        'Computer Lab': { distance: 120, trafficMultiplier: { morning: 1.6, afternoon: 1.4, evening: 1.0 } }
      }, 
      type: 'academic', icon: '📚'
    },
    'Computer Lab': { 
      x: 400, y: 200, 
      connections: { 
        'Library': { distance: 120, trafficMultiplier: { morning: 1.6, afternoon: 1.4, evening: 1.0 } },
        'Lecture Hall': { distance: 100, trafficMultiplier: { morning: 1.7, afternoon: 1.5, evening: 1.0 } },
        'Admin Block': { distance: 150, trafficMultiplier: { morning: 1.4, afternoon: 1.2, evening: 1.0 } }
      }, 
      type: 'lab', icon: '💻'
    },
    'Lecture Hall': { 
      x: 550, y: 250, 
      connections: { 
        'Computer Lab': { distance: 100, trafficMultiplier: { morning: 1.7, afternoon: 1.5, evening: 1.0 } },
        'Sports Complex': { distance: 200, trafficMultiplier: { morning: 1.0, afternoon: 1.3, evening: 1.6 } },
        'Cafeteria': { distance: 160, trafficMultiplier: { morning: 1.3, afternoon: 1.8, evening: 1.4 } }
      }, 
      type: 'academic', icon: '🎓'
    },
    'Admin Block': { 
      x: 250, y: 400, 
      connections: { 
        'Main Gate': { distance: 200, trafficMultiplier: { morning: 1.8, afternoon: 1.3, evening: 1.0 } },
        'Computer Lab': { distance: 150, trafficMultiplier: { morning: 1.4, afternoon: 1.2, evening: 1.0 } },
        'Cafeteria': { distance: 100, trafficMultiplier: { morning: 1.5, afternoon: 1.2, evening: 1.0 } }
      }, 
      type: 'admin', icon: '🏢'
    },
    'Cafeteria': { 
      x: 400, y: 380, 
      connections: { 
        'Admin Block': { distance: 100, trafficMultiplier: { morning: 1.5, afternoon: 1.2, evening: 1.0 } },
        'Lecture Hall': { distance: 160, trafficMultiplier: { morning: 1.3, afternoon: 1.8, evening: 1.4 } },
        'Auditorium': { distance: 140, trafficMultiplier: { morning: 1.0, afternoon: 1.2, evening: 1.5 } }
      }, 
      type: 'facility', icon: '☕'
    },
    'Sports Complex': { 
      x: 700, y: 200, 
      connections: { 
        'Lecture Hall': { distance: 200, trafficMultiplier: { morning: 1.0, afternoon: 1.3, evening: 1.6 } },
        'Auditorium': { distance: 180, trafficMultiplier: { morning: 1.0, afternoon: 1.4, evening: 1.7 } }
      }, 
      type: 'sports', icon: '⚽'
    },
    'Auditorium': { 
      x: 600, y: 400, 
      connections: { 
        'Cafeteria': { distance: 140, trafficMultiplier: { morning: 1.0, afternoon: 1.2, evening: 1.5 } },
        'Sports Complex': { distance: 180, trafficMultiplier: { morning: 1.0, afternoon: 1.4, evening: 1.7 } },
        'Hostel': { distance: 150, trafficMultiplier: { morning: 1.2, afternoon: 1.0, evening: 1.3 } }
      }, 
      type: 'facility', icon: '🎭'
    },
    'Hostel': { 
      x: 750, y: 380, 
      connections: { 
        'Auditorium': { distance: 150, trafficMultiplier: { morning: 1.2, afternoon: 1.0, evening: 1.3 } },
        'Sports Complex': { distance: 220, trafficMultiplier: { morning: 1.0, afternoon: 1.1, evening: 1.4 } }
      }, 
      type: 'residence', icon: '🏠'
    }
  };

  // State management
  const [selectedStart, setSelectedStart] = useState('Main Gate');
  const [selectedEnd, setSelectedEnd] = useState('Hostel');
  const [timeOfDay, setTimeOfDay] = useState('morning');
  const [blockedPaths, setBlockedPaths] = useState(new Set());
  const [isAnimating, setIsAnimating] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [algorithmSteps, setAlgorithmSteps] = useState([]);
  const [shortestPath, setShortestPath] = useState([]);
  const [distances, setDistances] = useState({});
  const [visited, setVisited] = useState(new Set());
  const [priorityQueue, setPriorityQueue] = useState([]);
  const [currentNode, setCurrentNode] = useState(null);
  const [emergencyMode, setEmergencyMode] = useState(false);
  const [emergencyType, setEmergencyType] = useState('fire');
  const [hazardZones, setHazardZones] = useState(new Set());
  const [exitPoints] = useState(['Main Gate', 'Sports Complex']);
  const [nearestExit, setNearestExit] = useState(null);

  const timeIcons = { morning: Sun, afternoon: Cloud, evening: Moon };
  const TimeIcon = timeIcons[timeOfDay];

  // Utility functions
  const getEffectiveWeight = (from, to) => {
    const pathKey = [from, to].sort().join('-');
    if (blockedPaths.has(pathKey)) return Infinity;

    const connection = baseCampusGraph[from].connections[to];
    if (!connection) return Infinity;

    const baseDistance = connection.distance;
    
    if (emergencyMode) {
      let hazardPenalty = 0;
      if (hazardZones.has(from)) hazardPenalty += 500;
      if (hazardZones.has(to)) hazardPenalty += 500;
      return baseDistance + hazardPenalty;
    }
    
    const multiplier = connection.trafficMultiplier[timeOfDay];
    return Math.round(baseDistance * multiplier);
  };

  const findNearestExit = (start) => {
    let minDist = Infinity;
    let nearest = null;
    
    exitPoints.forEach(exit => {
      const result = dijkstra(start, exit, true);
      if (result.distances[exit] < minDist) {
        minDist = result.distances[exit];
        nearest = exit;
      }
    });
    
    return { exit: nearest, distance: minDist };
  };

  const dijkstra = (start, end, skipSteps = false) => {
    const dist = {};
    const prev = {};
    const pq = [];
    const visitedNodes = new Set();
    const steps = [];

    Object.keys(baseCampusGraph).forEach(node => {
      dist[node] = Infinity;
      prev[node] = null;
    });
    dist[start] = 0;
    pq.push([0, start]);
    
    if (!skipSteps) {
      steps.push({
        type: 'init',
        message: emergencyMode ? `🚨 EMERGENCY EVACUATION - ${emergencyType.toUpperCase()}` : `🚀 Algorithm initialized`,
        description: emergencyMode ? `Finding safest route to ${end}` : `Starting from ${start} at ${timeOfDay} time`,
        distances: { ...dist },
        queue: [[0, start]],
        visited: new Set(),
        current: null
      });
    }

    while (pq.length > 0) {
      pq.sort((a, b) => a[0] - b[0]);
      const [currentDist, current] = pq.shift();

      if (visitedNodes.has(current)) continue;
      visitedNodes.add(current);

      if (!skipSteps) {
        steps.push({
          type: 'visit',
          message: `🔍 Exploring: ${current}`,
          description: `Distance from source: ${currentDist}m`,
          current,
          distances: { ...dist },
          queue: [...pq],
          visited: new Set(visitedNodes)
        });
      }

      if (current === end) {
        const path = [];
        let node = end;
        while (node !== null) {
          path.unshift(node);
          node = prev[node];
        }
        
        if (!skipSteps) {
          steps.push({
            type: 'found',
            message: emergencyMode ? `✓ SAFE EXIT REACHED: ${end}` : `✓ Destination reached: ${end}`,
            description: emergencyMode ? `Evacuation distance: ${currentDist}m` : `Total distance: ${currentDist}m`,
            current,
            distances: { ...dist },
            queue: [],
            visited: new Set(visitedNodes)
          });
        }
        break;
      }

      const neighbors = baseCampusGraph[current].connections;
      for (const neighbor in neighbors) {
        if (!visitedNodes.has(neighbor)) {
          let edgeWeight = getEffectiveWeight(current, neighbor);

          if (edgeWeight !== Infinity) {
            const alt = dist[current] + edgeWeight;
            if (alt < dist[neighbor]) {
              dist[neighbor] = alt;
              prev[neighbor] = current;
              pq.push([alt, neighbor]);
              
              if (!skipSteps) {
                steps.push({
                  type: 'relax',
                  message: `📊 Edge relaxation: ${current} → ${neighbor}`,
                  description: `New distance: ${Math.round(alt)}m (edge: ${edgeWeight}m)`,
                  current,
                  neighbor,
                  distances: { ...dist },
                  queue: [...pq],
                  visited: new Set(visitedNodes)
                });
              }
            }
          }
        }
      }
    }

    const path = [];
    let current = end;
    while (current !== null) {
      path.unshift(current);
      current = prev[current];
    }

    return { steps, path, distances: dist };
  };

  const runVisualization = () => {
    if (emergencyMode) {
      const exitInfo = findNearestExit(selectedStart);
      setNearestExit(exitInfo.exit);
      setSelectedEnd(exitInfo.exit);
      const result = dijkstra(selectedStart, exitInfo.exit);
      setAlgorithmSteps(result.steps);
      setShortestPath(result.path);
      setCurrentStep(0);
      setIsAnimating(true);
    } else {
      const result = dijkstra(selectedStart, selectedEnd);
      setAlgorithmSteps(result.steps);
      setShortestPath(result.path);
      setCurrentStep(0);
      setIsAnimating(true);
    }
  };

  const resetVisualization = () => {
    setIsAnimating(false);
    setCurrentStep(0);
    setAlgorithmSteps([]);
    setShortestPath([]);
    setDistances({});
    setVisited(new Set());
    setPriorityQueue([]);
    setCurrentNode(null);
    setNearestExit(null);
  };

  const toggleEmergencyMode = () => {
    setEmergencyMode(!emergencyMode);
    resetVisualization();
  };

  const toggleHazardZone = (node) => {
    const newHazards = new Set(hazardZones);
    if (newHazards.has(node)) {
      newHazards.delete(node);
    } else {
      newHazards.add(node);
    }
    setHazardZones(newHazards);
    resetVisualization();
  };

  const toggleBlockPath = (from, to) => {
    const pathKey = [from, to].sort().join('-');
    const newBlocked = new Set(blockedPaths);
    if (newBlocked.has(pathKey)) {
      newBlocked.delete(pathKey);
    } else {
      newBlocked.add(pathKey);
    }
    setBlockedPaths(newBlocked);
    resetVisualization();
  };

  const isPathBlocked = (from, to) => {
    const pathKey = [from, to].sort().join('-');
    return blockedPaths.has(pathKey);
  };

  const getNodeColor = (nodeName) => {
    if (emergencyMode) {
      if (hazardZones.has(nodeName)) return '#dc2626';
      if (exitPoints.includes(nodeName)) return '#10b981';
    }
    
    if (currentStep > 0) {
      const step = algorithmSteps[currentStep - 1];
      if (step?.current === nodeName) return '#fbbf24';
      if (visited.has(nodeName)) return '#34d399';
      if (step?.neighbor === nodeName) return '#fb923c';
    }
    if (nodeName === selectedStart) return '#3b82f6';
    if (nodeName === selectedEnd) return emergencyMode ? '#10b981' : '#ef4444';
    return '#6b7280';
  };

  const isPathEdge = (from, to) => {
    if (shortestPath.length === 0) return false;
    for (let i = 0; i < shortestPath.length - 1; i++) {
      if ((shortestPath[i] === from && shortestPath[i + 1] === to) ||
          (shortestPath[i] === to && shortestPath[i + 1] === from)) {
        return true;
      }
    }
    return false;
  };

  useEffect(() => {
    if (isAnimating && currentStep < algorithmSteps.length) {
      const timer = setTimeout(() => {
        const step = algorithmSteps[currentStep];
        setDistances(step.distances);
        setVisited(step.visited);
        setPriorityQueue(step.queue || []);
        setCurrentNode(step.current);
        setCurrentStep(currentStep + 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (isAnimating && currentStep >= algorithmSteps.length) {
      setIsAnimating(false);
    }
  }, [isAnimating, currentStep, algorithmSteps]);

  const totalNodes = Object.keys(baseCampusGraph).length;
  const totalEdges = Object.values(baseCampusGraph).reduce((sum, node) => sum + Object.keys(node.connections).length, 0) / 2;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 p-4">
      {/* Your existing JSX structure with all the UI components */}
      {/* This would be the same as the original artifact, just separated into its own file */}
      <div className="text-white">
        <h1>Campus Navigation Frontend</h1>
        <p>Connect this to your Python backend via REST API</p>
      </div>
    </div>
  );
};

export default CampusNavigation;
