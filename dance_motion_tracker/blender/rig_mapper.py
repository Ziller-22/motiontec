"""
Rig mapping utilities for different character rigs in Blender
Maps MediaPipe pose landmarks to various rig bone structures
"""
import bpy
import mathutils
from mathutils import Vector, Matrix, Euler
from typing import Dict, List, Tuple, Optional, Any
import json

class RigMapper:
    """
    Maps pose data to different rig types and bone naming conventions
    """
    
    def __init__(self):
        self.rig_mappings = {
            'mixamo': self.get_mixamo_mapping(),
            'rigify': self.get_rigify_mapping(),
            'ue4': self.get_ue4_mapping(),
            'generic': self.get_generic_mapping()
        }
    
    def get_mixamo_mapping(self) -> Dict[str, str]:
        """Mixamo rig bone mapping"""
        return {
            # Head and neck
            'HEAD': 'Head',
            'NECK': 'Neck',
            
            # Spine
            'SPINE_UPPER': 'Spine2',
            'SPINE_LOWER': 'Spine1',
            'HIPS': 'Hips',
            
            # Left arm
            'LEFT_SHOULDER': 'LeftShoulder',
            'LEFT_ARM_UPPER': 'LeftArm',
            'LEFT_ARM_LOWER': 'LeftForeArm',
            'LEFT_HAND': 'LeftHand',
            
            # Right arm
            'RIGHT_SHOULDER': 'RightShoulder',
            'RIGHT_ARM_UPPER': 'RightArm',
            'RIGHT_ARM_LOWER': 'RightForeArm',
            'RIGHT_HAND': 'RightHand',
            
            # Left leg
            'LEFT_LEG_UPPER': 'LeftUpLeg',
            'LEFT_LEG_LOWER': 'LeftLeg',
            'LEFT_FOOT': 'LeftFoot',
            
            # Right leg
            'RIGHT_LEG_UPPER': 'RightUpLeg',
            'RIGHT_LEG_LOWER': 'RightLeg',
            'RIGHT_FOOT': 'RightFoot',
        }
    
    def get_rigify_mapping(self) -> Dict[str, str]:
        """Rigify rig bone mapping"""
        return {
            # Head and neck
            'HEAD': 'head',
            'NECK': 'neck',
            
            # Spine
            'SPINE_UPPER': 'spine.003',
            'SPINE_LOWER': 'spine.001',
            'HIPS': 'spine',
            
            # Left arm
            'LEFT_SHOULDER': 'shoulder.L',
            'LEFT_ARM_UPPER': 'upper_arm.L',
            'LEFT_ARM_LOWER': 'forearm.L',
            'LEFT_HAND': 'hand.L',
            
            # Right arm
            'RIGHT_SHOULDER': 'shoulder.R',
            'RIGHT_ARM_UPPER': 'upper_arm.R',
            'RIGHT_ARM_LOWER': 'forearm.R',
            'RIGHT_HAND': 'hand.R',
            
            # Left leg
            'LEFT_LEG_UPPER': 'thigh.L',
            'LEFT_LEG_LOWER': 'shin.L',
            'LEFT_FOOT': 'foot.L',
            
            # Right leg
            'RIGHT_LEG_UPPER': 'thigh.R',
            'RIGHT_LEG_LOWER': 'shin.R',
            'RIGHT_FOOT': 'foot.R',
        }
    
    def get_ue4_mapping(self) -> Dict[str, str]:
        """Unreal Engine 4 rig bone mapping"""
        return {
            # Head and neck
            'HEAD': 'head',
            'NECK': 'neck_01',
            
            # Spine
            'SPINE_UPPER': 'spine_03',
            'SPINE_LOWER': 'spine_01',
            'HIPS': 'pelvis',
            
            # Left arm
            'LEFT_SHOULDER': 'clavicle_l',
            'LEFT_ARM_UPPER': 'upperarm_l',
            'LEFT_ARM_LOWER': 'lowerarm_l',
            'LEFT_HAND': 'hand_l',
            
            # Right arm
            'RIGHT_SHOULDER': 'clavicle_r',
            'RIGHT_ARM_UPPER': 'upperarm_r',
            'RIGHT_ARM_LOWER': 'lowerarm_r',
            'RIGHT_HAND': 'hand_r',
            
            # Left leg
            'LEFT_LEG_UPPER': 'thigh_l',
            'LEFT_LEG_LOWER': 'calf_l',
            'LEFT_FOOT': 'foot_l',
            
            # Right leg
            'RIGHT_LEG_UPPER': 'thigh_r',
            'RIGHT_LEG_LOWER': 'calf_r',
            'RIGHT_FOOT': 'foot_r',
        }
    
    def get_generic_mapping(self) -> Dict[str, str]:
        """Generic rig bone mapping"""
        return {
            'HEAD': 'Head',
            'NECK': 'Neck',
            'SPINE_UPPER': 'Spine_Upper',
            'SPINE_LOWER': 'Spine_Lower',
            'HIPS': 'Hips',
            'LEFT_SHOULDER': 'Left_Shoulder',
            'LEFT_ARM_UPPER': 'Left_Upper_Arm',
            'LEFT_ARM_LOWER': 'Left_Lower_Arm',
            'LEFT_HAND': 'Left_Hand',
            'RIGHT_SHOULDER': 'Right_Shoulder',
            'RIGHT_ARM_UPPER': 'Right_Upper_Arm',
            'RIGHT_ARM_LOWER': 'Right_Lower_Arm',
            'RIGHT_HAND': 'Right_Hand',
            'LEFT_LEG_UPPER': 'Left_Upper_Leg',
            'LEFT_LEG_LOWER': 'Left_Lower_Leg',
            'LEFT_FOOT': 'Left_Foot',
            'RIGHT_LEG_UPPER': 'Right_Upper_Leg',
            'RIGHT_LEG_LOWER': 'Right_Lower_Leg',
            'RIGHT_FOOT': 'Right_Foot',
        }
    
    def detect_rig_type(self, armature_obj: bpy.types.Object) -> str:
        """
        Automatically detect rig type based on bone names
        
        Args:
            armature_obj: Armature object to analyze
            
        Returns:
            Detected rig type string
        """
        if not armature_obj or armature_obj.type != 'ARMATURE':
            return 'generic'
        
        bone_names = [bone.name for bone in armature_obj.data.bones]
        
        # Check for Mixamo bones
        mixamo_indicators = ['Head', 'Neck', 'Spine1', 'Spine2', 'LeftArm', 'RightArm']
        if any(bone in bone_names for bone in mixamo_indicators):
            return 'mixamo'
        
        # Check for Rigify bones
        rigify_indicators = ['head', 'neck', 'spine.001', 'upper_arm.L', 'upper_arm.R']
        if any(bone in bone_names for bone in rigify_indicators):
            return 'rigify'
        
        # Check for UE4 bones
        ue4_indicators = ['head', 'neck_01', 'spine_01', 'upperarm_l', 'upperarm_r']
        if any(bone in bone_names for bone in ue4_indicators):
            return 'ue4'
        
        return 'generic'
    
    def get_bone_mapping(self, rig_type: str) -> Dict[str, str]:
        """
        Get bone mapping for specified rig type
        
        Args:
            rig_type: Type of rig ('mixamo', 'rigify', 'ue4', 'generic')
            
        Returns:
            Dictionary mapping pose bones to rig bones
        """
        return self.rig_mappings.get(rig_type, self.rig_mappings['generic'])
    
    def map_pose_to_rig(self, pose_data: Dict[str, Any], armature_obj: bpy.types.Object, 
                       rig_type: Optional[str] = None) -> bool:
        """
        Map pose data to rig bones and apply animation
        
        Args:
            pose_data: Pose data dictionary
            armature_obj: Target armature object
            rig_type: Rig type (auto-detected if None)
            
        Returns:
            True if mapping successful
        """
        if not armature_obj or armature_obj.type != 'ARMATURE':
            print("Invalid armature object")
            return False
        
        # Auto-detect rig type if not specified
        if rig_type is None:
            rig_type = self.detect_rig_type(armature_obj)
        
        bone_mapping = self.get_bone_mapping(rig_type)
        
        print(f"Mapping pose data to {rig_type} rig")
        
        # Set up scene
        scene = bpy.context.scene
        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='POSE')
        
        # Clear existing animation
        if armature_obj.animation_data:
            armature_obj.animation_data_clear()
        
        # Process animation frames
        animation_data = pose_data.get('animation_data', [])
        
        for frame_data in animation_data:
            frame_number = frame_data.get('frame', 1)
            scene.frame_set(frame_number)
            
            bones_data = frame_data.get('bones', {})
            
            # Apply transformations to mapped bones
            for pose_bone_name, rig_bone_name in bone_mapping.items():
                if pose_bone_name in bones_data:
                    pose_bone_data = bones_data[pose_bone_name]
                    rig_bone = armature_obj.pose.bones.get(rig_bone_name)
                    
                    if rig_bone and pose_bone_data.get('visibility', 0) > 0.5:
                        # Apply transformations
                        self.apply_bone_transform(rig_bone, pose_bone_data, rig_type)
                        
                        # Insert keyframes
                        rig_bone.keyframe_insert(data_path="location")
                        rig_bone.keyframe_insert(data_path="rotation_euler")
                        rig_bone.keyframe_insert(data_path="scale")
        
        bpy.ops.object.mode_set(mode='OBJECT')
        print(f"Applied {len(animation_data)} frames of animation")
        return True
    
    def apply_bone_transform(self, bone: bpy.types.PoseBone, 
                           bone_data: Dict[str, Any], rig_type: str):
        """
        Apply transformation data to a pose bone
        
        Args:
            bone: Pose bone to transform
            bone_data: Bone transformation data
            rig_type: Type of rig for coordinate system adjustments
        """
        # Get transformation data
        location = bone_data.get('location', [0, 0, 0])
        rotation = bone_data.get('rotation', [0, 0, 0])
        scale = bone_data.get('scale', [1, 1, 1])
        
        # Apply coordinate system conversion based on rig type
        if rig_type == 'mixamo':
            # Mixamo uses Y-up, Z-forward
            converted_location = [location[0], -location[2], location[1]]
        elif rig_type == 'ue4':
            # UE4 uses Z-up, X-forward
            converted_location = [location[1], location[0], location[2]]
        else:
            # Default: use as-is
            converted_location = location
        
        # Apply transformations
        bone.location = Vector(converted_location)
        bone.rotation_euler = Euler(rotation)
        bone.scale = Vector(scale)
    
    def create_retarget_constraints(self, source_armature: bpy.types.Object, 
                                   target_armature: bpy.types.Object, 
                                   rig_type: str) -> bool:
        """
        Create constraints to retarget animation from source to target rig
        
        Args:
            source_armature: Source armature with animation
            target_armature: Target armature to receive animation
            rig_type: Target rig type
            
        Returns:
            True if constraints created successfully
        """
        bone_mapping = self.get_bone_mapping(rig_type)
        
        # Set target as active
        bpy.context.view_layer.objects.active = target_armature
        bpy.ops.object.mode_set(mode='POSE')
        
        for pose_bone_name, target_bone_name in bone_mapping.items():
            target_bone = target_armature.pose.bones.get(target_bone_name)
            source_bone_name = pose_bone_name  # Assuming source uses pose bone names
            
            if target_bone:
                # Clear existing constraints
                target_bone.constraints.clear()
                
                # Add copy location constraint
                loc_constraint = target_bone.constraints.new('COPY_LOCATION')
                loc_constraint.target = source_armature
                loc_constraint.subtarget = source_bone_name
                
                # Add copy rotation constraint
                rot_constraint = target_bone.constraints.new('COPY_ROTATION')
                rot_constraint.target = source_armature
                rot_constraint.subtarget = source_bone_name
        
        bpy.ops.object.mode_set(mode='OBJECT')
        print(f"Created retarget constraints for {rig_type} rig")
        return True
    
    def bake_retargeted_animation(self, armature_obj: bpy.types.Object, 
                                 frame_start: int, frame_end: int) -> bool:
        """
        Bake constrained animation to keyframes
        
        Args:
            armature_obj: Armature with constraints
            frame_start: Start frame
            frame_end: End frame
            
        Returns:
            True if baking successful
        """
        # Select armature
        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='POSE')
        
        # Select all pose bones
        bpy.ops.pose.select_all(action='SELECT')
        
        # Bake animation
        bpy.ops.nla.bake(
            frame_start=frame_start,
            frame_end=frame_end,
            step=1,
            only_selected=True,
            visual_keying=True,
            clear_constraints=True,
            clear_parents=False,
            use_current_action=True,
            bake_types={'POSE'}
        )
        
        bpy.ops.object.mode_set(mode='OBJECT')
        print(f"Baked animation from frame {frame_start} to {frame_end}")
        return True

# Utility functions for rig mapping
def get_available_rig_types() -> List[str]:
    """Get list of available rig types"""
    return ['mixamo', 'rigify', 'ue4', 'generic']

def create_rig_mapping_file(armature_obj: bpy.types.Object, 
                           output_path: str, 
                           rig_name: str) -> bool:
    """
    Create a custom rig mapping file
    
    Args:
        armature_obj: Armature to analyze
        output_path: Output file path
        rig_name: Name for the rig mapping
        
    Returns:
        True if file created successfully
    """
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return False
    
    bone_names = [bone.name for bone in armature_obj.data.bones]
    
    # Create mapping template
    mapping_template = {
        'rig_name': rig_name,
        'bone_mapping': {},
        'bone_hierarchy': {},
        'coordinate_system': 'blender',  # Y-up, Z-forward
        'scale_factor': 1.0
    }
    
    # Add all bones to mapping (user will need to edit)
    for bone_name in bone_names:
        mapping_template['bone_mapping'][bone_name] = bone_name
    
    try:
        with open(output_path, 'w') as f:
            json.dump(mapping_template, f, indent=2)
        
        print(f"Created rig mapping template: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error creating rig mapping file: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Example of using the rig mapper
    mapper = RigMapper()
    
    # Get active armature
    active_obj = bpy.context.active_object
    if active_obj and active_obj.type == 'ARMATURE':
        rig_type = mapper.detect_rig_type(active_obj)
        print(f"Detected rig type: {rig_type}")
        
        bone_mapping = mapper.get_bone_mapping(rig_type)
        print(f"Bone mapping: {bone_mapping}")
    else:
        print("Please select an armature object")