"""
Unit tests for data export module
"""
import unittest
import json
import csv
import tempfile
import os
from pathlib import Path

from core.data_exporter import DataExporter
from core.pose_detector import PoseFrame, PoseLandmark

class TestDataExporter(unittest.TestCase):
    """Test cases for DataExporter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.exporter = DataExporter()
        
        # Create test pose data
        self.test_landmarks = [
            PoseLandmark(320.0, 240.0, -50.0, 0.95, "NOSE", 0),
            PoseLandmark(310.0, 230.0, -48.0, 0.90, "LEFT_EYE", 0),
            PoseLandmark(330.0, 230.0, -48.0, 0.92, "RIGHT_EYE", 0),
        ]
        
        self.test_pose_sequence = [
            PoseFrame(0, 0.0, self.test_landmarks, 640, 480, 0.92),
            PoseFrame(1, 0.033, self.test_landmarks, 640, 480, 0.94),
            PoseFrame(2, 0.066, self.test_landmarks, 640, 480, 0.91),
        ]
    
    def test_export_to_json(self):
        """Test JSON export functionality"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Test export
            success = self.exporter.export_to_json(self.test_pose_sequence, temp_path)
            self.assertTrue(success)
            
            # Verify file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Verify JSON content
            with open(temp_path, 'r') as f:
                data = json.load(f)
            
            self.assertEqual(data['format_version'], '1.0')
            self.assertEqual(data['total_frames'], 3)
            self.assertEqual(len(data['pose_data']), 3)
            
            # Check first frame data
            first_frame = data['pose_data'][0]
            self.assertEqual(first_frame['frame_index'], 0)
            self.assertEqual(first_frame['timestamp'], 0.0)
            self.assertEqual(len(first_frame['landmarks']), 3)
            
            # Check first landmark
            first_landmark = first_frame['landmarks'][0]
            self.assertEqual(first_landmark['name'], 'NOSE')
            self.assertEqual(first_landmark['x'], 320.0)
            self.assertEqual(first_landmark['y'], 240.0)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_to_csv_wide(self):
        """Test CSV export in wide format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            # Test export
            success = self.exporter.export_to_csv(self.test_pose_sequence, temp_path, 'wide')
            self.assertTrue(success)
            
            # Verify file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Verify CSV content
            with open(temp_path, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # Check header
            header = rows[0]
            self.assertIn('frame_index', header)
            self.assertIn('timestamp', header)
            self.assertIn('NOSE_x', header)
            self.assertIn('NOSE_y', header)
            self.assertIn('NOSE_z', header)
            self.assertIn('NOSE_visibility', header)
            
            # Check data rows
            self.assertEqual(len(rows), 4)  # Header + 3 data rows
            
            # Check first data row
            first_row = rows[1]
            self.assertEqual(first_row[0], '0')  # frame_index
            self.assertEqual(first_row[1], '0.0')  # timestamp
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_to_csv_long(self):
        """Test CSV export in long format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            # Test export
            success = self.exporter.export_to_csv(self.test_pose_sequence, temp_path, 'long')
            self.assertTrue(success)
            
            # Verify file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Verify CSV content
            with open(temp_path, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # Check header
            header = rows[0]
            expected_header = ['frame_index', 'timestamp', 'detection_confidence', 
                             'landmark_name', 'x', 'y', 'z', 'visibility']
            self.assertEqual(header, expected_header)
            
            # Check data rows (3 frames * 3 landmarks = 9 rows + header)
            self.assertEqual(len(rows), 10)
            
            # Check first data row
            first_row = rows[1]
            self.assertEqual(first_row[0], '0')  # frame_index
            self.assertEqual(first_row[3], 'NOSE')  # landmark_name
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_for_blender(self):
        """Test Blender export functionality"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Test export
            success = self.exporter.export_for_blender(self.test_pose_sequence, temp_path)
            self.assertTrue(success)
            
            # Verify file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Verify JSON content
            with open(temp_path, 'r') as f:
                data = json.load(f)
            
            self.assertEqual(data['format'], 'blender_pose_data')
            self.assertEqual(data['version'], '1.0')
            self.assertIn('bone_mapping', data)
            self.assertIn('animation_data', data)
            
            # Check animation data
            self.assertEqual(len(data['animation_data']), 3)
            
            # Check first frame
            first_frame = data['animation_data'][0]
            self.assertEqual(first_frame['frame'], 1)  # Blender frames start at 1
            self.assertIn('bones', first_frame)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_summary_stats(self):
        """Test summary statistics export"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Test export
            success = self.exporter.export_summary_stats(self.test_pose_sequence, temp_path)
            self.assertTrue(success)
            
            # Verify file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Verify JSON content
            with open(temp_path, 'r') as f:
                data = json.load(f)
            
            self.assertIn('general', data)
            self.assertIn('confidence', data)
            self.assertIn('landmarks', data)
            
            # Check general stats
            general = data['general']
            self.assertEqual(general['total_frames'], 3)
            
            # Check confidence stats
            confidence = data['confidence']
            self.assertIn('mean', confidence)
            self.assertIn('std', confidence)
            self.assertIn('min', confidence)
            self.assertIn('max', confidence)
            
            # Check landmark stats
            landmarks = data['landmarks']
            self.assertIn('NOSE', landmarks)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_load_from_json(self):
        """Test loading pose data from JSON"""
        # First export data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Export test data
            self.exporter.export_to_json(self.test_pose_sequence, temp_path)
            
            # Load data back
            loaded_sequence = self.exporter.load_from_json(temp_path)
            
            self.assertIsNotNone(loaded_sequence)
            self.assertEqual(len(loaded_sequence), 3)
            
            # Check first frame
            first_frame = loaded_sequence[0]
            self.assertEqual(first_frame.frame_index, 0)
            self.assertEqual(first_frame.timestamp, 0.0)
            self.assertEqual(len(first_frame.landmarks), 3)
            
            # Check first landmark
            first_landmark = first_frame.landmarks[0]
            self.assertEqual(first_landmark.name, 'NOSE')
            self.assertEqual(first_landmark.x, 320.0)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_empty_sequence(self):
        """Test exporting empty pose sequence"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Test export with empty sequence
            success = self.exporter.export_to_json([], temp_path)
            self.assertTrue(success)
            
            # Verify content
            with open(temp_path, 'r') as f:
                data = json.load(f)
            
            self.assertEqual(data['total_frames'], 0)
            self.assertEqual(len(data['pose_data']), 0)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_invalid_file_path(self):
        """Test export with invalid file path"""
        invalid_path = "/invalid/path/that/does/not/exist.json"
        success = self.exporter.export_to_json(self.test_pose_sequence, invalid_path)
        self.assertFalse(success)

if __name__ == '__main__':
    unittest.main()