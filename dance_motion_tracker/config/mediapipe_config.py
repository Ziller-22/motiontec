"""
MediaPipe configuration and pose landmark definitions
"""

# MediaPipe Pose landmark indices and names
POSE_LANDMARKS = {
    # Face
    'NOSE': 0,
    'LEFT_EYE_INNER': 1,
    'LEFT_EYE': 2,
    'LEFT_EYE_OUTER': 3,
    'RIGHT_EYE_INNER': 4,
    'RIGHT_EYE': 5,
    'RIGHT_EYE_OUTER': 6,
    'LEFT_EAR': 7,
    'RIGHT_EAR': 8,
    'MOUTH_LEFT': 9,
    'MOUTH_RIGHT': 10,
    
    # Upper body
    'LEFT_SHOULDER': 11,
    'RIGHT_SHOULDER': 12,
    'LEFT_ELBOW': 13,
    'RIGHT_ELBOW': 14,
    'LEFT_WRIST': 15,
    'RIGHT_WRIST': 16,
    
    # Hands
    'LEFT_PINKY': 17,
    'RIGHT_PINKY': 18,
    'LEFT_INDEX': 19,
    'RIGHT_INDEX': 20,
    'LEFT_THUMB': 21,
    'RIGHT_THUMB': 22,
    
    # Lower body
    'LEFT_HIP': 23,
    'RIGHT_HIP': 24,
    'LEFT_KNEE': 25,
    'RIGHT_KNEE': 26,
    'LEFT_ANKLE': 27,
    'RIGHT_ANKLE': 28,
    'LEFT_HEEL': 29,
    'RIGHT_HEEL': 30,
    'LEFT_FOOT_INDEX': 31,
    'RIGHT_FOOT_INDEX': 32
}

# Pose connections for visualization
POSE_CONNECTIONS = [
    # Face
    ('NOSE', 'LEFT_EYE_INNER'),
    ('LEFT_EYE_INNER', 'LEFT_EYE'),
    ('LEFT_EYE', 'LEFT_EYE_OUTER'),
    ('LEFT_EYE_OUTER', 'LEFT_EAR'),
    ('NOSE', 'RIGHT_EYE_INNER'),
    ('RIGHT_EYE_INNER', 'RIGHT_EYE'),
    ('RIGHT_EYE', 'RIGHT_EYE_OUTER'),
    ('RIGHT_EYE_OUTER', 'RIGHT_EAR'),
    ('MOUTH_LEFT', 'MOUTH_RIGHT'),
    
    # Upper body
    ('LEFT_SHOULDER', 'RIGHT_SHOULDER'),
    ('LEFT_SHOULDER', 'LEFT_ELBOW'),
    ('LEFT_ELBOW', 'LEFT_WRIST'),
    ('RIGHT_SHOULDER', 'RIGHT_ELBOW'),
    ('RIGHT_ELBOW', 'RIGHT_WRIST'),
    
    # Hands
    ('LEFT_WRIST', 'LEFT_PINKY'),
    ('LEFT_WRIST', 'LEFT_INDEX'),
    ('LEFT_WRIST', 'LEFT_THUMB'),
    ('RIGHT_WRIST', 'RIGHT_PINKY'),
    ('RIGHT_WRIST', 'RIGHT_INDEX'),
    ('RIGHT_WRIST', 'RIGHT_THUMB'),
    
    # Torso
    ('LEFT_SHOULDER', 'LEFT_HIP'),
    ('RIGHT_SHOULDER', 'RIGHT_HIP'),
    ('LEFT_HIP', 'RIGHT_HIP'),
    
    # Lower body
    ('LEFT_HIP', 'LEFT_KNEE'),
    ('LEFT_KNEE', 'LEFT_ANKLE'),
    ('LEFT_ANKLE', 'LEFT_HEEL'),
    ('LEFT_ANKLE', 'LEFT_FOOT_INDEX'),
    ('RIGHT_HIP', 'RIGHT_KNEE'),
    ('RIGHT_KNEE', 'RIGHT_ANKLE'),
    ('RIGHT_ANKLE', 'RIGHT_HEEL'),
    ('RIGHT_ANKLE', 'RIGHT_FOOT_INDEX'),
]

# Landmark groups for different body parts
LANDMARK_GROUPS = {
    'face': ['NOSE', 'LEFT_EYE_INNER', 'LEFT_EYE', 'LEFT_EYE_OUTER', 'RIGHT_EYE_INNER', 
             'RIGHT_EYE', 'RIGHT_EYE_OUTER', 'LEFT_EAR', 'RIGHT_EAR', 'MOUTH_LEFT', 'MOUTH_RIGHT'],
    'upper_body': ['LEFT_SHOULDER', 'RIGHT_SHOULDER', 'LEFT_ELBOW', 'RIGHT_ELBOW', 
                   'LEFT_WRIST', 'RIGHT_WRIST'],
    'hands': ['LEFT_PINKY', 'RIGHT_PINKY', 'LEFT_INDEX', 'RIGHT_INDEX', 'LEFT_THUMB', 'RIGHT_THUMB'],
    'lower_body': ['LEFT_HIP', 'RIGHT_HIP', 'LEFT_KNEE', 'RIGHT_KNEE', 'LEFT_ANKLE', 
                   'RIGHT_ANKLE', 'LEFT_HEEL', 'RIGHT_HEEL', 'LEFT_FOOT_INDEX', 'RIGHT_FOOT_INDEX']
}

# MediaPipe model configuration
MEDIAPIPE_CONFIG = {
    'model_complexity': 1,  # 0, 1, or 2 (higher = more accurate but slower)
    'min_detection_confidence': 0.5,
    'min_tracking_confidence': 0.5,
    'enable_segmentation': False,  # Set to True if you want background segmentation
    'smooth_landmarks': True,
    'smooth_segmentation': True,
}

# Visualization colors (BGR format for OpenCV)
VISUALIZATION_COLORS = {
    'joint': (0, 255, 0),        # Green for joints
    'connection': (255, 0, 0),    # Blue for connections
    'face': (0, 255, 255),        # Yellow for face landmarks
    'hands': (255, 0, 255),       # Magenta for hands
    'background': (0, 0, 0),      # Black background
}

# Blender bone mapping (maps MediaPipe landmarks to common rig bone names)
BLENDER_BONE_MAPPING = {
    'HEAD': 'NOSE',
    'NECK': 'NOSE',  # Approximation
    'SPINE_UPPER': 'LEFT_SHOULDER',  # Midpoint between shoulders
    'SPINE_LOWER': 'LEFT_HIP',       # Midpoint between hips
    'LEFT_SHOULDER': 'LEFT_SHOULDER',
    'RIGHT_SHOULDER': 'RIGHT_SHOULDER',
    'LEFT_ARM_UPPER': 'LEFT_ELBOW',
    'RIGHT_ARM_UPPER': 'RIGHT_ELBOW',
    'LEFT_ARM_LOWER': 'LEFT_WRIST',
    'RIGHT_ARM_LOWER': 'RIGHT_WRIST',
    'LEFT_HAND': 'LEFT_WRIST',
    'RIGHT_HAND': 'RIGHT_WRIST',
    'LEFT_LEG_UPPER': 'LEFT_KNEE',
    'RIGHT_LEG_UPPER': 'RIGHT_KNEE',
    'LEFT_LEG_LOWER': 'LEFT_ANKLE',
    'RIGHT_LEG_LOWER': 'RIGHT_ANKLE',
    'LEFT_FOOT': 'LEFT_FOOT_INDEX',
    'RIGHT_FOOT': 'RIGHT_FOOT_INDEX',
}