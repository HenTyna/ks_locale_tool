# Locale Tool API

A Flask-based REST API for processing TSX files to find and apply localization templates to Korean text.

## Features

- **Search for untemplated Korean elements** in TSX content
- **Apply BT/BVT templates** to Korean text
- **Smart file handling** - no project directory pollution
- **Optional file saving** - control whether to save files to disk
- **Automatic backup creation** when saving files
- **CORS enabled** for web applications
- **Comprehensive error handling**

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API

```bash
cd src/api
python app.py
```

The API will be available at `http://localhost:5000`

## Configuration

### File Handling
- **No disk storage**: Files are processed in memory only
- **Temporary files**: Used only for file downloads, automatically cleaned up
- **No project pollution**: Original files and project structure remain unchanged
- **Download naming**: Processed files are named `processed_original_filename.tsx`

## Swagger UI Documentation

Once the API is running, you can access the interactive Swagger UI documentation at:
**http://localhost:5000/docs/**

The Swagger UI provides:
- Interactive API documentation
- Try-it-out functionality for all endpoints
- Request/response schema definitions
- Example requests and responses

## API Endpoints

### Health Check
- **GET** `/api/health/`
- Returns API status and version information

### Search Untemplated Elements

#### File Upload (Primary Method)
- **POST** `/api/search/`
- Searches for Korean text elements that don't have templates in uploaded TSX file

**Request Parameters:**
- `file` (required): TSX file to upload
- `template_type` (optional): Template type to use for search (`bt` or `bvt`, default: `bt`)

**Example using curl:**
```bash
curl -X POST http://localhost:5000/api/search/ \
  -F "file=@your_file.tsx" \
  -F "template_type=bt"
```

#### Text Input (Alternative Method)
- **POST** `/api/search/content`
- Searches for Korean text elements that don't have templates in provided content

**Request Body:**
```json
{
  "content": "Your TSX content here..."
}
```

**Response:**
```json
{
  "success": true,
  "count": 5,
  "elements": [
    {
      "tag": "span",
      "attributes": " className=\"text\"",
      "inner_text": "안녕하세요",
      "korean_texts": ["안녕하세요"],
      "start": 100,
      "end": 150,
      "full_match": "<span className=\"text\">안녕하세요</span>",
      "is_simple": true
    }
  ],
  "duration": 0.05,
  "message": "Found 5 untemplated Korean elements",
  "filename": "your_file.tsx",
  "template_type": "bt"
}
```

### Apply Template

#### File Upload (Primary Method)
- **POST** `/api/apply/`
- Applies BT or BVT templates to Korean text in uploaded TSX file

**Request Parameters:**
- `file` (required): TSX file to upload
- `template_type` (optional): Template type to apply (`bt` or `bvt`, default: `bt`)
- `return_file` (optional): Whether to return processed file as download (boolean, default: `false`)

**Response Types:**
- **JSON Response** (`return_file=false`): Returns JSON with updated content and processing info
- **File Download** (`return_file=true`): Returns the processed TSX file as a downloadable attachment

**File Handling:**
- No files are saved to disk (no project pollution)
- Temporary files are automatically cleaned up
- Original uploaded files are not modified

**Example using curl (JSON response):**
```bash
curl -X POST http://localhost:5000/api/apply/ \
  -F "file=@your_file.tsx" \
  -F "template_type=bt" \
  -F "return_file=false"
```

**Example using curl (file download):**
```bash
curl -X POST http://localhost:5000/api/apply/ \
  -F "file=@your_file.tsx" \
  -F "template_type=bt" \
  -F "return_file=true" \
  -o processed_file.tsx
```

#### Text Input (Alternative Method)
- **POST** `/api/apply/content`
- Applies BT or BVT templates to Korean text in provided content

**Request Body:**
```json
{
  "content": "Your TSX content here...",
  "template_type": "bt"
}
```

**Response:**
```json
{
  "success": true,
  "updated_content": "Updated TSX content with templates...",
  "replacements_count": 3,
  "duration": 0.08,
  "message": "Template applied successfully! 3 replacements in 0.08s",
  "filename": "your_file.tsx",
  "template_type": "bt"
}
```

### Process File
- **POST** `/api/file/`
- Processes a file directly on the server

**Request Body:**
```json
{
  "file_path": "/path/to/your/file.tsx",
  "operation": "apply",
  "template_type": "bt"
}
```

**Response:**
```json
{
  "success": true,
  "updated_content": "Updated content...",
  "replacements_count": 3,
  "duration": 0.08,
  "backup_created": "/path/to/your/file.tsx.backup",
  "message": "Template applied successfully! 3 replacements in 0.08s"
}
```

## Template Types

### BT Template
- Format: `{bt("W#", "Korean text")}`
- Currently supported
- Replaces Korean text with BT template format

### BVT Template
- Format: `{bvt(...)}`
- Currently disabled
- Will be available in future updates

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error message description"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found (file not found)
- `405`: Method Not Allowed
- `500`: Internal Server Error

## Usage Examples

### Using curl

**Search for untemplated elements (file upload):**
```bash
curl -X POST http://localhost:5000/api/search/ \
  -F "file=@your_file.tsx" \
  -F "template_type=bt"
```

**Apply BT template (file upload):**
```bash
curl -X POST http://localhost:5000/api/apply/ \
  -F "file=@your_file.tsx" \
  -F "template_type=bt"
```

**Search for untemplated elements (text input):**
```bash
curl -X POST http://localhost:5000/api/search/content \
  -H "Content-Type: application/json" \
  -d '{"content": "<span>안녕하세요</span>"}'
```

**Apply BT template (text input):**
```bash
curl -X POST http://localhost:5000/api/apply/content \
  -H "Content-Type: application/json" \
  -d '{"content": "<span>안녕하세요</span>", "template_type": "bt"}'
```

### Using JavaScript/Fetch

```javascript
// File upload example
const formData = new FormData();
formData.append('file', fileInput.files[0]); // fileInput is an HTML file input
formData.append('template_type', 'bt');

// Search for untemplated elements (file upload)
const searchResponse = await fetch('http://localhost:5000/api/search/', {
  method: 'POST',
  body: formData
});

const searchResult = await searchResponse.json();
console.log(searchResult);

// Apply template (file upload)
const applyResponse = await fetch('http://localhost:5000/api/apply/', {
  method: 'POST',
  body: formData
});

const applyResult = await applyResponse.json();
console.log(applyResult);

// Text input example
// Search for untemplated elements (text input)
const searchTextResponse = await fetch('http://localhost:5000/api/search/content', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    content: '<span>안녕하세요</span>'
  })
});

const searchTextResult = await searchTextResponse.json();
console.log(searchTextResult);

// Apply template (text input)
const applyTextResponse = await fetch('http://localhost:5000/api/apply/content', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    content: '<span>안녕하세요</span>',
    template_type: 'bt'
  })
});

const applyTextResult = await applyTextResponse.json();
console.log(applyTextResult);
```

## Development

The API is built with Flask-RESTX and includes:
- **Swagger UI** for interactive API documentation
- **CORS support** for cross-origin requests
- **Comprehensive error handling** with proper HTTP status codes
- **Input validation** using Flask-RESTX models
- **File backup functionality** when processing files
- **Performance timing** for all operations
- **Structured API documentation** with request/response schemas

## Notes

- The original GUI tool (`locale_tool.py`) remains unchanged and functional
- BVT template support is temporarily disabled
- All Korean text detection uses regex pattern `[가-힣]+`
- File operations create automatic backups when processing files
