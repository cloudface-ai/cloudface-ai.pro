#!/usr/bin/env python3
"""
Standalone Progress Endpoint for Facetak
This provides a Flask endpoint for progress updates without modifying existing code
"""

from flask import Flask, Response, jsonify
from progress_tracker import *
import json
import time

def create_progress_endpoint(app):
    """Add progress endpoint to existing Flask app"""
    
    @app.route('/progress')
    def get_progress():
        """Get current progress data"""
        progress_data = get_progress()
        return jsonify(progress_data)
    
    @app.route('/progress/stream')
    def stream_progress():
        """Stream progress updates using Server-Sent Events"""
        def generate():
            while True:
                progress_data = get_progress()
                
                # Check if progress is complete
                if progress_data['overall'] >= 100:
                    yield f"data: {json.dumps(progress_data)}\n\n"
                    break
                
                # Send progress data
                yield f"data: {json.dumps(progress_data)}\n\n"
                time.sleep(0.5)  # Update every 500ms
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Cache-Control'
            }
        )
    
    @app.route('/progress/reset')
    def reset_progress_endpoint():
        """Reset progress data"""
        reset_progress()
        return jsonify({'success': True, 'message': 'Progress reset'})
    
    @app.route('/progress/start')
    def start_progress_endpoint():
        """Start progress tracking"""
        start_progress()
        return jsonify({'success': True, 'message': 'Progress tracking started'})
    
    @app.route('/progress/stop')
    def stop_progress_endpoint():
        """Stop progress tracking"""
        stop_progress()
        return jsonify({'success': True, 'message': 'Progress tracking stopped'})

# Example of how to integrate with existing Flask app:
"""
# In your existing web_server.py, just add these lines:

from progress_endpoint import create_progress_endpoint

# After creating your Flask app, add:
create_progress_endpoint(app)

# That's it! Now you have these new endpoints:
# - GET /progress - Get current progress
# - GET /progress/stream - Stream progress updates (SSE)
# - POST /progress/reset - Reset progress
# - POST /progress/start - Start progress tracking
# - POST /progress/stop - Stop progress tracking
"""
