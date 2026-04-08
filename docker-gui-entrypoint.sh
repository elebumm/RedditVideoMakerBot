#!/bin/bash
set -e

# Start virtual framebuffer
Xvfb :99 -screen 0 1920x1080x24 &
sleep 1

# Start lightweight window manager
fluxbox &

# Start VNC server (no password by default, use -rfbauth for security)
x11vnc -display :99 -forever -nopw -rfbport ${VNC_PORT:-5900} &

# Start noVNC web client (accessible via browser at http://localhost:6080)
websockify --web /usr/share/novnc/ ${NOVNC_PORT:-6080} localhost:${VNC_PORT:-5900} &

echo "============================================"
echo " GUI is available at:"
echo "   VNC:   vnc://localhost:${VNC_PORT:-5900}"
echo "   Web:   http://localhost:${NOVNC_PORT:-6080}/vnc.html"
echo "============================================"

# Run the main command
exec "$@"
