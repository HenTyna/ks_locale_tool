from flask import Flask, request, send_file, make_response
from flask_restx import Api, Resource, fields, Namespace
from flask_cors import CORS
from werkzeug.datastructures import FileStorage
import os
import re
import time
import tempfile
import shutil
from typing import List, Dict
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.expanduser('~'), 'locale_tool_uploads')
ALLOWED_EXTENSIONS = {'tsx'}

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Flask-RESTX
api = Api(
    app,
    version='1.0.0',
    title='Locale Tool API',
    description='A REST API for processing TSX files to find and apply localization templates to Korean text',
    doc='/docs/',  # Swagger UI will be available at /docs/
    prefix='/api'
)

class LocaleService:
    """Service class containing the core locale processing logic"""
    
    def __init__(self):
        # Korean language detection pattern
        self.korean_pattern = re.compile(r'[가-힣]+')
        
        # Template patterns
        self.bt_template = r'\{bt\("W\d+",\s*"([^"]+)"\)\}'
        self.bvt_template = r'\{bvt\(([^)]+)\)\}'
    
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
        
        # If no joined text found, return all segments
        return korean_segments
    
    def find_tsx_elements_with_korean(self, content: str) -> List[Dict]:
        """Find TSX elements containing Korean text"""
        elements = []
        
        # First, find simple elements (those without nested tags)
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
        
        # Also check for attributes with Korean text
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
    
    def has_any_template(self, text: str) -> bool:
        """Check if text has any template (bt or bvt)"""
        bt_pattern = r'\{bt\("W\d+",\s*"[^"]+"\)\}'
        return bool(re.search(bt_pattern, text) or re.search(self.bvt_template, text))
    
    def search_untemplated(self, content: str) -> Dict:
        """Search for elements without templates"""
        start_time = time.time()
        
        # Find elements with Korean text
        elements = self.find_tsx_elements_with_korean(content)
        
        # Filter out already templated elements
        untemplated_elements = []
        for element in elements:
            if not self.has_any_template(element['full_match']):
                untemplated_elements.append(element)
        
        duration = time.time() - start_time
        
        return {
            'success': True,
            'count': len(untemplated_elements),
            'elements': untemplated_elements,
            'duration': duration,
            'message': f'Found {len(untemplated_elements)} untemplated Korean elements'
        }
    
    def apply_template(self, content: str, template_type: str = 'bt') -> Dict:
        """Apply selected template to the content"""
        start_time = time.time()
        
        if template_type not in ['bt', 'bvt']:
            return {
                'success': False,
                'error': 'Invalid template type. Must be "bt" or "bvt"'
            }
        
        if template_type == 'bvt':
            return {
                'success': False,
                'error': 'BVT Template is temporarily disabled. Only BT Template is available.'
            }
        
        try:
            updated_content = content
            replacements_count = 0
            
            if template_type == "bt":
                # Process simple JSX elements
                simple_pattern = r'<(\w+)([^>]*?)>([^<]*)</\1>'
                simple_matches = list(re.finditer(simple_pattern, updated_content))
                
                # Process simple matches in reverse order
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
                    new_inner_text = inner_text
                    for korean_text in korean_texts:
                        if not self.has_any_template(korean_text):
                            new_inner_text = new_inner_text.replace(korean_text, f'{{bt("W#", "{korean_text}")}}')
                    
                    # Replace the entire match
                    new_element = f'<{tag_name}{attributes}>{new_inner_text}</{tag_name}>'
                    updated_content = updated_content[:match.start()] + new_element + updated_content[match.end():]
                
                # Replace attributes with Korean text
                attr_pattern = r'(\w+)=["\']([^"\']*[가-힣]+[^"\']*)["\']'
                attr_matches = list(re.finditer(attr_pattern, updated_content))
                
                # Process matches in reverse order
                for match in reversed(attr_matches):
                    attr_name = match.group(1)
                    attr_value = match.group(2)
                    
                    # Check if already templated
                    if self.has_any_template(match.group(0)):
                        continue
                    
                    # Apply BT template
                    replacements_count += 1
                    bt_template = f'bt("W#", "{attr_value}")'
                    new_attr = f'{attr_name}={{{bt_template}}}'
                    updated_content = updated_content[:match.start()] + new_attr + updated_content[match.end():]
            
            duration = time.time() - start_time
            
            return {
                'success': True,
                'updated_content': updated_content,
                'replacements_count': replacements_count,
                'duration': duration,
                'message': f'Template applied successfully! {replacements_count} replacements in {duration:.2f}s'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to apply template: {str(e)}'
            }

# Initialize the service
locale_service = LocaleService()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(uploaded_file, save_to_disk=False):
    """Save uploaded file to temporary location or return content only"""
    if not allowed_file(uploaded_file.filename):
        return None, "File type not allowed. Only TSX files are supported."
    
    try:
        content = uploaded_file.read().decode('utf-8')
        uploaded_file.seek(0)  # Reset file pointer
        
        if save_to_disk:
            # Save to upload directory
            filename = uploaded_file.filename
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # Create backup if file exists
            if os.path.exists(file_path):
                backup_path = file_path + '.backup'
                shutil.copy2(file_path, backup_path)
            
            # Save file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return content, file_path
        else:
            # Just return content without saving
            return content, None
            
    except UnicodeDecodeError:
        return None, "File must be UTF-8 encoded"
    except Exception as e:
        return None, f"Error processing file: {str(e)}"

# Create namespaces
health_ns = Namespace('health', description='Health check operations')
search_ns = Namespace('search', description='Search for untemplated Korean elements')
apply_ns = Namespace('apply', description='Apply templates to Korean text')
file_ns = Namespace('file', description='File processing operations')

# Add namespaces to API
api.add_namespace(health_ns)
api.add_namespace(search_ns)
api.add_namespace(apply_ns)
api.add_namespace(file_ns)

# Define API models
health_model = api.model('Health', {
    'status': fields.String(required=True, description='Service status'),
    'service': fields.String(required=True, description='Service name'),
    'version': fields.String(required=True, description='API version')
})

content_model = api.model('Content', {
    'content': fields.String(required=True, description='TSX content to process')
})

# File upload parser for search endpoint
search_parser = api.parser()
search_parser.add_argument('file', location='files', type=FileStorage, required=True, help='TSX file to process')
search_parser.add_argument('template_type', location='form', default='bt', choices=['bt', 'bvt'], help='Template type to use for search')

# File upload parser for apply endpoint  
apply_parser = api.parser()
apply_parser.add_argument('file', location='files', type=FileStorage, required=True, help='TSX file to process')
apply_parser.add_argument('template_type', location='form', default='bt', choices=['bt', 'bvt'], help='Template type to apply')
apply_parser.add_argument('return_file', location='form', type=bool, default=False, help='Whether to return the processed file as download')

apply_model = api.model('ApplyTemplate', {
    'content': fields.String(required=True, description='TSX content to process'),
    'template_type': fields.String(required=False, default='bt', enum=['bt', 'bvt'], description='Template type to apply')
})

file_model = api.model('ProcessFile', {
    'file_path': fields.String(required=True, description='Path to the TSX file'),
    'operation': fields.String(required=False, default='search', enum=['search', 'apply'], description='Operation to perform'),
    'template_type': fields.String(required=False, default='bt', enum=['bt', 'bvt'], description='Template type to apply')
})

element_model = api.model('Element', {
    'tag': fields.String(description='HTML/JSX tag name'),
    'attributes': fields.String(description='Element attributes'),
    'inner_text': fields.String(description='Inner text content'),
    'korean_texts': fields.List(fields.String, description='Korean text segments found'),
    'start': fields.Integer(description='Start position in content'),
    'end': fields.Integer(description='End position in content'),
    'full_match': fields.String(description='Full matched element'),
    'is_simple': fields.Boolean(description='Whether element is simple (no nested tags)'),
    'is_self_closing': fields.Boolean(description='Whether element is self-closing'),
    'is_attribute': fields.Boolean(description='Whether this is an attribute match')
})

debug_info_model = api.model('DebugInfo', {
    'file_size': fields.Integer(description='Size of uploaded file in characters'),
    'korean_segments_found': fields.Integer(description='Number of Korean text segments found'),
    'korean_segments': fields.List(fields.String, description='First 5 Korean text segments found')
})

search_response_model = api.model('SearchResponse', {
    'success': fields.Boolean(description='Whether operation was successful'),
    'count': fields.Integer(description='Number of untemplated elements found'),
    'elements': fields.List(fields.Nested(element_model), description='List of untemplated elements'),
    'duration': fields.Float(description='Processing time in seconds'),
    'message': fields.String(description='Response message'),
    'filename': fields.String(description='Name of uploaded file (if applicable)'),
    'template_type': fields.String(description='Template type used for search'),
    'debug_info': fields.Nested(debug_info_model, description='Debug information about the file')
})

apply_response_model = api.model('ApplyResponse', {
    'success': fields.Boolean(description='Whether operation was successful'),
    'updated_content': fields.String(description='Content with templates applied'),
    'replacements_count': fields.Integer(description='Number of replacements made'),
    'duration': fields.Float(description='Processing time in seconds'),
    'message': fields.String(description='Response message'),
    'filename': fields.String(description='Name of uploaded file (if applicable)'),
    'template_type': fields.String(description='Template type applied')
})

error_model = api.model('Error', {
    'success': fields.Boolean(description='Whether operation was successful'),
    'error': fields.String(description='Error message')
})

@health_ns.route('/')
class HealthCheck(Resource):
    @health_ns.marshal_with(health_model)
    @health_ns.doc('health_check')
    def get(self):
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'Locale Tool API',
            'version': '1.0.0'
        }

@search_ns.route('/')
class SearchUntemplated(Resource):
    @search_ns.expect(search_parser)
    @search_ns.doc('search_untemplated')
    def post(self):
        """Search for untemplated Korean elements in uploaded TSX file"""
        try:
            args = search_parser.parse_args()
            
            # Get uploaded file
            uploaded_file = args['file']
            template_type = args['template_type']
            
            if not uploaded_file:
                return {
                    'success': False,
                    'error': 'File is required'
                }, 400
            
            # Process file (read content only, don't save to disk)
            content, _ = save_uploaded_file(uploaded_file, save_to_disk=False)
            
            if content is None:
                return {
                    'success': False,
                    'error': _  # _ contains error message in this case
                }, 400
            
            # Get search results from locale service
            result = locale_service.search_untemplated(content)
            
            # Add additional information
            result['filename'] = uploaded_file.filename
            result['template_type'] = template_type
            
            # Add debug information
            korean_pattern = re.compile(r'[가-힣]+')
            korean_matches = korean_pattern.findall(content)
            result['debug_info'] = {
                'file_size': len(content),
                'korean_segments_found': len(korean_matches),
                'korean_segments': korean_matches[:5] if korean_matches else []
            }
            
            return result, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Internal server error: {str(e)}'
            }, 500

@search_ns.route('/content')
class SearchUntemplatedContent(Resource):
    @search_ns.expect(content_model)
    @search_ns.doc('search_untemplated_content')
    def post(self):
        """Search for untemplated Korean elements in TSX content (text input)"""
        try:
            data = api.payload
            
            if not data or 'content' not in data:
                return {
                    'success': False,
                    'error': 'Content is required'
                }, 400
            
            content = data['content']
            if not isinstance(content, str):
                return {
                    'success': False,
                    'error': 'Content must be a string'
                }, 400
            
            result = locale_service.search_untemplated(content)
            return result, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Internal server error: {str(e)}'
            }, 500

@apply_ns.route('/')
class ApplyTemplate(Resource):
    @apply_ns.expect(apply_parser)
    @apply_ns.doc('apply_template')
    def post(self):
        """Apply template to uploaded TSX file"""
        try:
            args = apply_parser.parse_args()
            
            # Get uploaded file and parameters
            uploaded_file = args['file']
            template_type = args['template_type']
            return_file = args.get('return_file', False)
            
            if not uploaded_file:
                return {
                    'success': False,
                    'error': 'File is required'
                }, 400
            
            # Process file (read content only)
            content, _ = save_uploaded_file(uploaded_file, save_to_disk=False)
            
            if content is None:
                return {
                    'success': False,
                    'error': _  # _ contains error message in this case
                }, 400
            
            # Apply template
            result = locale_service.apply_template(content, template_type)
            
            if result['success']:
                # Add file operation info to result
                result['filename'] = uploaded_file.filename
                result['template_type'] = template_type
                
                if return_file:
                    # Return the processed file as download
                    try:
                        # Create temporary file with processed content
                        temp_file = tempfile.NamedTemporaryFile(
                            mode='w', 
                            suffix='.tsx', 
                            delete=False, 
                            encoding='utf-8'
                        )
                        temp_file.write(result['updated_content'])
                        temp_file.close()
                        
                        # Create response with file download
                        response = make_response(send_file(
                            temp_file.name,
                            as_attachment=True,
                            download_name=f"processed_{uploaded_file.filename}",
                            mimetype='text/plain'
                        ))
                        
                        # Clean up temp file after sending
                        def remove_file(response):
                            try:
                                os.unlink(temp_file.name)
                            except:
                                pass
                            return response
                        
                        response.call_on_close(lambda: os.unlink(temp_file.name))
                        
                        return response
                        
                    except Exception as file_error:
                        return {
                            'success': False,
                            'error': f'Failed to create download file: {str(file_error)}'
                        }, 500
                else:
                    # Return JSON response with updated content
                    result['message'] += " (Use return_file=true to download the processed file)"
                    return result, 200
            else:
                return {
                    'success': False,
                    'error': result['error']
                }, 400
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Internal server error: {str(e)}'
            }, 500

@apply_ns.route('/content')
class ApplyTemplateContent(Resource):
    @apply_ns.expect(apply_model)
    @apply_ns.doc('apply_template_content')
    def post(self):
        """Apply template to TSX content (text input)"""
        try:
            data = api.payload
            
            if not data or 'content' not in data:
                return {
                    'success': False,
                    'error': 'Content is required'
                }, 400
            
            content = data['content']
            template_type = data.get('template_type', 'bt')
            
            if not isinstance(content, str):
                return {
                    'success': False,
                    'error': 'Content must be a string'
                }, 400
            
            result = locale_service.apply_template(content, template_type)
            
            if result['success']:
                return result, 200
            else:
                return {
                    'success': False,
                    'error': result['error']
                }, 400
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Internal server error: {str(e)}'
            }, 500

@file_ns.route('/')
class ProcessFile(Resource):
    @file_ns.expect(file_model)
    @file_ns.marshal_with(search_response_model, code=200)
    @file_ns.marshal_with(apply_response_model, code=200)
    @file_ns.marshal_with(error_model, code=400)
    @file_ns.marshal_with(error_model, code=404)
    @file_ns.marshal_with(error_model, code=500)
    @file_ns.doc('process_file')
    def post(self):
        """Process a file by file path (for server-side file processing)"""
        try:
            data = api.payload
            
            if not data or 'file_path' not in data:
                api.abort(400, 'File path is required')
            
            file_path = data['file_path']
            operation = data.get('operation', 'search')  # 'search' or 'apply'
            template_type = data.get('template_type', 'bt')
            
            if not os.path.exists(file_path):
                api.abort(404, 'File not found')
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if operation == 'search':
                result = locale_service.search_untemplated(content)
            elif operation == 'apply':
                result = locale_service.apply_template(content, template_type)
                
                # If apply was successful, write back to file
                if result['success']:
                    # Create backup
                    backup_path = file_path + '.backup'
                    with open(backup_path, 'w', encoding='utf-8') as backup_file:
                        backup_file.write(content)
                    
                    # Write updated content
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(result['updated_content'])
                    
                    result['backup_created'] = backup_path
            else:
                api.abort(400, 'Invalid operation. Must be "search" or "apply"')
            
            return result
            
        except Exception as e:
            api.abort(500, f'Internal server error: {str(e)}')

if __name__ == '__main__':
    # Get port from environment variable (Railway sets this)
    port = int(os.environ.get('PORT', 5000))
    # Use debug=False for production
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting Flask app on port {port}")
    print(f"Debug mode: {debug}")
    
    app.run(debug=debug, host='0.0.0.0', port=port, threaded=True)
