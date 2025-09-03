# Locale Tool - BT/BVT Template Updater

A Python automation tool for updating TSX files with BT and BVT localization templates. This tool automatically detects Korean text in TSX elements and applies the appropriate template format.

## Features

- **File Input**: Browse and select TSX files for processing
- **Template Selection**: Choose between BT and BVT templates
- **Korean Text Detection**: Automatically detects Korean language text in TSX elements
- **Smart Template Application**: Applies templates only to untemplated Korean text
- **Search Functionality**: Find all untemplated Korean elements without applying changes
- **Backup Creation**: Automatically creates backup files before making changes
- **Real-time Results**: Display search results and application statistics

## Template Formats

### BT Template
- **Format**: `{bt(W#, "text")}`
- **Usage**: For JSX elements and attributes containing Korean text
- **Example**: 
  - Before: `<p>한고어</p>`
  - After: `<p>{bt(W#, "한고어")}</p>`

### BVT Template
- **Format**: `{bvt(param)}`
- **Usage**: For Korean text in variable assignments and object properties
- **Example**:
  - Before: `const name = "한고어"`
  - After: `const name = {bvt(name)}`

## Installation

1. Ensure you have Python 3.7+ installed
2. Clone or download this repository
3. Navigate to the project directory
4. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

## Usage

### Running the Tool

```bash
# From the project root
python src/locale_tool/main.py

# Or directly
python src/locale_tool/locale_tool.py
```

### Step-by-Step Process

1. **Load File**: Click "Browse" to select a TSX file
2. **Choose Template**: Select either "BT Template" or "BVT Template"
3. **Search First**: Click "Search Untemplated Elements" to see what will be changed
4. **Apply Template**: Click "Apply Template" to update the file
5. **Review Results**: Check the "Apply Results" tab for statistics

### UI Components

- **File Path**: Display and browse for TSX files
- **Template Selection**: Radio buttons for BT or BVT templates
- **Action Buttons**: Search, Apply, and Clear functions
- **Results Tabs**: Separate tabs for search and application results
- **Status Bar**: Shows current operation status and timing

## How It Works

### Korean Text Detection
The tool uses regex patterns to detect Korean characters (`[가-힣]+`) in:
- JSX element content: `<tag>한국어</tag>`
- JSX attributes: `placeholder="한국어"`, `title="한국어"`
- Variable assignments: `const text = "한국어"`

### Template Application
1. **BT Template**: Wraps Korean text in JSX elements and attributes
2. **BVT Template**: Replaces Korean text with variable references
3. **Smart Detection**: Only applies templates to untemplated text
4. **Backup Creation**: Creates `.backup` files before making changes

### Safety Features
- Automatic backup creation
- Template collision detection
- Precise regex matching
- Error handling and user feedback

## Examples

### Input File (example.tsx)
```tsx
import React from 'react';

const Component = () => {
  const message = "안녕하세요";
  
  return (
    <div>
      <h1>제목</h1>
      <p>내용입니다</p>
      <input placeholder="입력하세요" />
      <button title="클릭하세요">버튼</button>
    </div>
  );
};

export default Component;
```

### After BT Template Application
```tsx
import React from 'react';

const Component = () => {
  const message = "안녕하세요";
  
  return (
    <div>
      <h1>{bt(W#, "제목")}</h1>
      <p>{bt(W#, "내용입니다")}</p>
      <input placeholder={bt(W#, "입력하세요")} />
      <button title={bt(W#, "클릭하세요")}>{bt(W#, "버튼")}</button>
    </div>
  );
};

export default Component;
```

## Notes

- **Korean Language Only**: The tool specifically detects Korean text using Unicode ranges
- **TSX Focus**: Designed for React TypeScript files but works with any TSX/JSX files
- **Non-Destructive**: Always creates backups before making changes
- **Template Collision**: Automatically detects and skips already templated text
- **Performance**: Optimized for large files with efficient regex patterns

## Troubleshooting

### Common Issues
1. **File Not Found**: Ensure the file path is correct and accessible
2. **Permission Errors**: Check file write permissions
3. **Encoding Issues**: Files should be UTF-8 encoded
4. **No Korean Text**: Tool only processes files containing Korean characters

### Error Messages
- **"Failed to load file"**: Check file path and permissions
- **"Failed to apply template"**: Review file content and try again
- **"No untemplated elements found"**: All Korean text already has templates

## Development

The tool is built with:
- **Tkinter**: Native Python GUI framework
- **Regex**: Pattern matching for text detection
- **File I/O**: Safe file reading and writing
- **Error Handling**: Comprehensive exception management

## License

This tool is provided as-is for educational and development purposes.
