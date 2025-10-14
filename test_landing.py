#!/usr/bin/env python
"""
Simple test server to view the landing page
Run: python test_landing.py
Then open: http://localhost:5555
"""

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def landing():
    return render_template('cloudface_pro/landing.html')

if __name__ == '__main__':
    print("=" * 70)
    print("CloudFace Pro - Landing Page Preview")
    print("=" * 70)
    print("")
    print("🌐 Open in browser: http://localhost:5555")
    print("")
    print("Press Ctrl+C to stop")
    print("")
    app.run(host='0.0.0.0', port=5555, debug=True)

