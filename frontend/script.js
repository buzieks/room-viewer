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
    setupMobileOptimizations();
});

/**
 * Initialize DOM elements
 */
function initializeElements() {
    statusLight = document.getElementById('status-light');
    statusText = document.getElementById('status-text');
}

/**
 * Mobile optimizations
 */
function setupMobileOptimizations() {
    // Prevent zoom on double tap for buttons
    document.addEventListener('touchstart', function(e) {
        if (e.target.closest('.btn')) {
            e.preventDefault();
            e.target.closest('.btn').click();
        }
    }, { passive: false });

    // Add touch feedback
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('touchstart', () => {
            btn.style.transform = 'scale(0.95)';
        });
        btn.addEventListener('touchend', () => {
            btn.style.transform = '';
        });
    });

    // Improve video responsiveness on mobile
    const videoContainer = document.querySelector('.video-container');
    if (videoContainer) {
        videoContainer.addEventListener('fullscreenchange', handleFullscreenChange);
    }
}

/**
 * Handle fullscreen changes
 */
function handleFullscreenChange() {
    const videoStream = document.getElementById('video-stream');
    if (document.fullscreenElement) {
        videoStream.style.objectFit = 'contain';
    } else {
        videoStream.style.objectFit = 'cover';
    }
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
        const value = e.target.value;
        document.getElementById('rollback-value').textContent = value + 's';
        
        // Update visual feedback
        const percentage = (value - 1) / 9 * 100;
        e.target.style.background = `linear-gradient(to right, #667eea 0%, #667eea ${percentage}%, #e0e0e0 ${percentage}%, #e0e0e0 100%)`;
    });

    // Initialize slider gradient
    const slider = document.getElementById('rollback-seconds');
    const value = slider.value;
    const percentage = (value - 1) / 9 * 100;
    slider.style.background = `linear-gradient(to right, #667eea 0%, #667eea ${percentage}%, #e0e0e0 ${percentage}%, #e0e0e0 100%)`;

    // Rollback button
    document.getElementById('rollback-btn').addEventListener('click', getRollbackFrames);

    // Make video fullscreen on click (mobile friendly)
    document.getElementById('video-stream').addEventListener('click', requestVideoFullscreen);
}

/**
 * Request fullscreen for video
 */
function requestVideoFullscreen() {
    const videoContainer = document.querySelector('.video-container');
    if (videoContainer.requestFullscreen) {
        videoContainer.requestFullscreen();
    } else if (videoContainer.webkitRequestFullscreen) {
        videoContainer.webkitRequestFullscreen();
    }
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
            btn.innerHTML = '<span class="btn-icon">👁️</span><span class="btn-text">Hide Detection</span>';
        } else {
            btn.classList.remove('active');
            btn.innerHTML = '<span class="btn-icon">👁️</span><span class="btn-text">Motion Detection</span>';
        }
    } catch (error) {
        console.error('Error toggling motion boxes:', error);
        showNotification('Failed to toggle motion detection', 'error');
    }
}

/**
 * Clear video buffer
 */
async function clearBuffer() {
    if (!confirm('Clear all buffered frames? This cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch('/api/clear-buffer', { method: 'POST' });
        const data = await response.json();
        showNotification('✓ Buffer cleared successfully', 'success');
        updateStats(data.stats);
    } catch (error) {
        console.error('Error clearing buffer:', error);
        showNotification('✗ Failed to clear buffer', 'error');
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
            infoDiv.innerHTML = `
                <strong>✓ ${data.total_frames} frames available</strong><br>
                <small>From ${data.seconds_back}s ago</small>
            `;
            infoDiv.classList.remove('hidden');
        } else {
            infoDiv.innerHTML = `<strong>✗ No frames available</strong><br><small>for this period</small>`;
            infoDiv.classList.remove('hidden');
        }

        // Auto-hide after 4 seconds
        setTimeout(() => {
            infoDiv.classList.add('hidden');
        }, 4000);
    } catch (error) {
        console.error('Error getting rollback frames:', error);
        showNotification('✗ Failed to get rollback frames', 'error');
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
            statusText.textContent = 'Camera Online';
        } else {
            statusLight.classList.remove('active');
            statusText.textContent = 'Camera Offline';
        }

        // Update motion status
        const motionStatus = document.getElementById('motion-status');
        const motionOverlay = document.getElementById('motion-overlay');

        if (data.motion_detected) {
            motionStatus.textContent = 'Motion Detected 🚨';
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

    // Use formatting with K for thousands
    const formatNumber = (n) => {
        if (n >= 1000) {
            return (n / 1000).toFixed(1) + 'K';
        }
        return n.toString();
    };

    document.getElementById('total-frames').textContent = formatNumber(stats.total_frames);
    document.getElementById('buffered-frames').textContent = formatNumber(stats.buffered_frames);
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
            eventsList.innerHTML = '<p class="placeholder">No motion events yet</p>';
            return;
        }

        // Show last 5 events
        const recentEvents = data.events.slice(-5).reverse();

        eventsList.innerHTML = recentEvents.map((event, index) => {
            const timestamp = new Date(event.timestamp);
            const timeStr = timestamp.toLocaleTimeString();
            const durationStr = (event.duration_frames / 30).toFixed(1);

            return `
                <div class="event-item" title="Motion event on ${timestamp.toLocaleDateString()}">
                    <div class="timestamp">${timeStr}</div>
                    <div class="details">
                        ${event.duration_frames} frames (~${durationStr}s)
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error updating motion events:', error);
    }
}

/**
 * Show notification (improved version)
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        background: ${type === 'success' ? '#51cf66' : type === 'error' ? '#ff6b6b' : '#667eea'};
        color: white;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        animation: slideInRight 0.3s ease;
        max-width: 90%;
    `;

    document.body.appendChild(notification);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
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

/**
 * Add notification animations to stylesheet
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(100px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        @keyframes slideOutRight {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100px);
            }
        }
    `;
    document.head.appendChild(style);
})();
