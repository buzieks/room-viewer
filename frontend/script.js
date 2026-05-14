// Configuration
const CONFIG = {
    statusUpdateInterval: 1000, // 1 second
    motionEventsInterval: 3000, // 3 seconds
};

let motionBoxesEnabled = false;
let statusLight = null;
let statusText = null;

// Initialize on document load
document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    setupEventListeners();
    startStatusUpdates();
    startMotionEventsUpdates();
});

/**
 * Initialize DOM elements
 */
function initializeElements() {
    statusLight = document.getElementById('status-light');
    statusText = document.getElementById('status-text');
}

/**
 * Setup event listeners for buttons and controls
 */
function setupEventListeners() {
    // Toggle motion detection boxes
    document.getElementById('toggle-motion-boxes').addEventListener('click', toggleMotionBoxes);

    // Clear buffer
    document.getElementById('clear-buffer').addEventListener('click', clearBuffer);

    // Rollback slider
    const rollbackSlider = document.getElementById('rollback-seconds');
    rollbackSlider.addEventListener('input', (e) => {
        document.getElementById('rollback-value').textContent = e.target.value + 's';
    });

    // Rollback button
    document.getElementById('rollback-btn').addEventListener('click', getRollbackFrames);
}

/**
 * Toggle motion detection visualization
 */
async function toggleMotionBoxes() {
    try {
        const response = await fetch('/api/toggle-motion-boxes', { method: 'POST' });
        const data = await response.json();

        motionBoxesEnabled = data.show_motion_boxes;
        const btn = document.getElementById('toggle-motion-boxes');

        if (motionBoxesEnabled) {
            btn.classList.add('active');
            btn.textContent = 'Hide Motion Detection';
        } else {
            btn.classList.remove('active');
            btn.textContent = 'Show Motion Detection';
        }
    } catch (error) {
        console.error('Error toggling motion boxes:', error);
        showNotification('Failed to toggle motion boxes', 'error');
    }
}

/**
 * Clear video buffer
 */
async function clearBuffer() {
    if (!confirm('Are you sure you want to clear the buffer? This will reset all recorded frames.')) {
        return;
    }

    try {
        const response = await fetch('/api/clear-buffer', { method: 'POST' });
        const data = await response.json();
        showNotification('Buffer cleared successfully', 'success');
        updateStats(data.stats);
    } catch (error) {
        console.error('Error clearing buffer:', error);
        showNotification('Failed to clear buffer', 'error');
    }
}

/**
 * Get rollback frames
 */
async function getRollbackFrames() {
    const secondsBack = document.getElementById('rollback-seconds').value;

    try {
        const response = await fetch(`/api/rollback/${secondsBack}`);
        const data = await response.json();

        const infoDiv = document.getElementById('rollback-info');

        if (data.available) {
            infoDiv.textContent = `✓ ${data.total_frames} frames available from ${data.seconds_back}s ago`;
            infoDiv.classList.remove('hidden');
        } else {
            infoDiv.textContent = '✗ No frames available in buffer for this period';
            infoDiv.classList.remove('hidden');
        }

        // Auto-hide after 5 seconds
        setTimeout(() => {
            infoDiv.classList.add('hidden');
        }, 5000);
    } catch (error) {
        console.error('Error getting rollback frames:', error);
        showNotification('Failed to get rollback frames', 'error');
    }
}

/**
 * Start periodic status updates
 */
function startStatusUpdates() {
    updateStatus();
    setInterval(updateStatus, CONFIG.statusUpdateInterval);
}

/**
 * Update current status
 */
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        // Update status light and text
        if (data.camera_running) {
            statusLight.classList.add('active');
            statusText.textContent = 'Camera Running';
        } else {
            statusLight.classList.remove('active');
            statusText.textContent = 'Camera Offline';
        }

        // Update motion status
        const motionStatus = document.getElementById('motion-status');
        const motionOverlay = document.getElementById('motion-overlay');

        if (data.motion_detected) {
            motionStatus.textContent = 'Motion Detected ⚠️';
            motionStatus.style.color = '#ff6b6b';
            motionOverlay.classList.remove('hidden');
        } else {
            motionStatus.textContent = 'No motion';
            motionStatus.style.color = '#51cf66';
            motionOverlay.classList.add('hidden');
        }

        // Update stats
        updateStats(data.buffer_stats);

        // Update last update time
        const lastUpdate = new Date(data.timestamp);
        document.getElementById('last-update').textContent =
            `Last updated: ${lastUpdate.toLocaleTimeString()}`;
    } catch (error) {
        console.error('Error updating status:', error);
        statusLight.classList.remove('active');
        statusText.textContent = 'Connection Error';
    }
}

/**
 * Update buffer statistics display
 */
function updateStats(stats) {
    if (!stats) return;

    document.getElementById('total-frames').textContent = stats.total_frames.toLocaleString();
    document.getElementById('buffered-frames').textContent = stats.buffered_frames.toLocaleString();
}

/**
 * Start periodic motion events updates
 */
function startMotionEventsUpdates() {
    updateMotionEvents();
    setInterval(updateMotionEvents, CONFIG.motionEventsInterval);
}

/**
 * Update motion events list
 */
async function updateMotionEvents() {
    try {
        const response = await fetch('/api/motion-events');
        const data = await response.json();

        const eventsList = document.getElementById('motion-events-list');
        const countSpan = document.getElementById('motion-events-count');

        countSpan.textContent = data.count;

        if (data.count === 0) {
            eventsList.innerHTML = '<p class="placeholder">No motion events recorded yet</p>';
            return;
        }

        // Show last 5 events
        const recentEvents = data.events.slice(-5).reverse();

        eventsList.innerHTML = recentEvents.map((event, index) => {
            const timestamp = new Date(event.timestamp);
            const timeStr = timestamp.toLocaleTimeString();

            return `
                <div class="event-item">
                    <div class="timestamp">${timeStr}</div>
                    <div class="details">
                        Duration: ${event.duration_frames} frames (~${(event.duration_frames / 30).toFixed(1)}s)
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error updating motion events:', error);
    }
}

/**
 * Show notification (simple alert-like notification)
 */
function showNotification(message, type = 'info') {
    // You can extend this to show actual notifications
    console.log(`[${type.toUpperCase()}] ${message}`);

    // Simple visual feedback
    alert(message);
}

/**
 * Format time duration
 */
function formatDuration(seconds) {
    if (seconds < 60) {
        return `${seconds}s`;
    }

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;

    return `${minutes}m ${remainingSeconds}s`;
}
