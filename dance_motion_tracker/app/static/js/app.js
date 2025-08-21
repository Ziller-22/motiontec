/**
 * Dance Motion Tracker - Frontend JavaScript
 */

// Global application state
const AppState = {
    currentSessionId: null,
    processingInterval: null,
    uploadProgress: 0,
    isProcessing: false
};

// Utility functions
const Utils = {
    /**
     * Format file size in human readable format
     */
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    /**
     * Format duration in human readable format
     */
    formatDuration: function(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    },

    /**
     * Show toast notification
     */
    showToast: function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        // Add to toast container (create if doesn't exist)
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    /**
     * Validate file type
     */
    isValidVideoFile: function(file) {
        const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/quicktime', 'video/x-msvideo', 'video/webm', 'video/x-matroska'];
        return validTypes.includes(file.type);
    },

    /**
     * Get file extension from filename
     */
    getFileExtension: function(filename) {
        return filename.split('.').pop().toLowerCase();
    }
};

// API functions
const API = {
    /**
     * Upload video file
     */
    uploadVideo: async function(file, progressCallback) {
        const formData = new FormData();
        formData.append('video', file);

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const progress = (e.loaded / e.total) * 100;
                    if (progressCallback) progressCallback(progress);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    resolve(JSON.parse(xhr.responseText));
                } else {
                    reject(new Error(JSON.parse(xhr.responseText).error || 'Upload failed'));
                }
            });

            xhr.addEventListener('error', () => {
                reject(new Error('Network error during upload'));
            });

            xhr.open('POST', '/upload');
            xhr.send(formData);
        });
    },

    /**
     * Start video processing
     */
    processVideo: async function(sessionId, options) {
        const response = await fetch(`/process/${sessionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(options)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Processing failed');
        }

        return response.json();
    },

    /**
     * Get processing status
     */
    getStatus: async function(sessionId) {
        const response = await fetch(`/status/${sessionId}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to get status');
        }

        return response.json();
    },

    /**
     * Get preview data
     */
    getPreview: async function(sessionId) {
        const response = await fetch(`/preview/${sessionId}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to get preview');
        }

        return response.json();
    },

    /**
     * Clean up session
     */
    cleanupSession: async function(sessionId) {
        const response = await fetch(`/cleanup/${sessionId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Cleanup failed');
        }

        return response.json();
    }
};

// UI Controllers
const UI = {
    /**
     * Initialize drag and drop for file upload
     */
    initializeDragDrop: function() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('videoFile');

        if (!uploadArea || !fileInput) return;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        uploadArea.addEventListener('drop', handleDrop, false);

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        function highlight() {
            uploadArea.classList.add('dragover');
        }

        function unhighlight() {
            uploadArea.classList.remove('dragover');
        }

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length > 0) {
                fileInput.files = files;
                UI.handleFileSelect(files[0]);
            }
        }
    },

    /**
     * Handle file selection
     */
    handleFileSelect: function(file) {
        if (!Utils.isValidVideoFile(file)) {
            Utils.showToast('Please select a valid video file', 'danger');
            return;
        }

        // Show file info
        const fileInfo = document.getElementById('fileInfo');
        if (fileInfo) {
            fileInfo.innerHTML = `
                <div class="alert alert-info">
                    <strong>Selected:</strong> ${file.name}<br>
                    <strong>Size:</strong> ${Utils.formatFileSize(file.size)}<br>
                    <strong>Type:</strong> ${file.type}
                </div>
            `;
        }
    },

    /**
     * Update upload progress
     */
    updateUploadProgress: function(progress) {
        const progressBar = document.getElementById('uploadProgressBar');
        const progressText = document.getElementById('uploadProgressText');
        
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }
        
        if (progressText) {
            progressText.textContent = `${Math.round(progress)}%`;
        }
        
        AppState.uploadProgress = progress;
    },

    /**
     * Show video information
     */
    showVideoInfo: function(videoInfo) {
        const videoInfoCard = document.getElementById('videoInfoCard');
        const videoInfoContent = document.getElementById('videoInfo');
        
        if (!videoInfoCard || !videoInfoContent) return;

        videoInfoContent.innerHTML = `
            <div class="row g-3">
                <div class="col-md-6">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-expand-arrows-alt text-primary me-2"></i>
                        <div>
                            <strong>Resolution</strong><br>
                            <span class="text-muted">${videoInfo.width} × ${videoInfo.height}</span>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-clock text-success me-2"></i>
                        <div>
                            <strong>Duration</strong><br>
                            <span class="text-muted">${Utils.formatDuration(videoInfo.duration)}</span>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-film text-info me-2"></i>
                        <div>
                            <strong>Frame Rate</strong><br>
                            <span class="text-muted">${videoInfo.fps.toFixed(2)} FPS</span>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-images text-warning me-2"></i>
                        <div>
                            <strong>Total Frames</strong><br>
                            <span class="text-muted">${videoInfo.frame_count.toLocaleString()}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        videoInfoCard.style.display = 'block';
        videoInfoCard.classList.add('fade-in-up');
    },

    /**
     * Update processing status
     */
    updateProcessingStatus: function(status) {
        const statusElement = document.getElementById('statusText');
        const spinnerElement = document.getElementById('processingSpinner');
        const progressBar = document.getElementById('processingProgressBar');
        
        if (statusElement) {
            const statusMessages = {
                'uploaded': 'Ready for processing',
                'processing': 'Analyzing video and extracting poses...',
                'completed': 'Processing completed successfully!',
                'failed': 'Processing failed'
            };
            
            statusElement.textContent = statusMessages[status.status] || status.status;
        }
        
        if (spinnerElement) {
            spinnerElement.style.display = status.status === 'processing' ? 'inline-block' : 'none';
        }
        
        // Update progress based on status
        if (progressBar) {
            const progressValues = {
                'uploaded': 0,
                'processing': 50,
                'completed': 100,
                'failed': 0
            };
            
            const progress = progressValues[status.status] || 0;
            progressBar.style.width = `${progress}%`;
        }
    },

    /**
     * Show processing results
     */
    showResults: function(status) {
        const resultsSummary = document.getElementById('resultsSummary');
        const downloadSection = document.getElementById('downloadSection');
        
        if (resultsSummary && status.pose_stats) {
            // Update statistics
            const framesElement = document.getElementById('framesProcessed');
            const confidenceElement = document.getElementById('avgConfidence');
            const durationElement = document.getElementById('videoDuration');
            const filesElement = document.getElementById('outputFiles');
            
            if (framesElement) framesElement.textContent = status.pose_stats.total_frames.toLocaleString();
            if (confidenceElement) confidenceElement.textContent = Math.round(status.pose_stats.avg_confidence * 100) + '%';
            if (durationElement) durationElement.textContent = Utils.formatDuration(status.pose_stats.duration);
            if (filesElement) filesElement.textContent = status.output_files.length;
            
            resultsSummary.style.display = 'block';
            resultsSummary.classList.add('fade-in-up');
        }
        
        // Create download buttons
        if (downloadSection && status.output_files) {
            UI.createDownloadButtons(status.output_files, AppState.currentSessionId);
            downloadSection.style.display = 'block';
            downloadSection.classList.add('slide-in-right');
        }
    },

    /**
     * Create download buttons
     */
    createDownloadButtons: function(outputFiles, sessionId) {
        const downloadLinks = document.getElementById('downloadLinks');
        if (!downloadLinks) return;
        
        downloadLinks.innerHTML = '';
        
        const fileTypeInfo = {
            'json': { label: 'JSON Data', icon: 'fas fa-file-code', color: 'primary' },
            'csv': { label: 'CSV Data', icon: 'fas fa-file-csv', color: 'success' },
            'blender': { label: 'Blender Data', icon: 'fas fa-cube', color: 'warning' },
            'overlay_video': { label: 'Overlay Video', icon: 'fas fa-video', color: 'info' },
            'statistics': { label: 'Statistics', icon: 'fas fa-chart-bar', color: 'secondary' }
        };
        
        outputFiles.forEach(fileType => {
            const info = fileTypeInfo[fileType] || { label: fileType.toUpperCase(), icon: 'fas fa-file', color: 'primary' };
            
            const col = document.createElement('div');
            col.className = 'col-md-4 col-lg-3 mb-3';
            
            const button = document.createElement('a');
            button.href = `/download/${sessionId}/${fileType}`;
            button.className = `btn btn-outline-${info.color} w-100 d-flex align-items-center justify-content-center`;
            button.style.minHeight = '60px';
            button.innerHTML = `
                <div class="text-center">
                    <i class="${info.icon} fa-lg d-block mb-1"></i>
                    <small>${info.label}</small>
                </div>
            `;
            
            // Add download tracking
            button.addEventListener('click', () => {
                Utils.showToast(`Downloading ${info.label}...`, 'info');
            });
            
            col.appendChild(button);
            downloadLinks.appendChild(col);
        });
    },

    /**
     * Show preview section
     */
    showPreview: function(previewData) {
        const previewSection = document.getElementById('previewSection');
        const previewContent = document.getElementById('previewContent');
        
        if (!previewSection || !previewContent) return;
        
        previewContent.innerHTML = `
            <div class="row">
                <div class="col-md-8">
                    <h6><i class="fas fa-chart-line me-2"></i>Pose Data Summary</h6>
                    <p>Successfully processed <strong>${previewData.total_frames}</strong> frames. 
                    Preview shows <strong>${previewData.preview_data.length}</strong> sample frames.</p>
                    
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Next Steps:</strong> Download the files above to use in your 3D animation software. 
                        The Blender data file includes bone mapping for easy import into rigged characters.
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-light">
                        <div class="card-body text-center">
                            <i class="fas fa-check-circle text-success fa-3x mb-2"></i>
                            <h6>Processing Complete</h6>
                            <p class="small text-muted">Your dance motion data is ready for download and use in 3D animation.</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        previewSection.style.display = 'block';
        previewSection.classList.add('fade-in-up');
    },

    /**
     * Reset UI to initial state
     */
    resetUI: function() {
        // Hide sections
        const sectionsToHide = ['videoInfoCard', 'resultsSection', 'previewSection'];
        sectionsToHide.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'none';
        });
        
        // Reset form
        const uploadForm = document.getElementById('uploadForm');
        if (uploadForm) uploadForm.reset();
        
        // Reset buttons
        const processBtn = document.getElementById('processBtn');
        if (processBtn) processBtn.disabled = true;
        
        // Clear file info
        const fileInfo = document.getElementById('fileInfo');
        if (fileInfo) fileInfo.innerHTML = '';
        
        // Reset progress
        UI.updateUploadProgress(0);
    }
};

// Main application controller
const App = {
    /**
     * Initialize application
     */
    init: function() {
        this.bindEvents();
        UI.initializeDragDrop();
        this.setupCleanupTimer();
    },

    /**
     * Bind event listeners
     */
    bindEvents: function() {
        // Upload form
        const uploadForm = document.getElementById('uploadForm');
        if (uploadForm) {
            uploadForm.addEventListener('submit', this.handleUpload.bind(this));
        }
        
        // Processing form
        const processingForm = document.getElementById('processingForm');
        if (processingForm) {
            processingForm.addEventListener('submit', this.handleProcessing.bind(this));
        }
        
        // File input change
        const videoFile = document.getElementById('videoFile');
        if (videoFile) {
            videoFile.addEventListener('change', (e) => {
                if (e.target.files[0]) {
                    UI.handleFileSelect(e.target.files[0]);
                }
            });
        }
        
        // Smoothing checkbox
        const applySmoothing = document.getElementById('applySmoothing');
        if (applySmoothing) {
            applySmoothing.addEventListener('change', this.updateSmoothingOptions);
        }
        
        // Page unload cleanup
        window.addEventListener('beforeunload', () => {
            if (AppState.currentSessionId) {
                // Attempt cleanup (may not complete due to page unload)
                API.cleanupSession(AppState.currentSessionId).catch(() => {});
            }
        });
    },

    /**
     * Handle video upload
     */
    handleUpload: async function(event) {
        event.preventDefault();
        
        const videoFile = document.getElementById('videoFile').files[0];
        if (!videoFile) {
            Utils.showToast('Please select a video file', 'warning');
            return;
        }
        
        if (!Utils.isValidVideoFile(videoFile)) {
            Utils.showToast('Please select a valid video file (MP4, AVI, MOV, etc.)', 'danger');
            return;
        }
        
        const uploadBtn = document.getElementById('uploadBtn');
        const uploadProgress = document.getElementById('uploadProgress');
        
        try {
            // Show progress and disable button
            uploadProgress.style.display = 'block';
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Uploading...';
            
            // Upload file
            const result = await API.uploadVideo(videoFile, UI.updateUploadProgress);
            
            // Store session ID and show video info
            AppState.currentSessionId = result.session_id;
            UI.showVideoInfo(result.video_info);
            
            // Enable processing
            const processBtn = document.getElementById('processBtn');
            if (processBtn) processBtn.disabled = false;
            
            Utils.showToast('Video uploaded successfully!', 'success');
            
        } catch (error) {
            Utils.showToast(error.message, 'danger');
        } finally {
            // Reset upload UI
            uploadProgress.style.display = 'none';
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="fas fa-cloud-upload-alt me-2"></i>Upload Video';
        }
    },

    /**
     * Handle video processing
     */
    handleProcessing: async function(event) {
        event.preventDefault();
        
        if (!AppState.currentSessionId) {
            Utils.showToast('Please upload a video first', 'warning');
            return;
        }
        
        // Collect processing options
        const options = {
            apply_smoothing: document.getElementById('applySmoothing').checked,
            smoothing_method: document.getElementById('smoothingMethod').value,
            create_overlay_video: document.getElementById('createOverlayVideo').checked,
            export_formats: []
        };
        
        // Collect export formats
        if (document.getElementById('exportJson').checked) options.export_formats.push('json');
        if (document.getElementById('exportCsv').checked) options.export_formats.push('csv');
        if (document.getElementById('exportBlender').checked) options.export_formats.push('blender');
        
        if (options.export_formats.length === 0) {
            Utils.showToast('Please select at least one export format', 'warning');
            return;
        }
        
        try {
            // Show results section and disable processing
            const resultsSection = document.getElementById('resultsSection');
            if (resultsSection) resultsSection.style.display = 'block';
            
            const processBtn = document.getElementById('processBtn');
            if (processBtn) {
                processBtn.disabled = true;
                processBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            }
            
            AppState.isProcessing = true;
            
            // Start processing
            await API.processVideo(AppState.currentSessionId, options);
            
            // Start status polling
            this.startStatusPolling();
            
        } catch (error) {
            Utils.showToast(error.message, 'danger');
            AppState.isProcessing = false;
            
            const processBtn = document.getElementById('processBtn');
            if (processBtn) {
                processBtn.disabled = false;
                processBtn.innerHTML = '<i class="fas fa-play me-2"></i>Start Processing';
            }
        }
    },

    /**
     * Start polling for processing status
     */
    startStatusPolling: function() {
        if (AppState.processingInterval) {
            clearInterval(AppState.processingInterval);
        }
        
        AppState.processingInterval = setInterval(async () => {
            try {
                const status = await API.getStatus(AppState.currentSessionId);
                UI.updateProcessingStatus(status);
                
                if (status.status === 'completed') {
                    clearInterval(AppState.processingInterval);
                    AppState.isProcessing = false;
                    
                    UI.showResults(status);
                    this.loadPreview();
                    
                    // Reset process button
                    const processBtn = document.getElementById('processBtn');
                    if (processBtn) {
                        processBtn.innerHTML = '<i class="fas fa-check me-2"></i>Completed';
                        processBtn.classList.remove('btn-success');
                        processBtn.classList.add('btn-outline-success');
                    }
                    
                    Utils.showToast('Processing completed successfully!', 'success');
                    
                } else if (status.status === 'failed') {
                    clearInterval(AppState.processingInterval);
                    AppState.isProcessing = false;
                    
                    Utils.showToast('Processing failed. Please try again.', 'danger');
                    
                    // Reset process button
                    const processBtn = document.getElementById('processBtn');
                    if (processBtn) {
                        processBtn.disabled = false;
                        processBtn.innerHTML = '<i class="fas fa-play me-2"></i>Start Processing';
                    }
                }
                
            } catch (error) {
                console.error('Status polling error:', error);
            }
        }, 2000);
    },

    /**
     * Load and display preview
     */
    loadPreview: async function() {
        try {
            const preview = await API.getPreview(AppState.currentSessionId);
            UI.showPreview(preview);
        } catch (error) {
            console.error('Preview loading error:', error);
        }
    },

    /**
     * Update smoothing options visibility
     */
    updateSmoothingOptions: function() {
        const smoothingEnabled = document.getElementById('applySmoothing').checked;
        const smoothingOptions = document.getElementById('smoothingOptions');
        
        if (smoothingOptions) {
            smoothingOptions.style.display = smoothingEnabled ? 'block' : 'none';
        }
    },

    /**
     * Setup periodic cleanup of old sessions
     */
    setupCleanupTimer: function() {
        // Clean up current session after 1 hour of inactivity
        let inactivityTimer;
        
        const resetTimer = () => {
            clearTimeout(inactivityTimer);
            inactivityTimer = setTimeout(() => {
                if (AppState.currentSessionId && !AppState.isProcessing) {
                    API.cleanupSession(AppState.currentSessionId).catch(() => {});
                    UI.resetUI();
                    AppState.currentSessionId = null;
                    Utils.showToast('Session cleaned up due to inactivity', 'info');
                }
            }, 60 * 60 * 1000); // 1 hour
        };
        
        // Reset timer on user activity
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
            document.addEventListener(event, resetTimer, true);
        });
        
        resetTimer();
    }
};

// Global functions for template compatibility
function showHelp() {
    const helpModal = new bootstrap.Modal(document.getElementById('helpModal'));
    helpModal.show();
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    App.init();
});

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { App, API, UI, Utils };
}