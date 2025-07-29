// Notion Clone App JavaScript

class NotionApp {
    constructor() {
        this.quill = null;
        this.autosaveTimer = null;
        this.currentPageId = null;
        this.isDirty = false;
        
        this.init();
    }
    
    init() {
        this.initializeEditor();
        this.initializeFileUpload();
        this.initializeAutosave();
        this.initializeEventListeners();
        this.initializeDragAndDrop();
    }
    
    // Initialize Quill.js editor
    initializeEditor() {
        const editorElement = document.getElementById('editor');
        if (!editorElement) return;
        
        // Get page ID from data attribute
        this.currentPageId = editorElement.dataset.pageId;
        
        // Quill configuration
        this.quill = new Quill('#editor', {
            theme: 'snow',
            modules: {
                toolbar: [
                    [{ 'header': [1, 2, 3, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    [{ 'color': [] }, { 'background': [] }],
                    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                    [{ 'align': [] }],
                    ['blockquote', 'code-block'],
                    ['link', 'image'],
                    ['clean']
                ]
            },
            placeholder: 'Start writing...'
        });
        
        // Load existing content
        this.loadPageContent();
        
        // Listen for content changes
        this.quill.on('text-change', () => {
            this.isDirty = true;
            this.scheduleAutosave();
        });
    }
    
    // Load page content from API
    async loadPageContent() {
        if (!this.currentPageId) return;
        
        try {
            const response = await fetch(`/api/page/${this.currentPageId}/content`);
            const data = await response.json();
            
            if (data.success && data.content_blocks.length > 0) {
                // Combine all text content blocks
                const content = data.content_blocks
                    .filter(block => block.block_type === 'text')
                    .map(block => block.content)
                    .join('\n\n');
                
                if (content) {
                    this.quill.root.innerHTML = content;
                }
            }
            
            // Display files
            this.displayFiles(data.files || []);
            
        } catch (error) {
            console.error('Error loading page content:', error);
        }
    }
    
    // Schedule autosave
    scheduleAutosave() {
        if (this.autosaveTimer) {
            clearTimeout(this.autosaveTimer);
        }
        
        this.autosaveTimer = setTimeout(() => {
            this.autosave();
        }, 2000); // Autosave after 2 seconds of inactivity
    }
    
    // Autosave content
    async autosave() {
        if (!this.isDirty || !this.currentPageId) return;
        
        const content = this.quill.root.innerHTML;
        
        try {
            const response = await fetch('/api/content-blocks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    page_id: this.currentPageId,
                    block_type: 'text',
                    content: content,
                    order: 0
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.isDirty = false;
                this.showSaveIndicator('Saved');
            } else {
                this.showSaveIndicator('Error saving', 'error');
            }
            
        } catch (error) {
            console.error('Autosave error:', error);
            this.showSaveIndicator('Error saving', 'error');
        }
    }
    
    // Initialize file upload
    initializeFileUpload() {
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        
        if (!fileInput || !uploadArea) return;
        
        // File input change
        fileInput.addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files[0]);
        });
        
        // Upload area click
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
    }
    
    // Initialize drag and drop
    initializeDragAndDrop() {
        const uploadArea = document.getElementById('uploadArea');
        if (!uploadArea) return;
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        });
    }
    
    // Handle file upload
    async handleFileUpload(file) {
        if (!file || !this.currentPageId) return;
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('page_id', this.currentPageId);
        
        try {
            this.showUploadProgress(true);
            
            const response = await fetch('/api/upload', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addFileToDisplay(data.file);
                this.showSaveIndicator('File uploaded successfully');
            } else {
                this.showSaveIndicator(data.error || 'Upload failed', 'error');
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showSaveIndicator('Upload failed', 'error');
        } finally {
            this.showUploadProgress(false);
        }
    }
    
    // Display files
    displayFiles(files) {
        const filesContainer = document.getElementById('filesContainer');
        if (!filesContainer) return;
        
        filesContainer.innerHTML = '';
        
        files.forEach(file => {
            this.addFileToDisplay(file);
        });
    }
    
    // Add file to display
    addFileToDisplay(file) {
        const filesContainer = document.getElementById('filesContainer');
        if (!filesContainer) return;
        
        const fileElement = document.createElement('div');
        fileElement.className = 'file-preview fade-in';
        fileElement.dataset.fileId = file.id;
        
        let fileContent = '';
        
        if (file.is_image) {
            fileContent = `
                <img src="${file.url}" alt="${file.original_filename}" class="img-fluid">
                <div class="mt-2">
                    <strong>${file.original_filename}</strong>
                    <small class="text-muted d-block">${this.formatFileSize(file.file_size)}</small>
                </div>
            `;
        } else {
            fileContent = `
                <div class="d-flex align-items-center">
                    <i class="bi bi-file-earmark text-primary fs-2 me-3"></i>
                    <div class="flex-grow-1">
                        <strong>${file.original_filename}</strong>
                        <small class="text-muted d-block">${this.formatFileSize(file.file_size)}</small>
                    </div>
                    <a href="${file.url}" class="btn btn-outline-primary btn-sm" download>
                        <i class="bi bi-download"></i>
                    </a>
                </div>
            `;
        }
        
        fileElement.innerHTML = `
            ${fileContent}
            <button class="btn btn-outline-danger btn-sm mt-2" onclick="app.deleteFile(${file.id})">
                <i class="bi bi-trash"></i> Delete
            </button>
        `;
        
        filesContainer.appendChild(fileElement);
    }
    
    // Delete file
    async deleteFile(fileId) {
        if (!confirm('Are you sure you want to delete this file?')) return;
        
        try {
            const response = await fetch(`/api/files/${fileId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                const fileElement = document.querySelector(`[data-file-id="${fileId}"]`);
                if (fileElement) {
                    fileElement.remove();
                }
                this.showSaveIndicator('File deleted');
            } else {
                this.showSaveIndicator('Error deleting file', 'error');
            }
            
        } catch (error) {
            console.error('Delete error:', error);
            this.showSaveIndicator('Error deleting file', 'error');
        }
    }
    
    // Initialize other event listeners
    initializeEventListeners() {
        // Save button
        const saveBtn = document.getElementById('saveBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.autosave();
            });
        }
        
        // Todo checkboxes
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('todo-checkbox')) {
                this.toggleTodo(e.target);
            }
        });
        
        // Search form enhancements
        const searchInput = document.querySelector('input[name="query"]');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => {
                // Could implement live search here
            }, 300));
        }
    }
    
    // Initialize autosave for the page
    initializeAutosave() {
        // Save before leaving page
        window.addEventListener('beforeunload', (e) => {
            if (this.isDirty) {
                this.autosave();
                e.preventDefault();
                e.returnValue = '';
            }
        });
        
        // Periodic save
        setInterval(() => {
            if (this.isDirty) {
                this.autosave();
            }
        }, 30000); // Save every 30 seconds if dirty
    }
    
    // Toggle todo item
    async toggleTodo(checkbox) {
        const todoText = checkbox.nextElementSibling;
        const isCompleted = checkbox.checked;
        
        if (isCompleted) {
            todoText.classList.add('completed');
        } else {
            todoText.classList.remove('completed');
        }
        
        // Save todo state
        this.isDirty = true;
        this.scheduleAutosave();
    }
    
    // Show save indicator
    showSaveIndicator(message, type = 'success') {
        const indicator = document.getElementById('saveIndicator');
        if (!indicator) {
            this.createSaveIndicator();
            return this.showSaveIndicator(message, type);
        }
        
        indicator.textContent = message;
        indicator.className = `save-indicator alert alert-${type === 'error' ? 'danger' : 'success'}`;
        indicator.style.display = 'block';
        
        setTimeout(() => {
            indicator.style.display = 'none';
        }, 3000);
    }
    
    // Create save indicator
    createSaveIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'saveIndicator';
        indicator.className = 'save-indicator alert';
        indicator.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 1051;
            display: none;
            min-width: 200px;
        `;
        document.body.appendChild(indicator);
    }
    
    // Show upload progress
    showUploadProgress(show) {
        const uploadArea = document.getElementById('uploadArea');
        if (!uploadArea) return;
        
        if (show) {
            uploadArea.classList.add('loading');
            uploadArea.innerHTML = `
                <div class="spinner me-2"></div>
                Uploading...
            `;
        } else {
            uploadArea.classList.remove('loading');
            uploadArea.innerHTML = `
                <i class="bi bi-cloud-upload fs-1 text-muted"></i>
                <p class="mt-2 mb-0">Drop files here or click to upload</p>
                <small class="text-muted">Supports images, PDFs, and documents</small>
            `;
        }
    }
    
    // Utility functions
    getCSRFToken() {
        const token = document.querySelector('meta[name=csrf-token]');
        return token ? token.getAttribute('content') : '';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Content Blocks Management
class ContentBlockManager {
    constructor() {
        this.blocks = new Map();
        this.init();
    }
    
    init() {
        this.initializeSortable();
        this.loadBlocks();
    }
    
    initializeSortable() {
        const blocksContainer = document.getElementById('contentBlocks');
        if (!blocksContainer) return;
        
        // Simple drag and drop implementation
        let draggedElement = null;
        
        blocksContainer.addEventListener('dragstart', (e) => {
            if (e.target.classList.contains('content-block')) {
                draggedElement = e.target;
                e.target.style.opacity = '0.5';
            }
        });
        
        blocksContainer.addEventListener('dragend', (e) => {
            if (e.target.classList.contains('content-block')) {
                e.target.style.opacity = '';
                draggedElement = null;
            }
        });
        
        blocksContainer.addEventListener('dragover', (e) => {
            e.preventDefault();
        });
        
        blocksContainer.addEventListener('drop', (e) => {
            e.preventDefault();
            if (draggedElement && e.target.classList.contains('content-block')) {
                const container = e.target.parentNode;
                const afterElement = this.getDragAfterElement(container, e.clientY);
                
                if (afterElement == null) {
                    container.appendChild(draggedElement);
                } else {
                    container.insertBefore(draggedElement, afterElement);
                }
                
                this.updateBlockOrder();
            }
        });
    }
    
    getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.content-block:not(.dragging)')];
        
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }
    
    async loadBlocks() {
        // Implementation for loading content blocks
    }
    
    async updateBlockOrder() {
        const blocks = document.querySelectorAll('.content-block');
        const blockData = Array.from(blocks).map((block, index) => ({
            block_id: block.dataset.blockId,
            order: index
        }));
        
        try {
            const response = await fetch('/api/content-blocks/reorder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': app.getCSRFToken()
                },
                body: JSON.stringify({
                    page_id: app.currentPageId,
                    blocks: blockData
                })
            });
            
            const data = await response.json();
            if (!data.success) {
                console.error('Failed to update block order');
            }
        } catch (error) {
            console.error('Error updating block order:', error);
        }
    }
}

// Search Enhancement
class SearchManager {
    constructor() {
        this.init();
    }
    
    init() {
        this.initializeSearch();
        this.initializeFilters();
    }
    
    initializeSearch() {
        const searchForm = document.querySelector('form[action*="search"]');
        if (!searchForm) return;
        
        const searchInput = searchForm.querySelector('input[name="query"]');
        if (!searchInput) return;
        
        // Add search suggestions/autocomplete here if needed
        searchInput.addEventListener('input', this.debounce((e) => {
            // Could implement live search suggestions
        }, 300));
    }
    
    initializeFilters() {
        // Add filter functionality for search results
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize main app
    window.app = new NotionApp();
    
    // Initialize other managers
    window.blockManager = new ContentBlockManager();
    window.searchManager = new SearchManager();
    
    // Add any additional initialization here
    console.log('Notion Clone App initialized');
});

// Global functions for template usage
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

function showToast(message, type = 'info') {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} toast-notification`;
    toast.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 1052;
        min-width: 300px;
        animation: slideIn 0.3s ease-out;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add CSS for toast animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);