// PDFTool 现代化JavaScript模块

/**
 * 全局应用状态管理
 */
class PDFToolApp {
    constructor() {
        this.theme = localStorage.getItem('pdftool-theme') || 'light';
        this.init();
    }

    init() {
        this.setupTheme();
        this.setupAnimations();
        this.setupErrorHandling();
        this.setupKeyboardShortcuts();
        console.log('PDFTool 应用已初始化');
    }

    setupTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        this.updateThemeIcon();
    }

    setupAnimations() {
        // 设置Intersection Observer for entrance animations
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-in');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            // 观察所有需要动画的元素
            document.querySelectorAll('.feature-card, .category-section').forEach(el => {
                observer.observe(el);
            });
        }
    }

    setupErrorHandling() {
        window.addEventListener('error', (event) => {
            console.error('JavaScript错误:', event.error);
            this.showNotification('应用遇到错误，请刷新页面重试', 'error');
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('未处理的Promise错误:', event.reason);
            this.showNotification('网络请求失败，请检查网络连接', 'error');
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // ESC键返回首页
            if (e.key === 'Escape' && window.location.pathname !== '/') {
                this.goHome();
            }
            // Ctrl/Cmd + K 快速搜索功能（未来实现）
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                // TODO: 实现快速搜索功能
            }
        });
    }

    goHome() {
        this.showLoadingOverlay();
        window.location.href = '/';
    }

    showLoadingOverlay(message = '正在加载...') {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.querySelector('.loading-text').textContent = message;
            overlay.style.display = 'flex';
        }
    }

    hideLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    updateThemeIcon() {
        const themeIcon = document.querySelector('.theme-icon');
        if (themeIcon) {
            themeIcon.textContent = this.theme === 'light' ? '🌙' : '☀️';
        }
    }

    showNotification(message, type = 'info', duration = 5000) {
        // 移除现有通知
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(n => n.remove());

        // 创建新通知
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${this.getNotificationIcon(type)}</span>
                <span class="notification-message">${message}</span>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()" aria-label="关闭通知">×</button>
        `;

        // 设置样式
        this.setNotificationStyles(notification, type);

        // 添加到页面
        document.body.appendChild(notification);

        // 入场动画
        requestAnimationFrame(() => {
            notification.classList.add('notification-show');
        });

        // 自动删除
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.classList.add('notification-hide');
                    setTimeout(() => notification.remove(), 300);
                }
            }, duration);
        }
    }

    getNotificationIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    setNotificationStyles(notification, type) {
        const colors = {
            success: 'var(--success-color)',
            error: 'var(--error-color)',
            warning: 'var(--warning-color)',
            info: 'var(--info-color)'
        };

        notification.style.cssText = `
            position: fixed;
            top: var(--spacing-5);
            right: var(--spacing-5);
            background: ${colors[type] || colors.info};
            color: white;
            padding: var(--spacing-4) var(--spacing-5);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-xl);
            z-index: 1000;
            max-width: 400px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: var(--spacing-3);
            transform: translateX(100%);
            transition: transform var(--transition-base);
            font-weight: 500;
            backdrop-filter: blur(10px);
        `;
    }
}

// 全局实例
const app = new PDFToolApp();

/**
 * 返回首页
 */
function goHome() {
    app.goHome();
}

/**
 * 切换主题
 */
function toggleTheme() {
    app.theme = app.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('pdftool-theme', app.theme);
    app.setupTheme();
    app.showNotification(`已切换到${app.theme === 'light' ? '浅色' : '深色'}主题`, 'success', 2000);
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
 * 显示通知消息 (兼容旧API)
 * @param {string} message 消息内容
 * @param {string} type 消息类型 (success, error, warning, info)
 * @param {number} duration 显示时长（毫秒）
 */
function showNotification(message, type = 'info', duration = 5000) {
    app.showNotification(message, type, duration);
}

/**
 * 文件上传处理器
 */
class FileUploadHandler {
    constructor(options = {}) {
        this.maxSize = options.maxSize || 100 * 1024 * 1024; // 100MB
        this.allowedTypes = options.allowedTypes || ['.pdf'];
        this.onProgress = options.onProgress || (() => {});
        this.onSuccess = options.onSuccess || (() => {});
        this.onError = options.onError || (() => {});
    }

    validateFile(file) {
        // 检查文件类型
        if (!this.validateFileType(file, this.allowedTypes)) {
            throw new Error(`不支持的文件类型。请选择 ${this.allowedTypes.join(', ')} 格式的文件。`);
        }

        // 检查文件大小
        if (!this.validateFileSize(file, this.maxSize)) {
            throw new Error(`文件太大。最大允许 ${this.formatFileSize(this.maxSize)}。`);
        }

        return true;
    }

    validateFileType(file, allowedTypes = ['.pdf']) {
        const fileName = file.name.toLowerCase();
        return allowedTypes.some(type => fileName.endsWith(type));
    }

    validateFileSize(file, maxSize = 100 * 1024 * 1024) {
        return file.size <= maxSize;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async uploadFile(file, url, options = {}) {
        try {
            // 验证文件
            this.validateFile(file);

            // 创建FormData
            const formData = new FormData();
            formData.append('file', file);

            // 添加额外字段
            Object.keys(options.data || {}).forEach(key => {
                formData.append(key, options.data[key]);
            });

            // 创建XMLHttpRequest用于进度监控
            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();

                // 上传进度
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const progress = Math.round((e.loaded * 100) / e.total);
                        this.onProgress(progress);
                    }
                });

                // 完成处理
                xhr.addEventListener('load', () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        try {
                            const response = JSON.parse(xhr.responseText);
                            this.onSuccess(response);
                            resolve(response);
                        } catch (e) {
                            this.onError(new Error('服务器返回无效响应'));
                            reject(new Error('服务器返回无效响应'));
                        }
                    } else {
                        const error = new Error(`上传失败: ${xhr.statusText}`);
                        this.onError(error);
                        reject(error);
                    }
                });

                // 错误处理
                xhr.addEventListener('error', () => {
                    const error = new Error('网络错误，请检查网络连接');
                    this.onError(error);
                    reject(error);
                });

                // 超时处理
                xhr.addEventListener('timeout', () => {
                    const error = new Error('上传超时，请重试');
                    this.onError(error);
                    reject(error);
                });

                // 发送请求
                xhr.open('POST', url);
                xhr.timeout = options.timeout || 300000; // 5分钟超时
                xhr.send(formData);
            });

        } catch (error) {
            this.onError(error);
            throw error;
        }
    }
}

/**
 * 拖拽上传处理
 */
function setupDragDrop(dropZone, onFilesDropped) {
    if (!dropZone) return;

    const events = ['dragenter', 'dragover', 'dragleave', 'drop'];

    events.forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.classList.add('dragover');
    }

    function unhighlight() {
        dropZone.classList.remove('dragover');
    }

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = Array.from(dt.files);

        if (onFilesDropped) {
            onFilesDropped(files);
        }
    }
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