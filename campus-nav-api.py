"""
Flask REST API for Smart Campus Navigation System
Connects Python backend logic with React frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from campus_navigation import (
    CampusGraph, 
    PathFinder, 
    TimeOfDay, 
    EmergencyType
)

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize global instances
campus_graph = CampusGraph()
path_finder = PathFinder(campus_graph)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Campus Navigation API is running'})


@app.route('/api/graph', methods=['GET'])
def get_graph():
    """
    Get complete campus graph structure
    Returns all nodes with their positions and connections
    """
    graph_data = {}
    for node_name, node in campus_graph.nodes.items():
        connections = {}
        for conn_name, conn in node.connections.items():
            connections[conn_name] = {
                'distance': conn.distance,
                'traffic': {
                    'morning': conn.traffic.morning,
                    'afternoon': conn.traffic.afternoon,
                    'evening': conn.traffic.evening
                }
            }
        
        graph_data[node_name] = {
            'x': node.x,
            'y': node.y,
            'type': node.node_type.value,
            'icon': node.icon,
            'connections': connections
        }
    
    return jsonify({
        'nodes': graph_data,
        'exit_points': campus_graph.exit_points
    })


@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    """Get list of all node names"""
    return jsonify({'nodes': campus_graph.get_all_nodes()})


@app.route('/api/path', methods=['POST'])
def find_path():
    """
    Find shortest path between two nodes
    
    Request body:
    {
        "start": "Main Gate",
        "end": "Hostel",
        "time_of_day": "morning",
        "emergency_mode": false,
        "track_steps": true
    }
    """
    data = request.get_json()
    
    start = data.get('start')
    end = data.get('end')
    time_str = data.get('time_of_day', 'morning')
    emergency_mode = data.get('emergency_mode', False)
    track_steps = data.get('track_steps', True)
    
    # Validate inputs
    if not start or not end:
        return jsonify({'error': 'start and end nodes are required'}), 400
    
    if start not in campus_graph.nodes or end not in campus_graph.nodes:
        return jsonify({'error': 'Invalid node names'}), 400
    
    # Convert time string to enum
    try:
        time_of_day = TimeOfDay[time_str.upper()]
    except KeyError:
        return jsonify({'error': 'Invalid time_of_day. Use: morning, afternoon, or evening'}), 400
    
    # Find path
    result = path_finder.dijkstra(
        start=start,
        end=end,
        time_of_day=time_of_day,
        emergency_mode=emergency_mode,
        track_steps=track_steps
    )
    
    return jsonify({
        'path': result.path,
        'distance': result.distance,
        'steps': result.steps,
        'visited_nodes': list(result.visited_nodes)
    })


@app.route('/api/emergency/nearest-exit', methods=['POST'])
def find_nearest_exit():
    """
    Find nearest safe exit for emergency evacuation
    
    Request body:
    {
        "start": "Lecture Hall",
        "time_of_day": "morning"
    }
    """
    data = request.get_json()
    
    start = data.get('start')
    time_str = data.get('time_of_day', 'morning')
    
    if not start:
        return jsonify({'error': 'start node is required'}), 400
    
    if start not in campus_graph.nodes:
        return jsonify({'error': 'Invalid node name'}), 400
    
    try:
        time_of_day = TimeOfDay[time_str.upper()]
    except KeyError:
        return jsonify({'error': 'Invalid time_of_day'}), 400
    
    nearest_exit, distance = path_finder.find_nearest_exit(start, time_of_day)
    
    return jsonify({
        'nearest_exit': nearest_exit,
        'distance': distance
    })


@app.route('/api/paths/block', methods=['POST'])
def block_path():
    """
    Block a path between two nodes
    
    Request body:
    {
        "node1": "Library",
        "node2": "Computer Lab"
    }
    """
    data = request.get_json()
    
    node1 = data.get('node1')
    node2 = data.get('node2')
    
    if not node1 or not node2:
        return jsonify({'error': 'Both node1 and node2 are required'}), 400
    
    path_finder.block_path(node1, node2)
    
    return jsonify({
        'message': f'Path between {node1} and {node2} blocked',
        'blocked_paths': [list(p) for p in path_finder.blocked_paths]
    })


@app.route('/api/paths/unblock', methods=['POST'])
def unblock_path():
    """
    Unblock a path between two nodes
    
    Request body:
    {
        "node1": "Library",
        "node2": "Computer Lab"
    }
    """
    data = request.get_json()
    
    node1 = data.get('node1')
    node2 = data.get('node2')
    
    if not node1 or not node2:
        return jsonify({'error': 'Both node1 and node2 are required'}), 400
    
    path_finder.unblock_path(node1, node2)
    
    return jsonify({
        'message': f'Path between {node1} and {node2} unblocked',
        'blocked_paths': [list(p) for p in path_finder.blocked_paths]
    })


@app.route('/api/paths/blocked', methods=['GET'])
def get_blocked_paths():
    """Get list of all blocked paths"""
    return jsonify({
        'blocked_paths': [list(p) for p in path_finder.blocked_paths]
    })


@app.route('/api/hazards/add', methods=['POST'])
def add_hazard():
    """
    Mark a node as hazardous
    
    Request body:
    {
        "node": "Library"
    }
    """
    data = request.get_json()
    node = data.get('node')
    
    if not node:
        return jsonify({'error': 'node is required'}), 400
    
    if node not in campus_graph.nodes:
        return jsonify({'error': 'Invalid node name'}), 400
    
    path_finder.add_hazard_zone(node)
    
    return jsonify({
        'message': f'{node} marked as hazardous',
        'hazard_zones': list(path_finder.hazard_zones)
    })


@app.route('/api/hazards/remove', methods=['POST'])
def remove_hazard():
    """
    Remove hazard marking from a node
    
    Request body:
    {
        "node": "Library"
    }
    """
    data = request.get_json()
    node = data.get('node')
    
    if not node:
        return jsonify({'error': 'node is required'}), 400
    
    path_finder.remove_hazard_zone(node)
    
    return jsonify({
        'message': f'Hazard removed from {node}',
        'hazard_zones': list(path_finder.hazard_zones)
    })


@app.route('/api/hazards/clear', methods=['POST'])
def clear_hazards():
    """Clear all hazard zones"""
    path_finder.clear_hazards()
    
    return jsonify({
        'message': 'All hazards cleared',
        'hazard_zones': []
    })


@app.route('/api/hazards', methods=['GET'])
def get_hazards():
    """Get list of all hazard zones"""
    return jsonify({
        'hazard_zones': list(path_finder.hazard_zones)
    })


@app.route('/api/reset', methods=['POST'])
def reset_state():
    """Reset all blocked paths and hazards"""
    path_finder.blocked_paths.clear()
    path_finder.clear_hazards()
    
    return jsonify({
        'message': 'All constraints reset',
        'blocked_paths': [],
        'hazard_zones': []
    })


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("=" * 50)
    print("Smart Campus Navigation API")
    print("=" * 50)
    print("\nAPI Endpoints:")
    print("  GET  /api/health              - Health check")
    print("  GET  /api/graph               - Get campus graph")
    print("  GET  /api/nodes               - Get all nodes")
    print("  POST /api/path                - Find shortest path")
    print("  POST /api/emergency/nearest-exit - Find nearest exit")
    print("  POST /api/paths/block         - Block a path")
    print("  POST /api/paths/unblock       - Unblock a path")
    print("  GET  /api/paths/blocked       - Get blocked paths")
    print("  POST /api/hazards/add         - Add hazard zone")
    print("  POST /api/hazards/remove      - Remove hazard zone")
    print("  POST /api/hazards/clear       - Clear all hazards")
    print("  GET  /api/hazards             - Get hazard zones")
    print("  POST /api/reset               - Reset all constraints")
    print("\nStarting server on http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
