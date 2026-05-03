// Detection page JavaScript for camera and upload functionality

let stream = null;
const video = document.getElementById('videoElement');

// Upload functionality
const uploadForm = document.getElementById('uploadForm');

if (uploadForm) {
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const file = document.getElementById('imageFile').files[0];
        if (!file) {
            alert('Please select an image file');
            return;
        }

        const formData = new FormData(uploadForm);
        
        try {
            const response = await fetch('/detect', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            showDetectionResult(result);
        } catch (error) {
            console.error('Error:', error);
            alert('Error during detection: ' + error.message);
        }
    });
}

function showDetectionResult(result) {
    if (!result.success) {
        alert('Detection failed: ' + result.error + (result.solution ? '\n\nSolution: ' + result.solution : ''));
        return;
    }

    const resultDiv = document.getElementById('detectionResult');
    document.getElementById('predictedClass').textContent = result.predicted_class.toUpperCase();
    document.getElementById('confidenceScore').textContent = (result.confidence * 100).toFixed(2) + '%';
    
    // Display severity with appropriate styling
    const severityBadge = document.getElementById('severityBadge');
    if (result.severity) {
        const severityConfig = {
            'good': { text: 'Good Condition', class: 'bg-success' },
            'bad': { text: 'Bad Condition', class: 'bg-warning' },
            'worse': { text: 'Worse Condition', class: 'bg-danger' },
            'far_from_saving': { text: 'Far From Saving', class: 'bg-dark' }
        };
        
        const config = severityConfig[result.severity] || { text: 'Unknown', class: 'bg-secondary' };
        severityBadge.textContent = config.text;
        severityBadge.className = `badge fs-6 ${config.class}`;
    }
    
    // Show warning if using mock predictions
    if (result.warning) {
        const warningDiv = document.createElement('div');
        warningDiv.className = 'alert alert-warning mt-3';
        warningDiv.innerHTML = `
            <strong>⚠️ Warning:</strong> ${result.warning}
            <br><small>${result.solution}</small>
        `;
        resultDiv.appendChild(warningDiv);
    }
    
    resultDiv.style.display = 'block';
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

// Camera functionality
const startCameraBtn = document.getElementById('startCamera');
const captureImageBtn = document.getElementById('captureImage');
const stopCameraBtn = document.getElementById('stopCamera');

if (startCameraBtn) {
    startCameraBtn.addEventListener('click', async function() {
        try {
            // Request camera with specific constraints for better compatibility
            const constraints = {
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'environment' // Use back camera on mobile if available
                }
            };
            
            stream = await navigator.mediaDevices.getUserMedia(constraints);
            video.srcObject = stream;
            
            // Wait for video metadata to load
            video.addEventListener('loadedmetadata', function() {
                // Ensure video dimensions are set
                video.play().then(() => {
                    startCameraBtn.disabled = true;
                    captureImageBtn.disabled = false;
                    stopCameraBtn.disabled = false;
                    console.log('Camera ready:', video.videoWidth, 'x', video.videoHeight);
                }).catch(err => {
                    console.error('Error playing video:', err);
                    alert('Error starting camera video stream');
                });
            }, { once: true });
            
            // Fallback: enable buttons after a short delay if metadata doesn't load
            setTimeout(() => {
                if (video.videoWidth > 0 && video.videoHeight > 0) {
                    startCameraBtn.disabled = true;
                    captureImageBtn.disabled = false;
                    stopCameraBtn.disabled = false;
                }
            }, 1000);
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            let errorMessage = 'Error accessing camera: ';
            if (error.name === 'NotAllowedError') {
                errorMessage += 'Camera permission denied. Please allow camera access and try again.';
            } else if (error.name === 'NotFoundError') {
                errorMessage += 'No camera found. Please connect a camera and try again.';
            } else {
                errorMessage += error.message;
            }
            alert(errorMessage);
        }
    });
}

if (stopCameraBtn) {
    stopCameraBtn.addEventListener('click', function() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            video.srcObject = null;
            
            startCameraBtn.disabled = false;
            captureImageBtn.disabled = true;
            stopCameraBtn.disabled = true;
        }
    });
}

if (captureImageBtn) {
    captureImageBtn.addEventListener('click', async function() {
        const location = document.getElementById('cameraLocationInput').value.trim();
        if (!location) {
            alert('Please enter the location where you\'re taking this photo');
            return;
        }

        // Check if video is ready and has valid dimensions
        if (!video || !video.videoWidth || !video.videoHeight) {
            alert('Camera is not ready. Please wait a moment and try again.');
            return;
        }

        // Wait for video to be ready
        if (video.readyState !== video.HAVE_ENOUGH_DATA) {
            alert('Camera is still initializing. Please wait a moment.');
            return;
        }

        try {
            // Capture image from video
            const canvas = document.createElement('canvas');
            // Ensure we use the actual video dimensions
            const videoWidth = video.videoWidth || 640;
            const videoHeight = video.videoHeight || 480;
            
            canvas.width = videoWidth;
            canvas.height = videoHeight;
            
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, videoWidth, videoHeight);
            
            // Convert to JPEG with high quality
            const imageData = canvas.toDataURL('image/jpeg', 0.95);
            
            // Verify image data was created
            if (!imageData || imageData.length < 100) {
                throw new Error('Failed to capture image from camera');
            }
            
            // Send to server
            const formData = new FormData();
            formData.append('camera_image', imageData);
            formData.append('location', location);
            
            // Show loading state
            captureImageBtn.disabled = true;
            captureImageBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            
            const response = await fetch('/detect', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            // Restore button state
            captureImageBtn.disabled = false;
            captureImageBtn.innerHTML = '<i class="fas fa-camera me-2"></i>Capture & Detect';
            
            showDetectionResult(result);
        } catch (error) {
            console.error('Error:', error);
            
            // Restore button state
            captureImageBtn.disabled = false;
            captureImageBtn.innerHTML = '<i class="fas fa-camera me-2"></i>Capture & Detect';
            
            alert('Error during detection: ' + error.message);
        }
    });
}

// Clean up camera stream on page unload
window.addEventListener('beforeunload', function() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
});

