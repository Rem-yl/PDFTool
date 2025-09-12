"""
Modern GUI application for PDFTool
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import List, Optional

from ..core.pdf_operations import PDFOperations
from ..core.models import SplitOptions, MergeOptions, SplitMode
from ..core.exceptions import PDFToolError
from ..config.settings import settings
from ..utils.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger("gui")


class ModernPDFTool:
    """Modern GUI for PDF operations with improved UX"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.pdf_ops = PDFOperations(temp_dir=settings.temp_dir)
        self.setup_main_window()
        self.setup_styles()
        self.create_widgets()
        
    def setup_main_window(self):
        """Configure main window"""
        self.root.title(f"{settings.app_name} - PDF操作工具 v{settings.version}")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")
        
    def setup_styles(self):
        """Configure modern styles"""
        style = ttk.Style()
        
        # Configure colors and styles
        style.configure('Title.TLabel', font=('Helvetica', 18, 'bold'))
        style.configure('Subtitle.TLabel', font=('Helvetica', 12))
        style.configure('Section.TLabel', font=('Helvetica', 14, 'bold'))
        
    def create_widgets(self):
        """Create and layout widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        self.create_header(main_frame)
        
        # Notebook for tabs
        self.create_notebook(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_header(self, parent):
        """Create application header"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(
            header_frame, 
            text=settings.app_name,
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0)
        
        subtitle_label = ttk.Label(
            header_frame,
            text="专业的PDF操作工具 - 合并、拆分、信息提取",
            style='Subtitle.TLabel'
        )
        subtitle_label.grid(row=1, column=0, pady=(5, 0))
        
    def create_notebook(self, parent):
        """Create tabbed interface"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.create_merge_tab()
        self.create_split_tab()
        self.create_info_tab()
        
    def create_merge_tab(self):
        """Create PDF merge tab"""
        merge_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(merge_frame, text="PDF合并")
        
        # Configure grid
        merge_frame.columnconfigure(0, weight=1)
        merge_frame.rowconfigure(1, weight=1)
        
        # Title
        ttk.Label(merge_frame, text="PDF文件合并", style='Section.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 15)
        )
        
        # File list with frame
        list_frame = ttk.LabelFrame(merge_frame, text="选择要合并的PDF文件", padding="10")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Listbox with scrollbar
        self.merge_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        self.merge_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        merge_scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        merge_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.merge_listbox.config(yscrollcommand=merge_scrollbar.set)
        merge_scrollbar.config(command=self.merge_listbox.yview)
        
        # Buttons frame
        merge_buttons = ttk.Frame(merge_frame)
        merge_buttons.grid(row=2, column=0, pady=10)
        
        ttk.Button(merge_buttons, text="添加PDF文件", command=self.add_merge_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(merge_buttons, text="移除选中", command=self.remove_merge_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(merge_buttons, text="清空列表", command=self.clear_merge_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(merge_buttons, text="合并PDF", command=self.merge_pdfs, style='Accent.TButton').pack(side=tk.LEFT, padx=15)
        
        # Store file paths
        self.merge_files: List[Path] = []
        
    def create_split_tab(self):
        """Create PDF split tab"""
        split_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(split_frame, text="PDF拆分")
        
        split_frame.columnconfigure(0, weight=1)
        
        # Title
        ttk.Label(split_frame, text="PDF文件拆分", style='Section.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 15)
        )
        
        # File selection
        file_frame = ttk.LabelFrame(split_frame, text="选择要拆分的PDF文件", padding="10")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(0, weight=1)
        
        self.split_file_var = tk.StringVar()
        self.split_file_entry = ttk.Entry(file_frame, textvariable=self.split_file_var, state="readonly")
        self.split_file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="浏览", command=self.select_split_file).grid(row=0, column=1)
        
        # Split options
        options_frame = ttk.LabelFrame(split_frame, text="拆分选项", padding="10")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.split_mode = tk.StringVar(value="all")
        ttk.Radiobutton(options_frame, text="每页单独拆分", variable=self.split_mode, value="all").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        ttk.Radiobutton(options_frame, text="指定页面范围", variable=self.split_mode, value="range").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        
        # Range options
        range_frame = ttk.Frame(options_frame)
        range_frame.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(range_frame, text="起始页:").grid(row=0, column=0)
        self.start_page_var = tk.StringVar(value="1")
        ttk.Entry(range_frame, textvariable=self.start_page_var, width=8).grid(row=0, column=1, padx=(5, 15))
        
        ttk.Label(range_frame, text="结束页:").grid(row=0, column=2)
        self.end_page_var = tk.StringVar()
        ttk.Entry(range_frame, textvariable=self.end_page_var, width=8).grid(row=0, column=3, padx=5)
        
        # Split button
        ttk.Button(split_frame, text="拆分PDF", command=self.split_pdf, style='Accent.TButton').grid(
            row=3, column=0, pady=20
        )
        
    def create_info_tab(self):
        """Create PDF info tab"""
        info_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(info_frame, text="PDF信息")
        
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(2, weight=1)
        
        # Title
        ttk.Label(info_frame, text="PDF文件信息", style='Section.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 15)
        )
        
        # File selection
        file_frame = ttk.LabelFrame(info_frame, text="选择PDF文件", padding="10")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(0, weight=1)
        
        self.info_file_var = tk.StringVar()
        self.info_file_entry = ttk.Entry(file_frame, textvariable=self.info_file_var, state="readonly")
        self.info_file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="浏览", command=self.select_info_file).grid(row=0, column=1)
        ttk.Button(file_frame, text="获取信息", command=self.get_pdf_info, style='Accent.TButton').grid(row=0, column=2, padx=(5, 0))
        
        # Info display
        info_display_frame = ttk.LabelFrame(info_frame, text="文件信息", padding="10")
        info_display_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        info_display_frame.columnconfigure(0, weight=1)
        info_display_frame.rowconfigure(0, weight=1)
        
        self.info_text = tk.Text(info_display_frame, wrap=tk.WORD, state=tk.DISABLED, font=('Consolas', 10))
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        info_scrollbar = ttk.Scrollbar(info_display_frame, orient="vertical")
        info_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.info_text.config(yscrollcommand=info_scrollbar.set)
        info_scrollbar.config(command=self.info_text.yview)
        
    def create_status_bar(self, parent):
        """Create status bar"""
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    # Merge operations
    def add_merge_files(self):
        """Add files to merge list"""
        files = filedialog.askopenfilenames(
            title="选择PDF文件",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        for file_path in files:
            path = Path(file_path)
            if path not in self.merge_files:
                self.merge_files.append(path)
                self.merge_listbox.insert(tk.END, path.name)
                
    def remove_merge_files(self):
        """Remove selected files from merge list"""
        selection = self.merge_listbox.curselection()
        for index in reversed(selection):
            self.merge_listbox.delete(index)
            del self.merge_files[index]
            
    def clear_merge_files(self):
        """Clear all files from merge list"""
        self.merge_listbox.delete(0, tk.END)
        self.merge_files.clear()
        
    def merge_pdfs(self):
        """Merge selected PDF files"""
        if len(self.merge_files) < 2:
            messagebox.showwarning("警告", "请选择至少2个PDF文件进行合并")
            return
            
        output_file = filedialog.asksaveasfilename(
            title="保存合并后的PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not output_file:
            return
            
        try:
            self.update_status("正在合并PDF文件...")
            options = MergeOptions(output_file=Path(output_file))
            result = self.pdf_ops.merge_pdfs(self.merge_files, options)
            
            if result.success:
                self.update_status("PDF合并完成")
                messagebox.showinfo("成功", f"PDF文件已成功合并到: {output_file}")
                logger.info(f"Successfully merged {len(self.merge_files)} PDFs")
            else:
                messagebox.showerror("错误", result.message)
                
        except PDFToolError as e:
            self.update_status("PDF合并失败")
            messagebox.showerror("错误", str(e))
            logger.error(f"Merge failed: {str(e)}")
        except Exception as e:
            self.update_status("PDF合并失败")
            messagebox.showerror("错误", f"合并PDF时出错: {str(e)}")
            logger.error(f"Merge failed: {str(e)}")
            
    # Split operations
    def select_split_file(self):
        """Select file for splitting"""
        file_path = filedialog.askopenfilename(
            title="选择要拆分的PDF文件",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.split_file_var.set(file_path)
            
    def split_pdf(self):
        """Split selected PDF file"""
        input_file = self.split_file_var.get()
        if not input_file:
            messagebox.showwarning("警告", "请先选择要拆分的PDF文件")
            return
            
        output_dir = filedialog.askdirectory(title="选择输出目录")
        if not output_dir:
            return
            
        try:
            self.update_status("正在拆分PDF文件...")
            
            # Setup split options
            mode = SplitMode.ALL_PAGES if self.split_mode.get() == "all" else SplitMode.PAGE_RANGE
            start_page = int(self.start_page_var.get()) if self.start_page_var.get() else None
            end_page = int(self.end_page_var.get()) if self.end_page_var.get() else None
            
            options = SplitOptions(
                mode=mode,
                start_page=start_page,
                end_page=end_page,
                output_dir=Path(output_dir),
                filename_prefix=Path(input_file).stem
            )
            
            result = self.pdf_ops.split_pdf(Path(input_file), options)
            
            if result.success:
                self.update_status("PDF拆分完成")
                messagebox.showinfo("成功", f"PDF已成功拆分为 {len(result.output_files)} 个文件")
                logger.info(f"Successfully split PDF into {len(result.output_files)} files")
            else:
                messagebox.showerror("错误", result.message)
                
        except ValueError:
            messagebox.showerror("错误", "请输入有效的页面数字")
        except PDFToolError as e:
            self.update_status("PDF拆分失败")
            messagebox.showerror("错误", str(e))
            logger.error(f"Split failed: {str(e)}")
        except Exception as e:
            self.update_status("PDF拆分失败")
            messagebox.showerror("错误", f"拆分PDF时出错: {str(e)}")
            logger.error(f"Split failed: {str(e)}")
            
    # Info operations
    def select_info_file(self):
        """Select file for info extraction"""
        file_path = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.info_file_var.set(file_path)
            
    def get_pdf_info(self):
        """Get PDF file information"""
        input_file = self.info_file_var.get()
        if not input_file:
            messagebox.showwarning("警告", "请先选择PDF文件")
            return
            
        try:
            self.update_status("正在读取PDF信息...")
            info = self.pdf_ops.get_pdf_info(Path(input_file))
            
            # Display info
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            
            info_text = f"""文件路径: {info.file_path}
页数: {info.pages}
标题: {info.title or '无'}
作者: {info.author or '无'}
创建时间: {info.creation_date or '无'}
文件大小: {info.file_size / 1024 / 1024:.2f} MB
"""
            
            self.info_text.insert(1.0, info_text)
            self.info_text.config(state=tk.DISABLED)
            
            self.update_status("PDF信息读取完成")
            logger.info(f"Successfully read PDF info for {input_file}")
            
        except PDFToolError as e:
            self.update_status("PDF信息读取失败")
            messagebox.showerror("错误", str(e))
            logger.error(f"Info extraction failed: {str(e)}")
        except Exception as e:
            self.update_status("PDF信息读取失败")
            messagebox.showerror("错误", f"读取PDF信息时出错: {str(e)}")
            logger.error(f"Info extraction failed: {str(e)}")


def main():
    """Main entry point for GUI application"""
    root = tk.Tk()
    app = ModernPDFTool(root)
    
    # Handle window closing
    def on_closing():
        if messagebox.askokcancel("退出", "确定要退出PDFTool吗？"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()