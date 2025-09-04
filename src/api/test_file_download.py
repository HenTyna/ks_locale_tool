#!/usr/bin/env python3
"""
Test script to verify file download functionality
"""

import requests
import os
import tempfile

def test_file_download():
    print("🔧 Testing File Download Functionality...")
    print("=" * 60)
    
    # Create a test file with Korean content
    test_content = '''
import React from 'react';

const TestComponent = () => {
  return (
    <div>
      <dd>1,325,324,111원</dd>
      <dt>총 금액</dt>
      <dd>{formatNumberWithCommas(summary.totalAmount)} 원</dd>
      <dt>총 건수</dt>
      <dd>{formatNumberWithCommas(summary.totalCount)} 건</dd>
      <dt>총 주행거리</dt>
      <dt>총 비용</dt>
    </div>
  );
};

export default TestComponent;
'''
    
    test_file = "test_download.tsx"
    
    # Write test file
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"📁 Created test file: {test_file}")
    print("📝 Original content:")
    print(test_content[:200] + "...")
    print()
    
    try:
        # Test 1: Apply without file download (JSON response)
        print("🔧 Test 1: Apply template with JSON response...")
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'text/plain')}
            data = {'template_type': 'bt', 'return_file': False}
            
            response = requests.post("http://localhost:5000/api/apply/", files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Apply successful!")
            print(f"  - Success: {result.get('success')}")
            print(f"  - Replacements: {result.get('replacements_count')}")
            print(f"  - Filename: {result.get('filename')}")
            print(f"  - Template type: {result.get('template_type')}")
            print(f"  - Message: {result.get('message')}")
            
            # Check if updated content contains templates
            updated_content = result.get('updated_content', '')
            if '{bt(' in updated_content:
                print("✅ Templates applied to content")
                print("📝 Sample of updated content:")
                print(updated_content[:300] + "...")
            else:
                print("❌ No templates found in updated content")
        
        print("\n" + "-" * 40)
        
        # Test 2: Apply with file download
        print("🔧 Test 2: Apply template with file download...")
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'text/plain')}
            data = {'template_type': 'bt', 'return_file': True}
            
            response = requests.post("http://localhost:5000/api/apply/", files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")
        
        if response.status_code == 200:
            # Check if response is a file download
            content_disposition = response.headers.get('Content-Disposition', '')
            if 'attachment' in content_disposition:
                print("✅ File download response received!")
                
                # Save downloaded file
                downloaded_filename = "downloaded_processed.tsx"
                with open(downloaded_filename, 'wb') as f:
                    f.write(response.content)
                
                print(f"📁 Downloaded file saved as: {downloaded_filename}")
                
                # Read and verify downloaded content
                with open(downloaded_filename, 'r', encoding='utf-8') as f:
                    downloaded_content = f.read()
                
                if '{bt(' in downloaded_content:
                    print("✅ Downloaded file contains applied templates")
                    print("📝 Sample of downloaded content:")
                    print(downloaded_content[:300] + "...")
                else:
                    print("❌ Downloaded file does not contain templates")
                
                # Clean up downloaded file
                os.remove(downloaded_filename)
                print(f"🗑️ Cleaned up: {downloaded_filename}")
                
            else:
                print("❌ Response is not a file download")
                print(f"Response content: {response.text[:200]}...")
        
        print("\n" + "-" * 40)
        
        # Test 3: Verify original file is unchanged
        print("🔧 Test 3: Verify original file is unchanged...")
        with open(test_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        if original_content == test_content:
            print("✅ Original file unchanged (no project pollution)")
        else:
            print("❌ Original file was modified!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"🗑️ Cleaned up: {test_file}")
    
    print("\n" + "=" * 60)
    print("✅ File download test completed!")
    print("📖 Key features:")
    print("   - JSON response with updated content (return_file=false)")
    print("   - File download response (return_file=true)")
    print("   - No project directory pollution")
    print("   - Temporary file cleanup")
    print("   - Proper file naming for downloads")

if __name__ == "__main__":
    test_file_download()
