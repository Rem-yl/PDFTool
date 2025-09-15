// PDFTool 文件上传相关功能

/**
 * 设置拖放区域
 * @param {string} dropZoneId 拖放区域元素ID
 * @param {string} inputId 文件输入框ID
 */
function setupDropZone(dropZoneId, inputId) {
    const dropZone = document.getElementById(dropZoneId);
    const fileInput = document.getElementById(inputId);
    
    if (!dropZone || !fileInput) {
        console.warn('Drop zone or file input not found:', dropZoneId, inputId);
        return;
    }
    
    // 防止默认拖放行为
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // 高亮拖放区域
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    // 处理文件拖放
    dropZone.addEventListener('drop', handleDrop, false);
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight() {
        dropZone.classList.add('dragover');
    }
    
    function unhighlight() {
        dropZone.classList.remove('dragover');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        // 验证文件
        const validFiles = Array.from(files).filter(file => {
            if (!validateFileType(file)) {
                showNotification(`文件 ${file.name} 不是PDF格式`, 'error');
                return false;
            }
            if (!validateFileSize(file)) {
                showNotification(`文件 ${file.name} 超过大小限制`, 'error');
                return false;
            }
            return true;
        });
        
        if (validFiles.length > 0) {
            // 设置到文件输入框
            const dataTransfer = new DataTransfer();
            validFiles.forEach(file => dataTransfer.items.add(file));
            fileInput.files = dataTransfer.files;
            
            // 显示文件信息
            displayFileInfo(validFiles, dropZoneId);
            
            showNotification(`已选择 ${validFiles.length} 个文件`, 'success');
        }
    }
}

/**
 * 显示文件信息
 * @param {FileList|Array} files 文件列表
 * @param {string} containerId 容器ID
 */
function displayFileInfo(files, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // 移除现有的文件信息
    const existingInfo = container.querySelector('.file-info');
    if (existingInfo) {
        existingInfo.remove();
    }
    
    // 创建文件信息元素
    const fileInfo = document.createElement('div');
    fileInfo.className = 'file-info';
    fileInfo.style.cssText = `
        margin-top: 20px;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    `;
    
    let infoHTML = '<h4 style="margin-bottom: 10px; color: #495057;">已选择的文件:</h4>';
    
    Array.from(files).forEach((file, index) => {
        const size = formatFileSize(file.size);
        infoHTML += `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #dee2e6;">
                <span style="color: #495057; font-weight: 500;">${file.name}</span>
                <span style="color: #6c757d; font-size: 0.9em;">${size}</span>
            </div>
        `;
    });
    
    fileInfo.innerHTML = infoHTML;
    container.appendChild(fileInfo);
}

/**
 * 预览上传文件
 * @param {File} file 文件对象
 * @param {string} previewId 预览容器ID
 */
function previewFile(file, previewId) {
    const preview = document.getElementById(previewId);
    if (!preview) return;
    
    preview.innerHTML = `
        <div class="file-preview" style="padding: 20px; background: #f8f9fa; border-radius: 8px; margin-top: 15px;">
            <h4 style="margin-bottom: 15px; color: #495057;">文件预览</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div>
                    <strong>文件名:</strong><br>
                    <span style="color: #6c757d;">${file.name}</span>
                </div>
                <div>
                    <strong>文件大小:</strong><br>
                    <span style="color: #6c757d;">${formatFileSize(file.size)}</span>
                </div>
                <div>
                    <strong>文件类型:</strong><br>
                    <span style="color: #6c757d;">${file.type || '未知'}</span>
                </div>
                <div>
                    <strong>最后修改:</strong><br>
                    <span style="color: #6c757d;">${new Date(file.lastModified).toLocaleString()}</span>
                </div>
            </div>
        </div>
    `;
}

/**
 * 创建文件上传进度显示
 * @param {string} containerId 容器ID
 * @param {string} fileName 文件名
 * @returns {Object} 进度控制对象
 */
function createUploadProgress(containerId, fileName) {
    const container = document.getElementById(containerId);
    if (!container) return null;
    
    const progressId = `progress-${Date.now()}`;
    const progressHTML = `
        <div id="${progressId}" class="upload-progress" style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-weight: 500; color: #495057;">上传: ${fileName}</span>
                <span id="${progressId}-percent" style="color: #6c757d;">0%</span>
            </div>
            <div style="width: 100%; height: 8px; background: #e9ecef; border-radius: 4px; overflow: hidden;">
                <div id="${progressId}-bar" style="height: 100%; background: linear-gradient(45deg, #667eea, #764ba2); width: 0%; transition: width 0.3s ease;"></div>
            </div>
            <div id="${progressId}-status" style="margin-top: 10px; font-size: 0.9em; color: #6c757d;">准备上传...</div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', progressHTML);
    
    return {
        update(percent, status) {
            const percentElement = document.getElementById(`${progressId}-percent`);
            const barElement = document.getElementById(`${progressId}-bar`);
            const statusElement = document.getElementById(`${progressId}-status`);
            
            if (percentElement) percentElement.textContent = `${percent}%`;
            if (barElement) barElement.style.width = `${percent}%`;
            if (statusElement) statusElement.textContent = status;
        },
        complete(success, message) {
            const statusElement = document.getElementById(`${progressId}-status`);
            const barElement = document.getElementById(`${progressId}-bar`);
            
            if (statusElement) {
                statusElement.textContent = message;
                statusElement.style.color = success ? '#28a745' : '#dc3545';
            }
            
            if (barElement && success) {
                barElement.style.background = '#28a745';
            }
        },
        remove() {
            const element = document.getElementById(progressId);
            if (element) element.remove();
        }
    };
}

/**
 * 批量文件上传
 * @param {FileList} files 文件列表
 * @param {string} uploadUrl 上传URL
 * @param {Object} options 上传选项
 * @returns {Promise} 上传Promise
 */
async function uploadFiles(files, uploadUrl, options = {}) {
    const {
        onProgress = () => {},
        onComplete = () => {},
        onError = () => {},
        additionalData = {}
    } = options;
    
    const formData = new FormData();
    
    // 添加文件
    Array.from(files).forEach((file, index) => {
        formData.append(`files`, file);
    });
    
    // 添加额外数据
    Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
    });
    
    try {
        const xhr = new XMLHttpRequest();
        
        // 上传进度
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                onProgress(percent);
            }
        });
        
        // 上传完成
        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                onComplete(xhr.response);
            } else {
                onError(new Error(`上传失败: ${xhr.status}`));
            }
        });
        
        // 上传错误
        xhr.addEventListener('error', () => {
            onError(new Error('网络错误'));
        });
        
        // 发送请求
        xhr.open('POST', uploadUrl);
        xhr.send(formData);
        
    } catch (error) {
        onError(error);
    }
}

/**
 * 文件大小验证装饰器
 * @param {number} maxSize 最大大小（字节）
 * @returns {Function} 装饰器函数
 */
function withFileSizeValidation(maxSize = 100 * 1024 * 1024) {
    return function(target, propertyKey, descriptor) {
        const originalMethod = descriptor.value;
        
        descriptor.value = function(...args) {
            const fileInput = args[0];
            if (fileInput && fileInput.files) {
                for (const file of fileInput.files) {
                    if (!validateFileSize(file, maxSize)) {
                        showNotification(
                            `文件 ${file.name} 超过大小限制 ${formatFileSize(maxSize)}`,
                            'error'
                        );
                        return;
                    }
                }
            }
            return originalMethod.apply(this, args);
        };
        
        return descriptor;
    };
}

// 自动设置文件输入变化监听
document.addEventListener('DOMContentLoaded', function() {
    // 为所有文件输入添加变化监听
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const files = e.target.files;
            if (files.length > 0) {
                displayFileInfo(files, e.target.closest('.upload-area').id);
            }
        });
    });
});