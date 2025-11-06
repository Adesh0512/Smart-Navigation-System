"""
Smart Campus Navigation System - Backend Logic
Implements Dijkstra's algorithm for pathfinding with emergency routing
"""

import heapq
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass
from enum import Enum


class NodeType(Enum):
    ENTRANCE = "entrance"
    ACADEMIC = "academic"
    LAB = "lab"
    ADMIN = "admin"
    FACILITY = "facility"
    SPORTS = "sports"
    RESIDENCE = "residence"


class EmergencyType(Enum):
    FIRE = "fire"
    EARTHQUAKE = "earthquake"
    INTRUDER = "intruder"
    MEDICAL = "medical"


class TimeOfDay(Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"


@dataclass
class TrafficMultiplier:
    morning: float
    afternoon: float
    evening: float


@dataclass
class Connection:
    distance: int
    traffic: TrafficMultiplier


@dataclass
class Node:
    x: int
    y: int
    connections: Dict[str, Connection]
    node_type: NodeType
    icon: str


@dataclass
class PathResult:
    path: List[str]
    distance: float
    steps: List[Dict]
    visited_nodes: Set[str]


class CampusGraph:
    """Represents the campus as a weighted graph"""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = self._initialize_campus_graph()
        self.exit_points = ['Main Gate', 'Sports Complex']
    
    def _initialize_campus_graph(self) -> Dict[str, Node]:
        """Initialize the campus graph structure"""
        return {
            'Main Gate': Node(
                x=100, y=300,
                connections={
                    'Library': Connection(150, TrafficMultiplier(1.5, 1.0, 1.2)),
                    'Admin Block': Connection(200, TrafficMultiplier(1.8, 1.3, 1.0))
                },
                node_type=NodeType.ENTRANCE,
                icon='🚪'
            ),
            'Library': Node(
                x=250, y=250,
                connections={
                    'Main Gate': Connection(150, TrafficMultiplier(1.5, 1.0, 1.2)),
                    'Computer Lab': Connection(120, TrafficMultiplier(1.6, 1.4, 1.0))
                },
                node_type=NodeType.ACADEMIC,
                icon='📚'
            ),
            'Computer Lab': Node(
                x=400, y=200,
                connections={
                    'Library': Connection(120, TrafficMultiplier(1.6, 1.4, 1.0)),
                    'Lecture Hall': Connection(100, TrafficMultiplier(1.7, 1.5, 1.0)),
                    'Admin Block': Connection(150, TrafficMultiplier(1.4, 1.2, 1.0))
                },
                node_type=NodeType.LAB,
                icon='💻'
            ),
            'Lecture Hall': Node(
                x=550, y=250,
                connections={
                    'Computer Lab': Connection(100, TrafficMultiplier(1.7, 1.5, 1.0)),
                    'Sports Complex': Connection(200, TrafficMultiplier(1.0, 1.3, 1.6)),
                    'Cafeteria': Connection(160, TrafficMultiplier(1.3, 1.8, 1.4))
                },
                node_type=NodeType.ACADEMIC,
                icon='🎓'
            ),
            'Admin Block': Node(
                x=250, y=400,
                connections={
                    'Main Gate': Connection(200, TrafficMultiplier(1.8, 1.3, 1.0)),
                    'Computer Lab': Connection(150, TrafficMultiplier(1.4, 1.2, 1.0)),
                    'Cafeteria': Connection(100, TrafficMultiplier(1.5, 1.2, 1.0))
                },
                node_type=NodeType.ADMIN,
                icon='🏢'
            ),
            'Cafeteria': Node(
                x=400, y=380,
                connections={
                    'Admin Block': Connection(100, TrafficMultiplier(1.5, 1.2, 1.0)),
                    'Lecture Hall': Connection(160, TrafficMultiplier(1.3, 1.8, 1.4)),
                    'Auditorium': Connection(140, TrafficMultiplier(1.0, 1.2, 1.5))
                },
                node_type=NodeType.FACILITY,
                icon='☕'
            ),
            'Sports Complex': Node(
                x=700, y=200,
                connections={
                    'Lecture Hall': Connection(200, TrafficMultiplier(1.0, 1.3, 1.6)),
                    'Auditorium': Connection(180, TrafficMultiplier(1.0, 1.4, 1.7))
                },
                node_type=NodeType.SPORTS,
                icon='⚽'
            ),
            'Auditorium': Node(
                x=600, y=400,
                connections={
                    'Cafeteria': Connection(140, TrafficMultiplier(1.0, 1.2, 1.5)),
                    'Sports Complex': Connection(180, TrafficMultiplier(1.0, 1.4, 1.7)),
                    'Hostel': Connection(150, TrafficMultiplier(1.2, 1.0, 1.3))
                },
                node_type=NodeType.FACILITY,
                icon='🎭'
            ),
            'Hostel': Node(
                x=750, y=380,
                connections={
                    'Auditorium': Connection(150, TrafficMultiplier(1.2, 1.0, 1.3)),
                    'Sports Complex': Connection(220, TrafficMultiplier(1.0, 1.1, 1.4))
                },
                node_type=NodeType.RESIDENCE,
                icon='🏠'
            )
        }
    
    def get_all_nodes(self) -> List[str]:
        """Get list of all node names"""
        return list(self.nodes.keys())
    
    def get_node_info(self, node_name: str) -> Optional[Node]:
        """Get information about a specific node"""
        return self.nodes.get(node_name)


class PathFinder:
    """Implements Dijkstra's algorithm for pathfinding"""
    
    def __init__(self, graph: CampusGraph):
        self.graph = graph
        self.blocked_paths: Set[Tuple[str, str]] = set()
        self.hazard_zones: Set[str] = set()
    
    def block_path(self, node1: str, node2: str):
        """Block a path between two nodes"""
        path_key = tuple(sorted([node1, node2]))
        self.blocked_paths.add(path_key)
    
    def unblock_path(self, node1: str, node2: str):
        """Unblock a path between two nodes"""
        path_key = tuple(sorted([node1, node2]))
        self.blocked_paths.discard(path_key)
    
    def add_hazard_zone(self, node: str):
        """Mark a node as hazardous"""
        if node not in self.graph.exit_points:
            self.hazard_zones.add(node)
    
    def remove_hazard_zone(self, node: str):
        """Remove hazard marking from a node"""
        self.hazard_zones.discard(node)
    
    def clear_hazards(self):
        """Clear all hazard zones"""
        self.hazard_zones.clear()
    
    def _get_effective_weight(
        self, 
        from_node: str, 
        to_node: str, 
        time_of_day: TimeOfDay,
        emergency_mode: bool = False
    ) -> float:
        """Calculate effective weight of an edge considering constraints"""
        # Check if path is blocked
        path_key = tuple(sorted([from_node, to_node]))
        if path_key in self.blocked_paths:
            return float('inf')
        
        # Check if connection exists
        node = self.graph.nodes.get(from_node)
        if not node or to_node not in node.connections:
            return float('inf')
        
        connection = node.connections[to_node]
        base_distance = connection.distance
        
        # Emergency mode: ignore traffic, add hazard penalties
        if emergency_mode:
            hazard_penalty = 0
            if from_node in self.hazard_zones:
                hazard_penalty += 500
            if to_node in self.hazard_zones:
                hazard_penalty += 500
            return base_distance + hazard_penalty
        
        # Normal mode: apply traffic multiplier
        if time_of_day == TimeOfDay.MORNING:
            multiplier = connection.traffic.morning
        elif time_of_day == TimeOfDay.AFTERNOON:
            multiplier = connection.traffic.afternoon
        else:
            multiplier = connection.traffic.evening
        
        return round(base_distance * multiplier)
    
    def dijkstra(
        self,
        start: str,
        end: str,
        time_of_day: TimeOfDay = TimeOfDay.MORNING,
        emergency_mode: bool = False,
        track_steps: bool = True
    ) -> PathResult:
        """
        Find shortest path using Dijkstra's algorithm
        
        Args:
            start: Starting node name
            end: Destination node name
            time_of_day: Time of day for traffic calculation
            emergency_mode: Enable emergency routing mode
            track_steps: Track algorithm steps for visualization
        
        Returns:
            PathResult containing path, distance, and algorithm steps
        """
        # Initialize distances and previous nodes
        distances = {node: float('inf') for node in self.graph.nodes}
        distances[start] = 0
        previous = {node: None for node in self.graph.nodes}
        
        # Priority queue: (distance, node)
        pq = [(0, start)]
        visited = set()
        steps = []
        
        # Initial step
        if track_steps:
            msg = f"🚨 EMERGENCY EVACUATION - {emergency_mode}" if emergency_mode else "🚀 Algorithm initialized"
            desc = f"Finding safest route to {end}" if emergency_mode else f"Starting from {start} at {time_of_day.value} time"
            steps.append({
                'type': 'init',
                'message': msg,
                'description': desc,
                'current': None,
                'distances': distances.copy()
            })
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            if track_steps:
                steps.append({
                    'type': 'visit',
                    'message': f"🔍 Exploring: {current}",
                    'description': f"Distance from source: {current_dist}m",
                    'current': current,
                    'distances': distances.copy()
                })
            
            # Found destination
            if current == end:
                if track_steps:
                    msg = f"✓ SAFE EXIT REACHED: {end}" if emergency_mode else f"✓ Destination reached: {end}"
                    desc = f"Evacuation distance: {current_dist}m" if emergency_mode else f"Total distance: {current_dist}m"
                    steps.append({
                        'type': 'found',
                        'message': msg,
                        'description': desc,
                        'current': current,
                        'distances': distances.copy()
                    })
                break
            
            # Explore neighbors
            node = self.graph.nodes[current]
            for neighbor in node.connections:
                if neighbor not in visited:
                    edge_weight = self._get_effective_weight(
                        current, neighbor, time_of_day, emergency_mode
                    )
                    
                    if edge_weight != float('inf'):
                        alt_distance = distances[current] + edge_weight
                        
                        if alt_distance < distances[neighbor]:
                            distances[neighbor] = alt_distance
                            previous[neighbor] = current
                            heapq.heappush(pq, (alt_distance, neighbor))
                            
                            if track_steps:
                                steps.append({
                                    'type': 'relax',
                                    'message': f"📊 Edge relaxation: {current} → {neighbor}",
                                    'description': f"New distance: {round(alt_distance)}m (edge: {edge_weight}m)",
                                    'current': current,
                                    'neighbor': neighbor,
                                    'distances': distances.copy()
                                })
        
        # Reconstruct path
        path = []
        current = end
        while current is not None:
            path.insert(0, current)
            current = previous[current]
        
        return PathResult(
            path=path,
            distance=distances[end],
            steps=steps,
            visited_nodes=visited
        )
    
    def find_nearest_exit(
        self, 
        start: str,
        time_of_day: TimeOfDay = TimeOfDay.MORNING
    ) -> Tuple[str, float]:
        """
        Find the nearest safe exit point for emergency evacuation
        
        Args:
            start: Current location
            time_of_day: Current time (for traffic consideration)
        
        Returns:
            Tuple of (nearest_exit_name, distance_to_exit)
        """
        min_distance = float('inf')
        nearest_exit = None
        
        for exit_point in self.graph.exit_points:
            result = self.dijkstra(
                start, 
                exit_point, 
                time_of_day, 
                emergency_mode=True,
                track_steps=False
            )
            
            if result.distance < min_distance:
                min_distance = result.distance
                nearest_exit = exit_point
        
        return nearest_exit, min_distance


# Example usage and API
def main():
    """Example usage of the Campus Navigation System"""
    
    # Initialize graph and pathfinder
    campus = CampusGraph()
    pathfinder = PathFinder(campus)
    
    print("=== Smart Campus Navigation System ===\n")
    
    # Example 1: Normal pathfinding
    print("Example 1: Normal Route (Morning)")
    result = pathfinder.dijkstra(
        start='Main Gate',
        end='Hostel',
        time_of_day=TimeOfDay.MORNING,
        emergency_mode=False
    )
    print(f"Path: {' → '.join(result.path)}")
    print(f"Distance: {result.distance}m")
    print(f"Nodes visited: {len(result.visited_nodes)}\n")
    
    # Example 2: With blocked path
    print("Example 2: Route with Construction Block")
    pathfinder.block_path('Library', 'Computer Lab')
    result = pathfinder.dijkstra(
        start='Main Gate',
        end='Hostel',
        time_of_day=TimeOfDay.AFTERNOON
    )
    print(f"Path: {' → '.join(result.path)}")
    print(f"Distance: {result.distance}m\n")
    pathfinder.unblock_path('Library', 'Computer Lab')
    
    # Example 3: Emergency evacuation
    print("Example 3: Emergency Evacuation")
    pathfinder.add_hazard_zone('Library')
    pathfinder.add_hazard_zone('Computer Lab')
    
    nearest_exit, distance = pathfinder.find_nearest_exit(
        start='Lecture Hall',
        time_of_day=TimeOfDay.MORNING
    )
    print(f"Nearest safe exit: {nearest_exit}")
    print(f"Evacuation distance: {distance}m")
    
    result = pathfinder.dijkstra(
        start='Lecture Hall',
        end=nearest_exit,
        emergency_mode=True
    )
    print(f"Evacuation route: {' → '.join(result.path)}")
    print(f"Hazard zones avoided: {pathfinder.hazard_zones}\n")
    
    # Example 4: Get all algorithm steps for visualization
    print("Example 4: Algorithm Steps (for frontend visualization)")
    result = pathfinder.dijkstra(
        start='Main Gate',
        end='Cafeteria',
        time_of_day=TimeOfDay.AFTERNOON,
        track_steps=True
    )
    print(f"Total algorithm steps: {len(result.steps)}")
    print("First 3 steps:")
    for i, step in enumerate(result.steps[:3]):
        print(f"  Step {i+1}: {step['message']}")


if __name__ == "__main__":
    main()
