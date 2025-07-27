let socket = null;
let currentWorkshopId = null;

document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    initializeEventListeners();
    initializeDarkMode();
});

function initializeSocket() {
    if (typeof io !== 'undefined') {
        socket = io();
        
        socket.on('connect', function() {
            console.log('Connected to server');
        });
        
        socket.on('disconnect', function() {
            console.log('Disconnected from server');
        });
        
        socket.on('download_status', function(data) {
            updateDownloadStatus(data);
        });
        
        socket.on('download_output', function(data) {
            appendDownloadOutput(data);
        });
        
        socket.on('download_progress', function(data) {
            updateDownloadProgress(data);
        });
    }
}

function initializeEventListeners() {
    const workshopUrlInput = document.getElementById('workshopUrl');
    if (workshopUrlInput) {
        workshopUrlInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                parseWorkshopUrl();
            }
        });
    }
}

function parseWorkshopUrl() {
    const url = document.getElementById('workshopUrl').value.trim();
    if (!url) {
        showToast('Please enter a Steam Workshop URL or ID', 'warning');
        return;
    }

    const parseBtn = document.getElementById('parseBtn');
    if (parseBtn) {
        parseBtn.disabled = true;
        parseBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Parsing...';
    }

    fetch('/parse_workshop', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showWorkshopPreview(data);
            currentWorkshopId = data.id;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error parsing workshop URL', 'error');
    })
    .finally(() => {
        if (parseBtn) {
            parseBtn.disabled = false;
            parseBtn.innerHTML = '<i class="fas fa-search me-2"></i>Parse & Preview';
        }
    });
}

function showWorkshopPreview(data) {
    const previewDiv = document.getElementById('workshopPreview');
    const contentDiv = document.getElementById('previewContent');
    
    if (contentDiv) {
        contentDiv.innerHTML = `
            <div class="col-md-3">
                ${data.preview_url ? `
                    <img src="${data.preview_url}" class="img-fluid rounded shadow-sm" alt="Workshop Preview">
                ` : `
                    <div class="bg-light rounded d-flex align-items-center justify-content-center" style="height: 200px;">
                        <i class="fas fa-image fa-3x text-muted"></i>
                    </div>
                `}
            </div>
            <div class="col-md-9">
                <h5 class="card-title">${escapeHtml(data.title)}</h5>
                <p class="card-text">
                    <strong>Workshop ID:</strong> ${data.id}<br>
                    <strong>Steam URL:</strong> <a href="${data.url}" target="_blank" class="text-decoration-none">${data.url}</a>
                </p>
                <div class="badge bg-primary">Wallpaper Engine</div>
            </div>
        `;
    }
    
    if (previewDiv) {
        previewDiv.classList.remove('d-none');
    }
}

function startDownload() {
    if (!currentWorkshopId) {
        showToast('Please parse a workshop item first', 'warning');
        return;
    }

    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.disabled = true;
        downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Starting Download...';
    }

    fetch('/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ workshop_id: currentWorkshopId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast(data.error, 'error');
            if (downloadBtn) {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = '<i class="fas fa-download me-2"></i>Download Wallpaper';
            }
        } else {
            showToast('Download started!', 'success');
            addDownloadToQueue(currentWorkshopId);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error starting download', 'error');
        if (downloadBtn) {
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = '<i class="fas fa-download me-2"></i>Download Wallpaper';
        }
    });
}

function addDownloadToQueue(workshopId) {
    const queueDiv = document.getElementById('downloadQueue');
    
    if (queueDiv) {
        const emptyMessage = queueDiv.querySelector('.text-muted');
        if (emptyMessage) {
            queueDiv.innerHTML = '';
        }
        
        const downloadItem = document.createElement('div');
        downloadItem.className = 'download-item border rounded p-3 mb-3';
        downloadItem.id = `download-${workshopId}`;
        downloadItem.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="mb-0">Workshop ID: ${workshopId}</h6>
                <span class="badge bg-info" id="status-${workshopId}">Initializing...</span>
            </div>
            <div class="progress mb-2">
                <div class="progress-bar" id="progress-${workshopId}" role="progressbar" style="width: 0%"></div>
            </div>
            <div class="output-container">
                <div class="output-text" id="output-${workshopId}"></div>
            </div>
        `;
        
        queueDiv.appendChild(downloadItem);
    }
}

function updateDownloadStatus(data) {
    const statusBadge = document.getElementById(`status-${data.workshop_id}`);
    if (statusBadge) {
        let badgeClass = 'bg-info';
        switch(data.status) {
            case 'completed':
                badgeClass = 'bg-success';
                enableDownloadButton();
                break;
            case 'error':
                badgeClass = 'bg-danger';
                enableDownloadButton();
                break;
            case 'running':
                badgeClass = 'bg-warning';
                break;
        }
        statusBadge.className = `badge ${badgeClass}`;
        statusBadge.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
    }
    
    if (data.message) {
        showToast(data.message, data.status === 'error' ? 'error' : 'info');
    }
}

function enableDownloadButton() {
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = '<i class="fas fa-download me-2"></i>Download Wallpaper';
    }
}

function appendDownloadOutput(data) {
    const outputDiv = document.getElementById(`output-${data.workshop_id}`);
    if (outputDiv) {
        const line = document.createElement('div');
        line.className = 'output-line';
        line.textContent = data.output;
        outputDiv.appendChild(line);
        outputDiv.scrollTop = outputDiv.scrollHeight;
    }
}

function updateDownloadProgress(data) {
    const progressBar = document.getElementById(`progress-${data.workshop_id}`);
    if (progressBar) {
        progressBar.style.width = `${data.progress}%`;
        progressBar.textContent = `${data.progress.toFixed(1)}%`;
    }
}

function showToast(message, type = 'info') {
    let toastContainer = document.getElementById('toastContainer');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.id = 'toastContainer';
        document.body.appendChild(toastContainer);
    }
    
    const toastId = 'toast-' + Date.now();
    
    let bgClass = 'bg-info';
    let icon = 'fa-info-circle';
    
    switch(type) {
        case 'success':
            bgClass = 'bg-success';
            icon = 'fa-check-circle';
            break;
        case 'error':
            bgClass = 'bg-danger';
            icon = 'fa-exclamation-circle';
            break;
        case 'warning':
            bgClass = 'bg-warning';
            icon = 'fa-exclamation-triangle';
            break;
    }
    
    const toastHtml = `
        <div class="toast" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header ${bgClass} text-white">
                <i class="fas ${icon} me-2"></i>
                <strong class="me-auto">Notification</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${escapeHtml(message)}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    if (typeof bootstrap !== 'undefined') {
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
}

function searchWorkshop() {
    const query = document.getElementById('searchQuery').value.trim();
    const sort = document.getElementById('sortSelect').value;
    
    if (!query) {
        showToast('Please enter a search query', 'warning');
        return;
    }
    
    document.getElementById('workshopLoading').style.display = 'block';
    document.getElementById('workshopGrid').innerHTML = '';
    
    fetch('/api/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: query,
            sort: sort
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('workshopLoading').style.display = 'none';
        console.log('Search response:', data);
        
        if (data.success) {
            console.log('Results:', data.results);
            displayWorkshopResults(data.results);
            showToast(`Found ${data.results.length} results`, 'success');
        } else {
            console.log('Search failed:', data.error);
            showToast(data.error || 'Search failed', 'error');
            showEmptyState();
        }
    })
    .catch(error => {
        document.getElementById('workshopLoading').style.display = 'none';
        console.error('Error:', error);
        showToast('Failed to search workshop', 'error');
        showEmptyState();
    });
}

function browseTrending() {
    document.getElementById('searchQuery').value = '';
    document.getElementById('workshopLoading').style.display = 'block';
    document.getElementById('workshopGrid').innerHTML = '';
    
    fetch('/api/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: '',
            sort: 'trend'
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('workshopLoading').style.display = 'none';
        
        if (data.success) {
            displayWorkshopResults(data.results);
            showToast(`Loaded ${data.results.length} trending wallpapers`, 'success');
        } else {
            showToast('Failed to load trending content', 'error');
            showEmptyState();
        }
    })
    .catch(error => {
        document.getElementById('workshopLoading').style.display = 'none';
        console.error('Error:', error);
        showToast('Failed to load trending content', 'error');
        showEmptyState();
    });
}

function displayWorkshopResults(results) {
    console.log('displayWorkshopResults called with:', results);
    const container = document.getElementById('workshopGrid');
    console.log('Container element:', container);
    
    if (results.length === 0) {
        container.innerHTML = '<div class="empty-state text-center py-4"><div class="alert alert-info">No results found. Try different search terms.</div></div>';
        return;
    }
    
    container.innerHTML = '';
    
    results.forEach(item => {
        console.log('Processing item:', item);
        const workshopItem = document.createElement('div');
        workshopItem.className = 'workshop-item';
        workshopItem.onclick = () => selectWorkshopItem(item.id, item.url);
        
        const cleanTitle = item.title.replace(/[<>&"']/g, function(match) {
            const escape = {
                '<': '&lt;',
                '>': '&gt;',
                '&': '&amp;',
                '"': '&quot;',
                "'": '&#x27;'
            };
            return escape[match];
        });
        
        workshopItem.innerHTML = `
            ${item.preview_url ? 
                `<img src="${item.preview_url}" alt="${cleanTitle}">` : 
                `<div class="workshop-item-placeholder">
                    <i class="fas fa-image fa-2x text-muted"></i>
                </div>`
            }
            <div class="workshop-item-content">
                <div class="workshop-item-title">${cleanTitle}</div>
                <div class="workshop-item-stats">
                    <span>ID: ${item.id}</span>
                    <span>by ${item.author || 'Unknown'}</span>
                </div>
            </div>
        `;
        
        container.appendChild(workshopItem);
    });
}

function selectWorkshopItem(workshopId, workshopUrl) {
    document.getElementById('workshopUrl').value = workshopUrl;
    currentWorkshopId = workshopId;
    
    showToast(`Selected workshop item: ${workshopId}`, 'success');
    
    const workshopInfo = {
        id: workshopId,
        url: workshopUrl,
        title: `Workshop Item ${workshopId}`,
        preview_url: null
    };
    
    showWorkshopPreview(workshopInfo);
    
    document.querySelector('#workshopGrid').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

function downloadFromBrowse(workshopId) {
    currentWorkshopId = workshopId;
    startDownload();
}

function showEmptyState() {
    const container = document.getElementById('workshopGrid');
    container.innerHTML = `
        <div class="empty-state">
            <i class="fab fa-steam"></i>
            <h5>No Results Found</h5>
            <p>Try adjusting your search terms or browse trending content.</p>
        </div>
    `;
}

function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

function initializeDarkMode() {
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
    }
}