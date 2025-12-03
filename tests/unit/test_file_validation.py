"""
Unit tests for file upload validation.

Per FR-013, FR-014, FR-015: Validate file uploads for:
- Image type validation (JPEG, PNG, WebP)
- File count (5-15 images)
- Individual file size (20MB max)
- Total upload size (200MB max)
"""

import io
from src.services.r2_storage import R2StorageService


class TestFileUploadValidation:
    """Test file upload validation rules."""
    
    def test_valid_file_within_size_limit(self):
        """Test that a file under 20MB passes validation."""
        service = R2StorageService(
            endpoint_url="https://test.r2.cloudflarestorage.com",
            access_key_id="test_key",
            secret_access_key="test_secret",
            bucket_name="test-bucket",
            bucket_id="test123",
        )
        
        # 10MB file
        file_size = 10 * 1024 * 1024
        is_valid, error = service.validate_file_upload(
            file_size_bytes=file_size,
            file_name="photo.jpg",
            allowed_types=["image/jpeg", "image/png", "image/webp"],
            max_file_size_mb=20,
        )
        
        assert is_valid is True
        assert error is None
    
    def test_file_exceeds_size_limit(self):
        """Test that a file over 20MB fails validation."""
        service = R2StorageService(
            endpoint_url="https://test.r2.cloudflarestorage.com",
            access_key_id="test_key",
            secret_access_key="test_secret",
            bucket_name="test-bucket",
            bucket_id="test123",
        )
        
        # 25MB file
        file_size = 25 * 1024 * 1024
        is_valid, error = service.validate_file_upload(
            file_size_bytes=file_size,
            file_name="photo.jpg",
            allowed_types=["image/jpeg", "image/png", "image/webp"],
            max_file_size_mb=20,
        )
        
        assert is_valid is False
        assert error is not None
        assert "20MB" in error
        assert "photo.jpg" in error
    
    def test_valid_image_types(self):
        """Test that JPEG, PNG, WebP files pass type validation."""
        service = R2StorageService(
            endpoint_url="https://test.r2.cloudflarestorage.com",
            access_key_id="test_key",
            secret_access_key="test_secret",
            bucket_name="test-bucket",
            bucket_id="test123",
        )
        
        valid_files = ["photo.jpg", "image.jpeg", "picture.png", "graphic.webp"]
        file_size = 5 * 1024 * 1024  # 5MB
        
        for filename in valid_files:
            is_valid, error = service.validate_file_upload(
                file_size_bytes=file_size,
                file_name=filename,
                allowed_types=["image/jpeg", "image/png", "image/webp"],
                max_file_size_mb=20,
            )
            assert is_valid is True, f"File '{filename}' should be valid"
            assert error is None
    
    def test_invalid_file_types(self):
        """Test that non-image files fail validation."""
        service = R2StorageService(
            endpoint_url="https://test.r2.cloudflarestorage.com",
            access_key_id="test_key",
            secret_access_key="test_secret",
            bucket_name="test-bucket",
            bucket_id="test123",
        )
        
        invalid_files = ["document.pdf", "video.mp4", "audio.mp3", "file.txt", "script.js"]
        file_size = 5 * 1024 * 1024  # 5MB
        
        for filename in invalid_files:
            is_valid, error = service.validate_file_upload(
                file_size_bytes=file_size,
                file_name=filename,
                allowed_types=["image/jpeg", "image/png", "image/webp"],
                max_file_size_mb=20,
            )
            assert is_valid is False, f"File '{filename}' should be invalid"
            assert error is not None
            assert "not allowed" in error.lower() or "file type" in error.lower()


class TestBatchFileValidation:
    """Test batch file upload validation for count and total size."""
    
    def setup_method(self):
        """Create R2 service for testing."""
        self.service = R2StorageService(
            endpoint_url="https://test.r2.cloudflarestorage.com",
            access_key_id="test_key",
            secret_access_key="test_secret",
            bucket_name="test-bucket",
            bucket_id="test123",
        )
        
        self.validation_rules = {
            "allowed_types": ["image/jpeg", "image/png", "image/webp"],
            "max_file_size_mb": 20,
            "max_total_size_mb": 200,
            "min_files": 5,
            "max_files": 15,
        }
    
    def _create_mock_file(self, size_mb: int, name: str):
        """Create a mock file-like object."""
        size_bytes = size_mb * 1024 * 1024
        file_data = io.BytesIO(b"0" * size_bytes)
        return file_data, name
    
    def test_valid_file_count_within_range(self):
        """Test that 5-15 files pass validation."""
        # Create 7 files (within range)
        files = [
            self._create_mock_file(5, f"photo{i}.jpg")
            for i in range(7)
        ]
        
        _, errors = self.service.batch_upload_files(
            files, "test_session/20231201", self.validation_rules
        )
        
        # Should not have count-related errors
        count_errors = [e for e in errors if "at least 5" in e or "at most 15" in e]
        assert len(count_errors) == 0, "No count-related errors expected for 7 files"
    
    def test_too_few_files(self):
        """Test that <5 files fails validation."""
        # Create 3 files (below minimum)
        files = [
            self._create_mock_file(5, f"photo{i}.jpg")
            for i in range(3)
        ]
        
        _, errors = self.service.batch_upload_files(
            files, "test_session/20231201", self.validation_rules
        )
        
        assert len(errors) > 0
        assert any("at least 5" in e for e in errors)
    
    def test_too_many_files(self):
        """Test that >15 files fails validation."""
        # Create 18 files (above maximum)
        files = [
            self._create_mock_file(5, f"photo{i}.jpg")
            for i in range(18)
        ]
        
        _, errors = self.service.batch_upload_files(
            files, "test_session/20231201", self.validation_rules
        )
        
        assert len(errors) > 0
        assert any("at most 15" in e for e in errors)
    
    def test_total_size_within_limit(self):
        """Test that total size under 200MB passes."""
        # Create 10 files, each 15MB = 150MB total (under limit)
        files = [
            self._create_mock_file(15, f"photo{i}.jpg")
            for i in range(10)
        ]
        
        _, errors = self.service.batch_upload_files(
            files, "test_session/20231201", self.validation_rules
        )
        
        # Should not have size-related errors (may have network errors since mocking)
        size_errors = [e for e in errors if "200MB" in e and "total" in e.lower()]
        assert len(size_errors) == 0, "No total size errors expected for 150MB"
    
    def test_total_size_exceeds_limit(self):
        """Test that total size over 200MB fails."""
        # Create 15 files, each 15MB = 225MB total (over limit)
        files = [
            self._create_mock_file(15, f"photo{i}.jpg")
            for i in range(15)
        ]
        
        _, errors = self.service.batch_upload_files(
            files, "test_session/20231201", self.validation_rules
        )
        
        assert len(errors) > 0
        assert any("200MB" in e and "total" in e.lower() for e in errors)
    
    def test_mixed_valid_and_invalid_files(self):
        """Test that invalid files are caught and reported."""
        files = [
            self._create_mock_file(5, "photo1.jpg"),
            self._create_mock_file(5, "photo2.png"),
            self._create_mock_file(25, "too_large.jpg"),  # Over 20MB
            self._create_mock_file(5, "photo3.webp"),
            self._create_mock_file(5, "document.pdf"),  # Wrong type
            self._create_mock_file(5, "photo4.jpg"),
        ]
        
        _, errors = self.service.batch_upload_files(
            files, "test_session/20231201", self.validation_rules
        )
        
        # Should have errors for oversized file and PDF
        assert len(errors) >= 2
        assert any("too_large.jpg" in e and "20MB" in e for e in errors)
        # PDF error message contains mime type, not filename
        assert any("application/pdf" in e.lower() and "not allowed" in e.lower() for e in errors)

