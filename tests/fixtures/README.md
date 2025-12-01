# Test Fixtures

This directory contains **real test assets** (not mocks) for testing file upload functionality.

## Philosophy

We use **real files instead of mocks** to ensure tests catch real-world issues:
- Actual MIME type detection
- Real file size calculations  
- Genuine binary data handling
- Realistic error scenarios

## Available Fixtures

### Image Files

- **`test_image.jpg`** - Minimal valid JPEG (~135 bytes)
  - Use for: Basic upload tests, MIME type validation
  
- **`test_image_5kb.jpg`** - Medium JPEG (~5KB)
  - Use for: Realistic upload tests, batch upload scenarios
  
- **`test_image.png`** - Minimal valid PNG (~50 bytes)
  - Use for: PNG format validation, multi-format tests
  
- **`test_image.webp`** - Minimal valid WebP (~20 bytes)
  - Use for: WebP format validation, modern format support

## Usage in Tests

```python
from pathlib import Path

def test_file_upload(sample_image_file):
    """Use fixture that provides Path object."""
    with open(sample_image_file, 'rb') as f:
        data = f.read()
    # Test with real file data

def test_with_direct_path():
    """Or access directly for custom scenarios."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    jpg_path = fixtures_dir / "test_image.jpg"
    png_path = fixtures_dir / "test_image.png"
    # Use as needed
```

## Generating Large Test Files

For tests requiring large files (e.g., 20MB+), generate them programmatically in the test itself:

```python
def test_large_file_upload():
    """Generate large file in test to avoid committing huge files."""
    large_file = io.BytesIO(b'\\xFF\\xD8\\xFF\\xE0' + b'\\x00' * (20 * 1024 * 1024) + b'\\xFF\\xD9')
    # Test with large file
```

This keeps the repository lean while still testing real-world scenarios.

