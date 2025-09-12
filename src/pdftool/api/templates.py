"""
HTML templates for the web interface
"""


def get_main_menu_template() -> str:
    """Get the main menu template for function selection"""
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
            
            .function-selection {
                text-align: center;
                padding: 20px;
            }
            
            .function-selection h2 {
                color: #495057;
                margin-bottom: 10px;
                font-size: 2.2em;
                font-weight: 300;
            }
            
            .subtitle {
                color: #6c757d;
                font-size: 1.1em;
                margin-bottom: 40px;
            }
            
            .function-cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 30px;
                margin-top: 30px;
            }
            
            .function-card {
                background: white;
                border-radius: 15px;
                padding: 40px 30px;
                border: 2px solid #e9ecef;
                transition: all 0.3s ease;
                cursor: pointer;
                text-align: center;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .function-card:hover {
                transform: translateY(-8px);
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
                border-color: #667eea;
            }
            
            .card-icon {
                font-size: 3.5em;
                margin-bottom: 20px;
                display: block;
            }
            
            .card-title {
                font-size: 1.5em;
                font-weight: 600;
                color: #495057;
                margin-bottom: 15px;
            }
            
            .card-description {
                color: #6c757d;
                line-height: 1.5;
                margin-bottom: 25px;
                font-size: 0.95em;
            }
            
            .card-button {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                padding: 12px 25px;
                border-radius: 25px;
                font-weight: 500;
                display: inline-block;
                transition: all 0.3s ease;
            }
            
            .function-card:hover .card-button {
                transform: scale(1.05);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
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
                <div class="function-selection">
                    <h2>🎯 选择PDF操作功能</h2>
                    <p class="subtitle">请选择您要使用的PDF处理功能</p>
                    
                    <div class="function-cards">
                        <div class="function-card" onclick="goToFunction('merge')">
                            <div class="card-icon">📄</div>
                            <div class="card-title">PDF合并</div>
                            <div class="card-description">将多个PDF文件合并为一个文件</div>
                            <div class="card-button">开始合并</div>
                        </div>
                        
                        <div class="function-card" onclick="goToFunction('split')">
                            <div class="card-icon">✂️</div>
                            <div class="card-title">PDF拆分</div>
                            <div class="card-description">将PDF文件拆分成多个页面或指定范围</div>
                            <div class="card-button">开始拆分</div>
                        </div>
                        
                        <div class="function-card" onclick="goToFunction('info')">
                            <div class="card-icon">ℹ️</div>
                            <div class="card-title">PDF信息</div>
                            <div class="card-description">查看PDF文件的详细信息和属性</div>
                            <div class="card-button">查看信息</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function goToFunction(functionName) {
                window.location.href = `/${functionName}`;
            }
        </script>
    </body>
    </html>
    """


def get_merge_template() -> str:
    """Get the PDF merge page template"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF合并 - PDFTool</title>
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
                max-width: 800px;
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
                position: relative;
            }
            
            .back-button {
                position: absolute;
                left: 30px;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(255,255,255,0.2);
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s ease;
            }
            
            .back-button:hover {
                background: rgba(255,255,255,0.3);
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 300;
            }
            
            .content {
                padding: 40px;
            }
            
            .upload-area {
                border: 2px dashed #ced4da;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                background: #f8f9fa;
                transition: all 0.3s ease;
                margin-bottom: 20px;
            }
            
            .upload-area:hover, .upload-area.dragover {
                border-color: #667eea;
                background: #e3f2fd;
            }
            
            input[type="file"] {
                margin: 20px 0;
                padding: 12px;
                border: 1px solid #ced4da;
                border-radius: 5px;
                font-size: 16px;
                width: 100%;
                max-width: 400px;
            }
            
            button {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 500;
                margin: 10px;
                transition: all 0.3s ease;
                box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            .result {
                margin-top: 20px;
                padding: 15px;
                border-radius: 8px;
                font-weight: 500;
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
            
            .progress-bar {
                width: 100%;
                height: 4px;
                background: #e9ecef;
                border-radius: 2px;
                overflow: hidden;
                margin: 20px 0;
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
                <button class="back-button" onclick="goHome()">← 返回</button>
                <h1>📄 PDF合并</h1>
                <p>将多个PDF文件合并为一个文件</p>
            </div>
            
            <div class="content">
                <div class="upload-area" id="mergeDropZone">
                    <h3>选择要合并的PDF文件</h3>
                    <p>请选择至少2个PDF文件进行合并</p>
                    <input type="file" id="mergeFiles" multiple accept=".pdf">
                    <br>
                    <button onclick="mergePDFs()">开始合并</button>
                </div>
                <div class="progress-bar" id="mergeProgress">
                    <div class="progress-fill"></div>
                </div>
                <div id="mergeResult"></div>
            </div>
        </div>

        <script>
            const zone = document.getElementById('mergeDropZone');
            
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
                const input = document.getElementById('mergeFiles');
                input.files = files;
            });

            function goHome() {
                window.location.href = '/';
            }

            function showProgress() {
                document.getElementById('mergeProgress').style.display = 'block';
            }

            function hideProgress() {
                document.getElementById('mergeProgress').style.display = 'none';
            }

            async function mergePDFs() {
                const files = document.getElementById('mergeFiles').files;
                if (files.length < 2) {
                    showResult('请选择至少2个PDF文件', false);
                    return;
                }

                const formData = new FormData();
                for (let file of files) {
                    formData.append('files', file);
                }

                showProgress();
                
                try {
                    const response = await fetch('/merge', {
                        method: 'POST',
                        body: formData
                    });
                    
                    hideProgress();
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        downloadFile(blob, 'merged.pdf');
                        showResult(`✅ PDF合并成功！已合并 ${files.length} 个文件`, true);
                    } else {
                        const error = await response.json();
                        showResult(`❌ 错误: ${error.detail}`, false);
                    }
                } catch (error) {
                    hideProgress();
                    showResult(`❌ 请求失败: ${error.message}`, false);
                }
            }

            function showResult(message, isSuccess) {
                const element = document.getElementById('mergeResult');
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


def get_split_template() -> str:
    """Get the PDF split page template"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF拆分 - PDFTool</title>
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
                max-width: 800px;
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
                position: relative;
            }
            
            .back-button {
                position: absolute;
                left: 30px;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(255,255,255,0.2);
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s ease;
            }
            
            .back-button:hover {
                background: rgba(255,255,255,0.3);
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 300;
            }
            
            .content {
                padding: 40px;
            }
            
            .upload-area {
                border: 2px dashed #ced4da;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                background: #f8f9fa;
                transition: all 0.3s ease;
                margin-bottom: 20px;
            }
            
            .upload-area:hover, .upload-area.dragover {
                border-color: #667eea;
                background: #e3f2fd;
            }
            
            input[type="file"] {
                margin: 20px 0;
                padding: 12px;
                border: 1px solid #ced4da;
                border-radius: 5px;
                font-size: 16px;
                width: 100%;
                max-width: 400px;
            }
            
            input[type="number"] {
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 5px;
                font-size: 14px;
                width: 80px;
                margin: 0 5px;
            }
            
            label {
                margin: 10px 15px;
                cursor: pointer;
                font-weight: 500;
                display: inline-block;
            }
            
            button {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 500;
                margin: 10px;
                transition: all 0.3s ease;
                box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            .options-group {
                margin: 20px 0;
                padding: 20px;
                background: white;
                border-radius: 8px;
                border: 1px solid #e9ecef;
                text-align: left;
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
            
            .result {
                margin-top: 20px;
                padding: 15px;
                border-radius: 8px;
                font-weight: 500;
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
            
            .progress-bar {
                width: 100%;
                height: 4px;
                background: #e9ecef;
                border-radius: 2px;
                overflow: hidden;
                margin: 20px 0;
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
                <button class="back-button" onclick="goHome()">← 返回</button>
                <h1>✂️ PDF拆分</h1>
                <p>将PDF文件拆分成多个页面或指定范围</p>
            </div>
            
            <div class="content">
                <div class="upload-area" id="splitDropZone">
                    <h3>选择要拆分的PDF文件</h3>
                    <input type="file" id="splitFile" accept=".pdf">
                    
                    <div class="options-group">
                        <h4>拆分选项：</h4>
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
                    <button onclick="splitPDF()">开始拆分</button>
                </div>
                <div class="progress-bar" id="splitProgress">
                    <div class="progress-fill"></div>
                </div>
                <div id="splitResult"></div>
            </div>
        </div>

        <script>
            const zone = document.getElementById('splitDropZone');
            
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
                const input = document.getElementById('splitFile');
                input.files = files;
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

            function goHome() {
                window.location.href = '/';
            }

            function showProgress() {
                document.getElementById('splitProgress').style.display = 'block';
            }

            function hideProgress() {
                document.getElementById('splitProgress').style.display = 'none';
            }

            async function splitPDF() {
                const file = document.getElementById('splitFile').files[0];
                if (!file) {
                    showResult('请选择PDF文件', false);
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

                showProgress();

                try {
                    const response = await fetch('/split', {
                        method: 'POST',
                        body: formData
                    });
                    
                    hideProgress();
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        const filename = mode === 'all' ? 'split_pages.zip' : 'split_range.pdf';
                        downloadFile(blob, filename);
                        showResult('✅ PDF拆分成功！文件已下载', true);
                    } else {
                        const error = await response.json();
                        showResult(`❌ 错误: ${error.detail}`, false);
                    }
                } catch (error) {
                    hideProgress();
                    showResult(`❌ 请求失败: ${error.message}`, false);
                }
            }

            function showResult(message, isSuccess) {
                const element = document.getElementById('splitResult');
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


def get_info_template() -> str:
    """Get the PDF info page template"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF信息 - PDFTool</title>
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
                max-width: 800px;
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
                position: relative;
            }
            
            .back-button {
                position: absolute;
                left: 30px;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(255,255,255,0.2);
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s ease;
            }
            
            .back-button:hover {
                background: rgba(255,255,255,0.3);
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 300;
            }
            
            .content {
                padding: 40px;
            }
            
            .upload-area {
                border: 2px dashed #ced4da;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                background: #f8f9fa;
                transition: all 0.3s ease;
                margin-bottom: 20px;
            }
            
            .upload-area:hover, .upload-area.dragover {
                border-color: #667eea;
                background: #e3f2fd;
            }
            
            input[type="file"] {
                margin: 20px 0;
                padding: 12px;
                border: 1px solid #ced4da;
                border-radius: 5px;
                font-size: 16px;
                width: 100%;
                max-width: 400px;
            }
            
            button {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 500;
                margin: 10px;
                transition: all 0.3s ease;
                box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            .result {
                margin-top: 20px;
                padding: 20px;
                border-radius: 8px;
                font-weight: 500;
                text-align: left;
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
            
            .progress-bar {
                width: 100%;
                height: 4px;
                background: #e9ecef;
                border-radius: 2px;
                overflow: hidden;
                margin: 20px 0;
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
                <button class="back-button" onclick="goHome()">← 返回</button>
                <h1>ℹ️ PDF信息</h1>
                <p>查看PDF文件的详细信息和属性</p>
            </div>
            
            <div class="content">
                <div class="upload-area" id="infoDropZone">
                    <h3>选择要查看信息的PDF文件</h3>
                    <input type="file" id="infoFile" accept=".pdf">
                    <br>
                    <button onclick="getPDFInfo()">获取文件信息</button>
                </div>
                <div class="progress-bar" id="infoProgress">
                    <div class="progress-fill"></div>
                </div>
                <div id="infoResult"></div>
            </div>
        </div>

        <script>
            const zone = document.getElementById('infoDropZone');
            
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
                const input = document.getElementById('infoFile');
                input.files = files;
            });

            function goHome() {
                window.location.href = '/';
            }

            function showProgress() {
                document.getElementById('infoProgress').style.display = 'block';
            }

            function hideProgress() {
                document.getElementById('infoProgress').style.display = 'none';
            }

            async function getPDFInfo() {
                const file = document.getElementById('infoFile').files[0];
                if (!file) {
                    showResult('请选择PDF文件', false);
                    return;
                }

                const formData = new FormData();
                formData.append('file', file);

                showProgress();

                try {
                    const response = await fetch('/info', {
                        method: 'POST',
                        body: formData
                    });
                    
                    hideProgress();
                    
                    if (response.ok) {
                        const info = await response.json();
                        const sizeInMB = (info.file_size / 1024 / 1024).toFixed(2);
                        showResult(`
                            <strong>📋 PDF文件信息:</strong><br><br>
                            📄 <strong>页数:</strong> ${info.pages}<br>
                            📝 <strong>标题:</strong> ${info.title || '无'}<br>
                            👤 <strong>作者:</strong> ${info.author || '无'}<br>
                            📅 <strong>创建时间:</strong> ${info.creation_date || '无'}<br>
                            💾 <strong>文件大小:</strong> ${sizeInMB} MB
                        `, true);
                    } else {
                        const error = await response.json();
                        showResult(`❌ 错误: ${error.detail}`, false);
                    }
                } catch (error) {
                    hideProgress();
                    showResult(`❌ 请求失败: ${error.message}`, false);
                }
            }

            function showResult(message, isSuccess) {
                const element = document.getElementById('infoResult');
                element.innerHTML = message;
                element.className = isSuccess ? 'result success' : 'result error';
            }
        </script>
    </body>
    </html>
    """