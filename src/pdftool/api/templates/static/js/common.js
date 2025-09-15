// PDFTool 通用JavaScript函数

/**
 * 返回首页
 */
function goHome() {
    window.location.href = '/';
}

/**
 * 显示进度条
 * @param {string} progressId 进度条元素ID
 */
function showProgress(progressId) {
    const element = document.getElementById(progressId);
    if (element) {
        element.style.display = 'block';
    }
}

/**
 * 隐藏进度条
 * @param {string} progressId 进度条元素ID
 */
function hideProgress(progressId) {
    const element = document.getElementById(progressId);
    if (element) {
        element.style.display = 'none';
    }
}

/**
 * 显示结果信息
 * @param {string} elementId 结果显示元素ID
 * @param {string} message 消息内容
 * @param {boolean} isSuccess 是否成功
 */
function showResult(elementId, message, isSuccess) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = message;
        element.className = isSuccess ? 'result success' : 'result error';
    }
}

/**
 * 下载文件
 * @param {Blob} blob 文件Blob对象
 * @param {string} filename 文件名
 */
function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

/**
 * 格式化文件大小
 * @param {number} bytes 字节数
 * @returns {string} 格式化后的大小
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 验证文件类型
 * @param {File} file 文件对象
 * @param {Array} allowedTypes 允许的文件类型
 * @returns {boolean} 是否有效
 */
function validateFileType(file, allowedTypes = ['.pdf']) {
    const fileName = file.name.toLowerCase();
    return allowedTypes.some(type => fileName.endsWith(type));
}

/**
 * 验证文件大小
 * @param {File} file 文件对象
 * @param {number} maxSize 最大大小（字节）
 * @returns {boolean} 是否有效
 */
function validateFileSize(file, maxSize = 100 * 1024 * 1024) { // 100MB
    return file.size <= maxSize;
}

/**
 * 显示通知消息
 * @param {string} message 消息内容
 * @param {string} type 消息类型 (success, error, warning, info)
 * @param {number} duration 显示时长（毫秒）
 */
function showNotification(message, type = 'info', duration = 5000) {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    // 添加样式
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 1000;
        max-width: 400px;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: slideInRight 0.3s ease;
    `;
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 自动删除
    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);
    }
}

/**
 * 获取通知颜色
 * @param {string} type 通知类型
 * @returns {string} 颜色值
 */
function getNotificationColor(type) {
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    return colors[type] || colors.info;
}

/**
 * 防抖函数
 * @param {Function} func 要防抖的函数
 * @param {number} wait 等待时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
function debounce(func, wait) {
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

/**
 * 节流函数
 * @param {Function} func 要节流的函数
 * @param {number} limit 时间限制（毫秒）
 * @returns {Function} 节流后的函数
 */
function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * 深拷贝对象
 * @param {any} obj 要拷贝的对象
 * @returns {any} 拷贝后的对象
 */
function deepClone(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime());
    if (obj instanceof Array) return obj.map(item => deepClone(item));
    if (typeof obj === 'object') {
        const clonedObj = {};
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                clonedObj[key] = deepClone(obj[key]);
            }
        }
        return clonedObj;
    }
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        font-size: 18px;
        cursor: pointer;
        padding: 0;
        margin: 0;
        min-width: auto;
        box-shadow: none;
    }
    
    .notification-close:hover {
        opacity: 0.8;
        transform: none;
    }
`;
document.head.appendChild(style);