import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import os
import time
from typing import List, Tuple, Dict
import json

class LocaleTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Locale Tool - BT/BVT Template Updater")
        self.root.geometry("800x600")
        
        # Korean language detection pattern
        self.korean_pattern = re.compile(r'[가-힣]+')
        
        # Template patterns - updated to match actual template formats
        self.bt_template = r'\{bt\("W\d+",\s*"([^"]+)"\)\}'
        self.bvt_template = r'\{bvt\(([^)]+)\)\}'
        
        # File content
        self.current_file_content = ""
        self.current_file_path = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # File selection
        ttk.Label(main_frame, text="File Path:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(main_frame, textvariable=self.file_path_var, width=50)
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=(5, 0), pady=5)
        
        # Template selection (BVT temporarily disabled)
        ttk.Label(main_frame, text="Template:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.template_var = tk.StringVar(value="bt")
        template_frame = ttk.Frame(main_frame)
        template_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(template_frame, text="BT Template", variable=self.template_var, value="bt").pack(side=tk.LEFT)
        # ttk.Radiobutton(template_frame, text="BVT Template", variable=self.template_var, value="bvt").pack(side=tk.LEFT, padx=(20, 0))
        ttk.Label(template_frame, text="(BVT Template temporarily disabled)", foreground="gray").pack(side=tk.LEFT, padx=(20, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        ttk.Button(button_frame, text="Search Untemplated Elements", command=self.search_untemplated).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Apply Template", command=self.apply_template).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear Results", command=self.clear_results).pack(side=tk.LEFT)
        
        # Results display
        ttk.Label(main_frame, text="Results:").grid(row=3, column=0, sticky=tk.W, pady=(20, 5))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Search results tab
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Search Results")
        
        # Apply results tab
        self.apply_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.apply_frame, text="Apply Results")
        
        # Search results
        self.search_text = tk.Text(self.search_frame, height=15, width=80)
        search_scrollbar = ttk.Scrollbar(self.search_frame, orient=tk.VERTICAL, command=self.search_text.yview)
        self.search_text.configure(yscrollcommand=search_scrollbar.set)
        self.search_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        search_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Apply results
        self.apply_text = tk.Text(self.apply_frame, height=15, width=80)
        apply_scrollbar = ttk.Scrollbar(self.apply_frame, orient=tk.VERTICAL, command=self.apply_text.yview)
        self.apply_text.configure(yscrollcommand=apply_scrollbar.set)
        self.apply_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        apply_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure row weights for proper resizing
        main_frame.rowconfigure(4, weight=1)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select TSX File",
            filetypes=[("TSX files", "*.tsx"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.current_file_path = file_path
            self.load_file_content()
    
    def load_file_content(self):
        try:
            with open(self.current_file_path, 'r', encoding='utf-8') as file:
                self.current_file_content = file.read()
            self.status_var.set(f"File loaded: {os.path.basename(self.current_file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
            self.status_var.set("Error loading file")
    
    def detect_korean_text(self, text: str) -> List[str]:
        """Detect Korean text in the given string"""
        # Find all Korean text segments first
        korean_segments = self.korean_pattern.findall(text)
        
        if not korean_segments:
            return []
        
        # If there's only one segment, return it
        if len(korean_segments) == 1:
            return korean_segments
        
        # If there are multiple segments, try to find the largest continuous block
        # Look for patterns like "다운로드 란눌" where Korean words are separated by spaces
        largest_joined = ""
        
        # Try all possible combinations of segments
        for i in range(len(korean_segments)):
            for j in range(i + 1, len(korean_segments) + 1):
                # Try to join segments from i to j-1
                joined_text = " ".join(korean_segments[i:j])
                # Check if this joined text exists in the original text
                if joined_text in text and len(joined_text) > len(largest_joined):
                    largest_joined = joined_text
        
        # If we found a joined text, return it
        if largest_joined:
            return [largest_joined]
        
        # If no joined text found, return all segments (this handles cases where they can't be joined)
        return korean_segments
    
    def find_tsx_elements_with_korean(self, content: str) -> List[Dict]:
        """Find TSX elements containing Korean text"""
        elements = []
        
        # First, find simple elements (those without nested tags) - these are what we want
        simple_pattern = r'<(\w+)([^>]*?)>([^<]*)</\1>'
        
        for match in re.finditer(simple_pattern, content):
            tag_name = match.group(1)
            attributes = match.group(2)
            inner_text = match.group(3).strip()
            
            # Check if inner text contains Korean
            korean_texts = self.detect_korean_text(inner_text)
            if korean_texts:
                elements.append({
                    'tag': tag_name,
                    'attributes': attributes,
                    'inner_text': inner_text,
                    'korean_texts': korean_texts,
                    'start': match.start(),
                    'end': match.end(),
                    'full_match': match.group(0),
                    'is_simple': True
                })
        
        # Also check for self-closing tags with Korean text in attributes
        self_closing_pattern = r'<(\w+)([^>]*?)/>'
        for match in re.finditer(self_closing_pattern, content):
            tag_name = match.group(1)
            attributes = match.group(2)
            
            # Check if attributes contain Korean text
            korean_texts = self.detect_korean_text(attributes)
            if korean_texts:
                elements.append({
                    'tag': tag_name,
                    'attributes': attributes,
                    'inner_text': '',
                    'korean_texts': korean_texts,
                    'start': match.start(),
                    'end': match.end(),
                    'full_match': match.group(0),
                    'is_self_closing': True
                })
        
        # Also check for attributes with Korean text (placeholder, label, title, etc.)
        attr_pattern = r'(\w+)=["\']([^"\']*[가-힣]+[^"\']*)["\']'
        for match in re.finditer(attr_pattern, content):
            attr_name = match.group(1)
            attr_value = match.group(2)
            korean_texts = self.detect_korean_text(attr_value)
            if korean_texts:
                elements.append({
                    'tag': 'attribute',
                    'attributes': f'{attr_name}="{attr_value}"',
                    'inner_text': attr_value,
                    'korean_texts': korean_texts,
                    'start': match.start(),
                    'end': match.end(),
                    'full_match': match.group(0),
                    'is_attribute': True
                })
        
        return elements
    
    def is_already_templated(self, text: str, template_type: str) -> bool:
        """Check if text already has the specified template"""
        if template_type == "bt":
            return bool(re.search(self.bt_template, text))
        elif template_type == "bvt":
            return bool(re.search(self.bvt_template, text))
        return False
    
    def has_any_template(self, text: str) -> bool:
        """Check if text has any template (bt or bvt)"""
        # Check for BT templates with any W number (e.g., W1152, W10979, etc.)
        bt_pattern = r'\{bt\("W\d+",\s*"[^"]+"\)\}'
        return bool(re.search(bt_pattern, text) or re.search(self.bvt_template, text))
    
    def search_untemplated(self):
        """Search for elements without templates"""
        if not self.current_file_content:
            messagebox.showwarning("Warning", "Please load a file first")
            return
        
        start_time = time.time()
        
        # Find elements with Korean text
        elements = self.find_tsx_elements_with_korean(self.current_file_content)
        
        # Filter out already templated elements
        untemplated_elements = []
        for element in elements:
            if not self.has_any_template(element['full_match']):
                untemplated_elements.append(element)
        
        # Display results
        self.search_text.delete(1.0, tk.END)
        
        if not untemplated_elements:
            self.search_text.insert(tk.END, "No untemplated Korean elements found.\n")
        else:
            self.search_text.insert(tk.END, f"Found {len(untemplated_elements)} untemplated Korean elements:\n\n")
            
            for i, element in enumerate(untemplated_elements, 1):
                if element.get('is_attribute'):
                    self.search_text.insert(tk.END, f"{i}. Attribute: {element['attributes']}\n")
                elif element.get('is_self_closing'):
                    self.search_text.insert(tk.END, f"{i}. Self-closing: <{element['tag']}{element['attributes']}/>\n")
                else:
                    self.search_text.insert(tk.END, f"{i}. Element: <{element['tag']}{element['attributes']}>{element['inner_text']}</{element['tag']}>\n")
                
                self.search_text.insert(tk.END, f"   Korean text: {', '.join(element['korean_texts'])}\n")
                self.search_text.insert(tk.END, f"   Position: {element['start']}-{element['end']}\n\n")
        
        duration = time.time() - start_time
        self.status_var.set(f"Search completed in {duration:.2f}s. Found {len(untemplated_elements)} untemplated elements.")
    
    def apply_template(self):
        """Apply selected template to the file"""
        if not self.current_file_content or not self.current_file_path:
            messagebox.showwarning("Warning", "Please load a file first")
            return
        
        template_type = self.template_var.get()
        start_time = time.time()
        
        try:
            # Create backup
            backup_path = self.current_file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as backup_file:
                backup_file.write(self.current_file_content)
            
            # Find and replace elements
            updated_content = self.current_file_content
            replacements_count = 0
            
            if template_type == "bt":
                # Process simple JSX elements one by one to avoid multiple replacements
                # Use the same approach as search: simple elements first
                simple_pattern = r'<(\w+)([^>]*?)>([^<]*)</\1>'
                
                # Find all simple matches first (these are usually the ones we want)
                simple_matches = list(re.finditer(simple_pattern, updated_content))
                
                # Process simple matches in reverse order to avoid position shifting issues
                for match in reversed(simple_matches):
                    tag_name = match.group(1)
                    attributes = match.group(2)
                    inner_text = match.group(3)
                    
                    # Check if already templated
                    if self.has_any_template(match.group(0)):
                        continue
                    
                    # Check if inner text contains Korean
                    korean_texts = self.detect_korean_text(inner_text)
                    if not korean_texts:
                        continue
                    
                    # Apply BT template to Korean text only
                    replacements_count += 1
                    # Replace Korean text with template, preserving exact whitespace and structure
                    new_inner_text = inner_text
                    for korean_text in korean_texts:
                        # Only replace if this Korean text is not already in a template
                        if not self.has_any_template(korean_text):
                            new_inner_text = new_inner_text.replace(korean_text, f'{{bt("W#", "{korean_text}")}}')
                    
                    # Replace the entire match
                    new_element = f'<{tag_name}{attributes}>{new_inner_text}</{tag_name}>'
                    updated_content = updated_content[:match.start()] + new_element + updated_content[match.end():]
                
                # Replace attributes with Korean text
                attr_pattern = r'(\w+)=["\']([^"\']*[가-힣]+[^"\']*)["\']'
                
                # Find all attribute matches first
                attr_matches = list(re.finditer(attr_pattern, updated_content))
                
                # Process matches in reverse order to avoid position shifting issues
                for match in reversed(attr_matches):
                    attr_name = match.group(1)
                    attr_value = match.group(2)
                    
                    # Check if already templated
                    if self.has_any_template(match.group(0)):
                        continue
                    
                    # Apply BT template
                    replacements_count += 1
                    new_attr = f'{attr_name}={{{"bt(\"W#\", \"" + attr_value + "\")"}}}'
                    updated_content = updated_content[:match.start()] + new_attr + updated_content[match.end():]
                
            elif template_type == "bvt":
                # BVT template temporarily disabled
                messagebox.showinfo("Info", "BVT Template is temporarily disabled. Only BT Template is available.")
                return
            
            # Write updated content
            with open(self.current_file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            
            # Update current content
            self.current_file_content = updated_content
            
            duration = time.time() - start_time
            
            # Display results
            self.apply_text.delete(1.0, tk.END)
            self.apply_text.insert(tk.END, "Template application completed successfully!\n\n")
            self.apply_text.insert(tk.END, f"Template type: {template_type.upper()}\n")
            self.apply_text.insert(tk.END, f"Replacements made: {replacements_count}\n")
            self.apply_text.insert(tk.END, f"Duration: {duration:.2f}s\n")
            self.apply_text.insert(tk.END, f"Backup created: {os.path.basename(backup_path)}\n")
            
            self.status_var.set(f"Template applied successfully! {replacements_count} replacements in {duration:.2f}s")
            
            # Switch to apply results tab
            self.notebook.select(1)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply template: {str(e)}")
            self.status_var.set("Error applying template")
    
    def clear_results(self):
        """Clear all result displays"""
        self.search_text.delete(1.0, tk.END)
        self.apply_text.delete(1.0, tk.END)
        self.status_var.set("Results cleared")

def main():
    root = tk.Tk()
    app = LocaleTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
