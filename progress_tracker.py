#!/usr/bin/env python3
"""
Standalone Progress Tracker for Facetak
This module provides real-time progress tracking without modifying existing code
"""

import threading
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional

class ProgressTracker:
    """Standalone progress tracker that can be used across different modules"""
    
    def __init__(self):
        self.progress_data = {
            'overall': 0,
            'current_step': 'Initializing...',
            'steps': {
                'download': {'progress': 0, 'status': 'Waiting...', 'total_files': 0, 'processed_files': 0},
                'processing': {'progress': 0, 'status': 'Waiting...', 'total_photos': 0, 'processed_photos': 0},
                'face_detection': {'progress': 0, 'status': 'Waiting...', 'total_faces': 0, 'detected_faces': 0},
                'embedding': {'progress': 0, 'status': 'Waiting...', 'total_embeddings': 0, 'created_embeddings': 0},
                'storage': {'progress': 0, 'status': 'Waiting...', 'total_stored': 0, 'stored_count': 0}
            },
            'start_time': None,
            'estimated_time': None,
            'errors': [],
            'warnings': []
        }
        self.lock = threading.Lock()
        self.is_active = False
        
    def start_tracking(self):
        """Start progress tracking"""
        with self.lock:
            self.is_active = True
            self.progress_data['start_time'] = datetime.now().isoformat()
            self.progress_data['overall'] = 0
            # Reset all steps
            for step in self.progress_data['steps'].values():
                step['progress'] = 0
                step['status'] = 'Waiting...'
                step['total_files'] = 0
                step['processed_files'] = 0
            self.progress_data['errors'] = []
            self.progress_data['warnings'] = []
    
    def stop_tracking(self):
        """Stop progress tracking"""
        with self.lock:
            self.is_active = False
            self.progress_data['overall'] = 100
            for step in self.progress_data['steps'].values():
                step['progress'] = 100
                step['status'] = 'Completed'
    
    def update_step(self, step_name: str, **kwargs):
        """Update a specific step's progress"""
        if not self.is_active:
            return
            
        with self.lock:
            if step_name in self.progress_data['steps']:
                step = self.progress_data['steps'][step_name]
                for key, value in kwargs.items():
                    if key in step:
                        step[key] = value
                
                # Calculate step progress
                if step['total_files'] > 0:
                    step['progress'] = min(100, int((step['processed_files'] / step['total_files']) * 100))
                
                # Update overall progress
                self._calculate_overall_progress()
    
    def update_status(self, step_name: str, status: str):
        """Update status message for a step"""
        if not self.is_active:
            return
            
        with self.lock:
            if step_name in self.progress_data['steps']:
                self.progress_data['steps'][step_name]['status'] = status
    
    def set_total_files(self, step_name: str, total: int):
        """Set total files for a step"""
        if not self.is_active:
            return
            
        with self.lock:
            if step_name in self.progress_data['steps']:
                self.progress_data['steps'][step_name]['total_files'] = total
    
    def increment_processed(self, step_name: str, count: int = 1):
        """Increment processed count for a step"""
        if not self.is_active:
            return
            
        with self.lock:
            if step_name in self.progress_data['steps']:
                self.progress_data['steps'][step_name]['processed_files'] += count
                # Recalculate progress
                self.update_step(step_name)
    
    def add_error(self, error: str):
        """Add an error message"""
        with self.lock:
            self.progress_data['errors'].append({
                'message': error,
                'timestamp': datetime.now().isoformat()
            })
    
    def add_warning(self, warning: str):
        """Add a warning message"""
        with self.lock:
            self.progress_data['warnings'].append({
                'message': warning,
                'timestamp': datetime.now().isoformat()
            })
    
    def _calculate_overall_progress(self):
        """Calculate overall progress across all steps"""
        total_progress = 0
        step_count = len(self.progress_data['steps'])
        
        for step in self.progress_data['steps'].values():
            total_progress += step['progress']
        
        self.progress_data['overall'] = min(100, int(total_progress / step_count))
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress data"""
        with self.lock:
            # Calculate estimated time if we have progress
            if self.progress_data['overall'] > 0 and self.progress_data['start_time']:
                elapsed = (datetime.now() - datetime.fromisoformat(self.progress_data['start_time'])).total_seconds()
                if self.progress_data['overall'] > 0:
                    estimated_total = (elapsed / self.progress_data['overall']) * 100
                    remaining = max(0, estimated_total - elapsed)
                    self.progress_data['estimated_time'] = f"{int(remaining)}s remaining"
            
            return self.progress_data.copy()
    
    def reset(self):
        """Reset all progress data"""
        with self.lock:
            self.is_active = False
            self.progress_data = {
                'overall': 0,
                'current_step': 'Initializing...',
                'steps': {
                    'download': {'progress': 0, 'status': 'Waiting...', 'total_files': 0, 'processed_files': 0},
                    'processing': {'progress': 0, 'status': 'Waiting...', 'total_photos': 0, 'processed_photos': 0},
                    'face_detection': {'progress': 0, 'status': 'Waiting...', 'total_faces': 0, 'detected_faces': 0},
                    'embedding': {'progress': 0, 'status': 'Waiting...', 'total_embeddings': 0, 'created_embeddings': 0},
                    'storage': {'progress': 0, 'status': 'Waiting...', 'total_stored': 0, 'stored_count': 0}
                },
                'start_time': None,
                'estimated_time': None,
                'errors': [],
                'warnings': []
            }

# Global progress tracker instance
progress_tracker = ProgressTracker()

# Convenience functions for easy use
def start_progress():
    """Start progress tracking"""
    progress_tracker.start_tracking()

def stop_progress():
    """Stop progress tracking"""
    progress_tracker.stop_tracking()

def update_progress(step_name: str, **kwargs):
    """Update progress for a step"""
    progress_tracker.update_step(step_name, **kwargs)

def set_status(step_name: str, status: str):
    """Set status for a step"""
    progress_tracker.update_status(step_name, status)

def set_total(step_name: str, total: int):
    """Set total for a step"""
    progress_tracker.set_total_files(step_name, total)

def increment(step_name: str, count: int = 1):
    """Increment processed count for a step"""
    progress_tracker.increment_processed(step_name, count)

def get_progress():
    """Get current progress data"""
    return progress_tracker.get_progress()

def reset_progress():
    """Reset progress data"""
    progress_tracker.reset()

def add_error(error: str):
    """Add error message"""
    progress_tracker.add_error(error)

def add_warning(warning: str):
    """Add warning message"""
    progress_tracker.add_warning(warning)
