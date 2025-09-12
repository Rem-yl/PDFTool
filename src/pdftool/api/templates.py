"""
HTML templates for the web interface
"""


def get_html_template() -> str:
    """Get the main HTML template for the web interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDFTool - PDF操作工具</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 300;
            }
            
            .header p {
                opacity: 0.9;
                font-size: 1.1em;
            }
            
            .content {
                padding: 40px;
            }
            
            .function-group {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 30px;
                margin-bottom: 30px;
                border: 1px solid #e9ecef;
                transition: all 0.3s ease;
            }
            
            .function-group:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }
            
            .function-group h2 {
                color: #495057;
                margin-bottom: 20px;
                font-size: 1.5em;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            
            .upload-area {
                border: 2px dashed #ced4da;
                border-radius: 10px;
                padding: 30px;
                text-align: center;
                background: white;
                transition: all 0.3s ease;
                margin-bottom: 20px;
            }
            
            .upload-area:hover {
                border-color: #667eea;
                background: #f8f9ff;
            }
            
            .upload-area.dragover {
                border-color: #667eea;
                background: #e3f2fd;
            }
            
            input[type="file"] {
                margin: 15px 0;
                padding: 10px;
                border: 1px solid #ced4da;
                border-radius: 5px;
                font-size: 14px;
            }
            
            input[type="number"] {
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 5px;
                font-size: 14px;
                width: 80px;
            }
            
            label {
                margin: 0 15px 0 5px;
                cursor: pointer;
                font-weight: 500;
            }
            
            button {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                margin: 8px;
                transition: all 0.3s ease;
                box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            button:active {
                transform: translateY(0);
            }
            
            .result {
                margin-top: 20px;
                padding: 15px;
                border-radius: 8px;
                font-weight: 500;
                animation: slideIn 0.3s ease;
            }
            
            .result.success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            
            .result.error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            
            .options-group {
                margin: 20px 0;
                padding: 20px;
                background: white;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
            
            .range-inputs {
                margin-top: 15px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 5px;
                display: none;
            }
            
            .range-inputs.show {
                display: block;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .progress-bar {
                width: 100%;
                height: 4px;
                background: #e9ecef;
                border-radius: 2px;
                overflow: hidden;
                margin: 10px 0;
                display: none;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(45deg, #667eea, #764ba2);
                border-radius: 2px;
                animation: progress 2s ease-in-out infinite;
            }
            
            @keyframes progress {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>PDFTool</h1>
                <p>专业的PDF操作工具 - 合并、拆分、信息提取</p>
            </div>
            
            <div class="content">
                <div class="function-group">
                    <h2>📄 PDF合并</h2>
                    <div class="upload-area" id="mergeDropZone">
                        <p>选择多个PDF文件进行合并</p>
                        <input type="file" id="mergeFiles" multiple accept=".pdf">
                        <br>
                        <button onclick="mergePDFs()">合并PDF</button>
                    </div>
                    <div class="progress-bar" id="mergeProgress">
                        <div class="progress-fill"></div>
                    </div>
                    <div id="mergeResult"></div>
                </div>
                
                <div class="function-group">
                    <h2>✂️ PDF拆分</h2>
                    <div class="upload-area" id="splitDropZone">
                        <p>选择PDF文件进行拆分</p>
                        <input type="file" id="splitFile" accept=".pdf">
                        <div class="options-group">
                            <label>
                                <input type="radio" name="splitMode" value="all" checked> 每页单独拆分
                            </label>
                            <label>
                                <input type="radio" name="splitMode" value="range"> 指定页面范围
                            </label>
                            <div class="range-inputs" id="rangeInputs">
                                起始页: <input type="number" id="startPage" value="1" min="1">
                                结束页: <input type="number" id="endPage" min="1" placeholder="可选">
                            </div>
                        </div>
                        <button onclick="splitPDF()">拆分PDF</button>
                    </div>
                    <div class="progress-bar" id="splitProgress">
                        <div class="progress-fill"></div>
                    </div>
                    <div id="splitResult"></div>
                </div>
                
                <div class="function-group">
                    <h2>ℹ️ PDF信息</h2>
                    <div class="upload-area" id="infoDropZone">
                        <p>获取PDF文件详细信息</p>
                        <input type="file" id="infoFile" accept=".pdf">
                        <br>
                        <button onclick="getPDFInfo()">获取信息</button>
                    </div>
                    <div class="progress-bar" id="infoProgress">
                        <div class="progress-fill"></div>
                    </div>
                    <div id="infoResult"></div>
                </div>
            </div>
        </div>

        <script>
            // Setup drag and drop for all upload areas
            ['mergeDropZone', 'splitDropZone', 'infoDropZone'].forEach(id => {
                const zone = document.getElementById(id);
                
                zone.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    zone.classList.add('dragover');
                });
                
                zone.addEventListener('dragleave', () => {
                    zone.classList.remove('dragover');
                });
                
                zone.addEventListener('drop', (e) => {
                    e.preventDefault();
                    zone.classList.remove('dragover');
                    
                    const files = e.dataTransfer.files;
                    const input = zone.querySelector('input[type="file"]');
                    input.files = files;
                });
            });

            // Toggle range inputs
            document.querySelectorAll('input[name="splitMode"]').forEach(radio => {
                radio.addEventListener('change', function() {
                    const rangeInputs = document.getElementById('rangeInputs');
                    if (this.value === 'range') {
                        rangeInputs.classList.add('show');
                    } else {
                        rangeInputs.classList.remove('show');
                    }
                });
            });

            function showProgress(progressId) {
                document.getElementById(progressId).style.display = 'block';
            }

            function hideProgress(progressId) {
                document.getElementById(progressId).style.display = 'none';
            }

            async function mergePDFs() {
                const files = document.getElementById('mergeFiles').files;
                if (files.length < 2) {
                    showResult('mergeResult', '请选择至少2个PDF文件', false);
                    return;
                }

                const formData = new FormData();
                for (let file of files) {
                    formData.append('files', file);
                }

                showProgress('mergeProgress');
                
                try {
                    const response = await fetch('/merge', {
                        method: 'POST',
                        body: formData
                    });
                    
                    hideProgress('mergeProgress');
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        downloadFile(blob, 'merged.pdf');
                        showResult('mergeResult', `✅ PDF合并成功！已合并 ${files.length} 个文件`, true);
                    } else {
                        const error = await response.json();
                        showResult('mergeResult', `❌ 错误: ${error.detail}`, false);
                    }
                } catch (error) {
                    hideProgress('mergeProgress');
                    showResult('mergeResult', `❌ 请求失败: ${error.message}`, false);
                }
            }

            async function splitPDF() {
                const file = document.getElementById('splitFile').files[0];
                if (!file) {
                    showResult('splitResult', '请选择PDF文件', false);
                    return;
                }

                const formData = new FormData();
                formData.append('file', file);
                
                const mode = document.querySelector('input[name="splitMode"]:checked').value;
                formData.append('mode', mode);
                
                if (mode === 'range') {
                    const startPage = document.getElementById('startPage').value;
                    const endPage = document.getElementById('endPage').value;
                    formData.append('start_page', startPage);
                    if (endPage) formData.append('end_page', endPage);
                }

                showProgress('splitProgress');

                try {
                    const response = await fetch('/split', {
                        method: 'POST',
                        body: formData
                    });
                    
                    hideProgress('splitProgress');
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        const filename = mode === 'all' ? 'split_pages.zip' : 'split_range.pdf';
                        downloadFile(blob, filename);
                        showResult('splitResult', '✅ PDF拆分成功！文件已下载', true);
                    } else {
                        const error = await response.json();
                        showResult('splitResult', `❌ 错误: ${error.detail}`, false);
                    }
                } catch (error) {
                    hideProgress('splitProgress');
                    showResult('splitResult', `❌ 请求失败: ${error.message}`, false);
                }
            }

            async function getPDFInfo() {
                const file = document.getElementById('infoFile').files[0];
                if (!file) {
                    showResult('infoResult', '请选择PDF文件', false);
                    return;
                }

                const formData = new FormData();
                formData.append('file', file);

                showProgress('infoProgress');

                try {
                    const response = await fetch('/info', {
                        method: 'POST',
                        body: formData
                    });
                    
                    hideProgress('infoProgress');
                    
                    if (response.ok) {
                        const info = await response.json();
                        const sizeInMB = (info.file_size / 1024 / 1024).toFixed(2);
                        showResult('infoResult', `
                            <strong>📋 PDF信息:</strong><br>
                            📄 页数: ${info.pages}<br>
                            📝 标题: ${info.title || '无'}<br>
                            👤 作者: ${info.author || '无'}<br>
                            📅 创建时间: ${info.creation_date || '无'}<br>
                            💾 文件大小: ${sizeInMB} MB
                        `, true);
                    } else {
                        const error = await response.json();
                        showResult('infoResult', `❌ 错误: ${error.detail}`, false);
                    }
                } catch (error) {
                    hideProgress('infoProgress');
                    showResult('infoResult', `❌ 请求失败: ${error.message}`, false);
                }
            }

            function showResult(elementId, message, isSuccess) {
                const element = document.getElementById(elementId);
                element.innerHTML = message;
                element.className = isSuccess ? 'result success' : 'result error';
            }

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
        </script>
    </body>
    </html>
    """