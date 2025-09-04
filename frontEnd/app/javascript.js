// API Configuration
const API_BASE_URL = 'https://kslocaletool-production.up.railway.app';

// DOM Elements
const findUploadArea = document.getElementById('findUploadArea');
const findFileInput = document.getElementById('findFileInput');
const findTemplateType = document.getElementById('findTemplateType');
const findBtn = document.getElementById('findBtn');
const findResults = document.getElementById('findResults');
const findResultsContent = document.getElementById('findResultsContent');

const applyUploadArea = document.getElementById('applyUploadArea');
const applyFileInput = document.getElementById('applyFileInput');
const applyTemplateType = document.getElementById('applyTemplateType');
const applyBtn = document.getElementById('applyBtn');
const applyResults = document.getElementById('applyResults');
const applyResultsContent = document.getElementById('applyResultsContent');
const downloadSection = document.getElementById('downloadSection');
const downloadBtn = document.getElementById('downloadBtn');

const loadingOverlay = document.getElementById('loadingOverlay');
const toastContainer = document.getElementById('toastContainer');

// Global variables
let findFile = null;
let applyFile = null;
let processedFileContent = null;

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

function initializeEventListeners() {
    // Find section event listeners
    findUploadArea.addEventListener('click', () => findFileInput.click());
    findUploadArea.addEventListener('dragover', handleDragOver);
    findUploadArea.addEventListener('dragleave', handleDragLeave);
    findUploadArea.addEventListener('drop', (e) => handleDrop(e, 'find'));
    findFileInput.addEventListener('change', (e) => handleFileSelect(e, 'find'));
    findBtn.addEventListener('click', handleFindKoreanText);

    // Apply section event listeners
    applyUploadArea.addEventListener('click', () => applyFileInput.click());
    applyUploadArea.addEventListener('dragover', handleDragOver);
    applyUploadArea.addEventListener('dragleave', handleDragLeave);
    applyUploadArea.addEventListener('drop', (e) => handleDrop(e, 'apply'));
    applyFileInput.addEventListener('change', (e) => handleFileSelect(e, 'apply'));
    applyBtn.addEventListener('click', handleApplyTranslation);
    downloadBtn.addEventListener('click', handleDownload);
}

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e, section) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0], section);
    }
}

function handleFileSelect(e, section) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file, section);
    }
}

function handleFile(file, section) {
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.tsx')) {
        showToast('Please select a .tsx file', 'error');
        return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        showToast('File size must be less than 10MB', 'error');
        return;
    }

    if (section === 'find') {
        findFile = file;
        updateUploadArea(findUploadArea, file);
        findBtn.disabled = false;
    } else {
        applyFile = file;
        updateUploadArea(applyUploadArea, file);
        applyBtn.disabled = false;
    }
}

function updateUploadArea(uploadArea, file) {
    const uploadContent = uploadArea.querySelector('.upload-content');
    uploadContent.innerHTML = `
        <i class="fas fa-file-code"></i>
        <p><strong>${file.name}</strong></p>
        <span class="file-types">${formatFileSize(file.size)} • Ready to process</span>
    `;
    uploadArea.style.borderColor = '#48bb78';
    uploadArea.style.background = '#f0fff4';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// API Functions
async function handleFindKoreanText() {
    if (!findFile) {
        showToast('Please select a file first', 'error');
        return;
    }

    showLoading(true);
    
    try {
        const formData = new FormData();
        formData.append('file', findFile);
        formData.append('template_type', findTemplateType.value);

        const response = await fetch(`${API_BASE_URL}/api/search/`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        console.log("Response:", result);

        if (response.ok) {
            displayFindResults(result);
            showToast('Korean text search completed successfully!', 'success');
        } else {
            throw new Error(result.message || 'Search failed');
        }
    } catch (error) {
        console.error('Search error:', error);
        showToast(`Search failed: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

async function handleApplyTranslation() {
    if (!applyFile) {
        showToast('Please select a file first', 'error');
        return;
    }
    console.log("applyFile", applyFile)

    showLoading(true);
    
    try {
        const formData = new FormData();
        formData.append('file', applyFile);
        formData.append('template_type', applyTemplateType.value);
        formData.append('return_file', true);    

        const response = await fetch(`${API_BASE_URL}/api/apply/`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            // Get the processed file content
            const blob = await response.blob();
            processedFileContent = blob;
            
            // Get metadata from response headers
            const filename = response.headers.get('Content-Disposition')?.split('filename=')[1]?.replace(/"/g, '') || 'processed_file.tsx';
            
            displayApplyResults({
                success: true,
                filename: filename,
                message: 'Translation applied successfully!'
            });
            
            showToast('Translation applied successfully!', 'success');
            downloadSection.style.display = 'block';
        } else {
            const errorResult = await response.json();
            throw new Error(errorResult.message || 'Apply failed');
        }
    } catch (error) {
        console.error('Apply error:', error);
        showToast(`Translation failed: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function handleDownload() {
    if (!processedFileContent) {
        showToast('No processed file available', 'error');
        return;
    }

    const url = window.URL.createObjectURL(processedFileContent);
    const a = document.createElement('a');
    a.href = url;
    a.download = `processed_${applyFile.name}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    showToast('File downloaded successfully!', 'success');
}

// Display Functions
function displayFindResults(result) {
    findResults.style.display = 'block';
    
    if (!result.success || !result.elements || result.elements.length === 0) {
        findResultsContent.innerHTML = `
            <div class="result-stats">
                <h4>No Korean text found</h4>
                <p>All Korean text in your file is already properly templated.</p>
            </div>
        `;
        return;
    }

    let html = `
        <div class="result-stats">
            <h4>Search Results</h4>
            <div class="stat-item">
                <span class="stat-label">Total Korean elements found:</span>
                <span class="stat-value">${result.count}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Processing time:</span>
                <span class="stat-value">${result.duration || 'N/A'}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">File:</span>
                <span class="stat-value">${result.filename || 'Unknown'}</span>
            </div>
        </div>
    `;

    result.elements.forEach((element, index) => {
        html += `
            <div class="result-item">
                <h4>Element ${index + 1}</h4>
                <p><strong>Position:</strong> ${element.start}</p>
                <p><strong>Korean text:</strong></p>
                <span class="korean-text">${element.inner_text}</span>
            </div>
        `;
    });

    findResultsContent.innerHTML = html;
}

function displayApplyResults(result) {
    applyResults.style.display = 'block';
    
    let html = `
        <div class="result-stats">
            <h4>Translation Results</h4>
            <div class="stat-item">
                <span class="stat-label">Status:</span>
                <span class="stat-value" style="color: #48bb78;">Success</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">File processed:</span>
                <span class="stat-value">${result.filename || 'Unknown'}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Message:</span>
                <span class="stat-value">${result.message || 'Translation completed'}</span>
            </div>
        </div>
    `;

    applyResultsContent.innerHTML = html;
}

// Utility Functions
function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';
    
    toast.innerHTML = `
        <i class="${icon}"></i>
        <span class="toast-message">${message}</span>
    `;
    
    toastContainer.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Remove toast after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 5000);
}

// Reset functions
function resetFindSection() {
    findFile = null;
    findFileInput.value = '';
    findBtn.disabled = true;
    findResults.style.display = 'none';
    findResultsContent.innerHTML = '';
    
    const uploadContent = findUploadArea.querySelector('.upload-content');
    uploadContent.innerHTML = `
        <i class="fas fa-cloud-upload-alt"></i>
        <p>Drop your TSX file here or click to browse</p>
        <span class="file-types">Supported: .tsx files</span>
    `;
    findUploadArea.style.borderColor = '#cbd5e0';
    findUploadArea.style.background = '#f7fafc';
}

function resetApplySection() {
    applyFile = null;
    applyFileInput.value = '';
    applyBtn.disabled = true;
    applyResults.style.display = 'none';
    applyResultsContent.innerHTML = '';
    downloadSection.style.display = 'none';
    processedFileContent = null;
    
    const uploadContent = applyUploadArea.querySelector('.upload-content');
    uploadContent.innerHTML = `
        <i class="fas fa-cloud-upload-alt"></i>
        <p>Drop your TSX file here or click to browse</p>
        <span class="file-types">Supported: .tsx files</span>
    `;
    applyUploadArea.style.borderColor = '#cbd5e0';
    applyUploadArea.style.background = '#f7fafc';
}

// Add reset buttons functionality (optional)
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        resetFindSection();
        resetApplySection();
    }
});

// Error handling for network issues
window.addEventListener('online', function() {
    showToast('Connection restored', 'success');
});

window.addEventListener('offline', function() {
    showToast('Connection lost. Please check your internet connection.', 'error');
});
