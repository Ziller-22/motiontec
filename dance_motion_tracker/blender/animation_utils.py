"""
Animation utilities and helper functions for Blender integration
"""
import bpy
import bmesh
import mathutils
from mathutils import Vector, Matrix, Euler, Quaternion
from typing import List, Dict, Tuple, Optional, Any
import math

class AnimationUtils:
    """
    Utility functions for animation processing and enhancement
    """
    
    @staticmethod
    def smooth_keyframes(armature_obj: bpy.types.Object, 
                        frame_start: int, 
                        frame_end: int,
                        smoothing_factor: float = 0.5) -> bool:
        """
        Apply smoothing to keyframes in animation
        
        Args:
            armature_obj: Armature with animation
            frame_start: Start frame
            frame_end: End frame
            smoothing_factor: Smoothing strength (0.0 to 1.0)
            
        Returns:
            True if smoothing applied successfully
        """
        if not armature_obj or armature_obj.type != 'ARMATURE':
            return False
        
        # Set active object
        bpy.context.view_layer.objects.active = armature_obj
        
        # Enter Graph Editor context
        for area in bpy.context.screen.areas:
            if area.type == 'GRAPH_EDITOR':
                with bpy.context.temp_override(area=area):
                    # Select all keyframes in range
                    bpy.ops.graph.select_all(action='SELECT')
                    
                    # Apply smooth operator
                    bpy.ops.graph.smooth(factor=smoothing_factor)
                    
                    print(f"Applied smoothing with factor {smoothing_factor}")
                    return True
        
        print("Graph Editor not found, smoothing not applied")
        return False
    
    @staticmethod
    def add_noise_to_animation(armature_obj: bpy.types.Object,
                              noise_strength: float = 0.01,
                              frame_start: int = 1,
                              frame_end: int = 250) -> bool:
        """
        Add subtle noise to animation for more natural movement
        
        Args:
            armature_obj: Armature with animation
            noise_strength: Strength of noise to add
            frame_start: Start frame
            frame_end: End frame
            
        Returns:
            True if noise added successfully
        """
        if not armature_obj or armature_obj.type != 'ARMATURE':
            return False
        
        import random
        
        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='POSE')
        
        scene = bpy.context.scene
        
        for frame in range(frame_start, frame_end + 1):
            scene.frame_set(frame)
            
            for bone in armature_obj.pose.bones:
                # Add small random variations
                noise_x = (random.random() - 0.5) * noise_strength
                noise_y = (random.random() - 0.5) * noise_strength
                noise_z = (random.random() - 0.5) * noise_strength
                
                bone.location += Vector((noise_x, noise_y, noise_z))
                bone.keyframe_insert(data_path="location")
        
        bpy.ops.object.mode_set(mode='OBJECT')
        print(f"Added noise to animation (strength: {noise_strength})")
        return True
    
    @staticmethod
    def create_ground_contact_constraints(armature_obj: bpy.types.Object,
                                        foot_bones: List[str],
                                        ground_level: float = 0.0) -> bool:
        """
        Create constraints to prevent feet from going through ground
        
        Args:
            armature_obj: Armature object
            foot_bones: List of foot bone names
            ground_level: Y-coordinate of ground level
            
        Returns:
            True if constraints created successfully
        """
        if not armature_obj or armature_obj.type != 'ARMATURE':
            return False
        
        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='POSE')
        
        for foot_bone_name in foot_bones:
            foot_bone = armature_obj.pose.bones.get(foot_bone_name)
            
            if foot_bone:
                # Add limit location constraint
                limit_constraint = foot_bone.constraints.new('LIMIT_LOCATION')
                limit_constraint.use_min_y = True
                limit_constraint.min_y = ground_level
                limit_constraint.owner_space = 'WORLD'
        
        bpy.ops.object.mode_set(mode='OBJECT')
        print(f"Added ground contact constraints for {len(foot_bones)} foot bones")
        return True
    
    @staticmethod
    def create_look_at_constraint(armature_obj: bpy.types.Object,
                                 bone_name: str,
                                 target_obj: bpy.types.Object) -> bool:
        """
        Create look-at constraint for head/eye tracking
        
        Args:
            armature_obj: Armature object
            bone_name: Name of bone to constrain (usually head)
            target_obj: Target object to look at
            
        Returns:
            True if constraint created successfully
        """
        if not armature_obj or armature_obj.type != 'ARMATURE':
            return False
        
        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='POSE')
        
        bone = armature_obj.pose.bones.get(bone_name)
        
        if bone:
            # Add track to constraint
            track_constraint = bone.constraints.new('TRACK_TO')
            track_constraint.target = target_obj
            track_constraint.track_axis = 'TRACK_Y'
            track_constraint.up_axis = 'UP_Z'
            
            print(f"Added look-at constraint to {bone_name}")
            return True
        
        return False
    
    @staticmethod
    def create_secondary_animation(armature_obj: bpy.types.Object,
                                  bone_patterns: Dict[str, Dict[str, float]]) -> bool:
        """
        Create secondary animation (hair, cloth simulation approximation)
        
        Args:
            armature_obj: Armature object
            bone_patterns: Dictionary of bone patterns and their properties
                          e.g., {'hair_*': {'delay': 2, 'damping': 0.8}}
            
        Returns:
            True if secondary animation created successfully
        """
        if not armature_obj or armature_obj.type != 'ARMATURE':
            return False
        
        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='POSE')
        
        for pattern, properties in bone_patterns.items():
            matching_bones = [bone for bone in armature_obj.pose.bones 
                            if pattern.replace('*', '') in bone.name]
            
            for bone in matching_bones:
                # Add child of constraint with offset
                child_constraint = bone.constraints.new('CHILD_OF')
                child_constraint.target = armature_obj
                
                # Find parent bone
                if bone.parent:
                    child_constraint.subtarget = bone.parent.name
                
                # Apply delay and damping effects
                delay = properties.get('delay', 1)
                damping = properties.get('damping', 0.9)
                
                # This would need more complex implementation for true secondary animation
                print(f"Added secondary animation setup to {bone.name}")
        
        bpy.ops.object.mode_set(mode='OBJECT')
        return True
    
    @staticmethod
    def optimize_keyframes(armature_obj: bpy.types.Object,
                          tolerance: float = 0.01) -> int:
        """
        Remove redundant keyframes to optimize animation
        
        Args:
            armature_obj: Armature with animation
            tolerance: Tolerance for keyframe removal
            
        Returns:
            Number of keyframes removed
        """
        if not armature_obj or not armature_obj.animation_data:
            return 0
        
        action = armature_obj.animation_data.action
        if not action:
            return 0
        
        removed_count = 0
        
        for fcurve in action.fcurves:
            keyframes_to_remove = []
            
            for i in range(1, len(fcurve.keyframe_points) - 1):
                prev_kf = fcurve.keyframe_points[i - 1]
                curr_kf = fcurve.keyframe_points[i]
                next_kf = fcurve.keyframe_points[i + 1]
                
                # Check if current keyframe is redundant
                if abs(curr_kf.co.y - prev_kf.co.y) < tolerance and \
                   abs(curr_kf.co.y - next_kf.co.y) < tolerance:
                    keyframes_to_remove.append(i)
            
            # Remove redundant keyframes (in reverse order)
            for i in reversed(keyframes_to_remove):
                fcurve.keyframe_points.remove(fcurve.keyframe_points[i])
                removed_count += 1
        
        print(f"Removed {removed_count} redundant keyframes")
        return removed_count
    
    @staticmethod
    def create_animation_layers(armature_obj: bpy.types.Object,
                               layer_names: List[str]) -> bool:
        """
        Create NLA animation layers for non-destructive editing
        
        Args:
            armature_obj: Armature object
            layer_names: Names for animation layers
            
        Returns:
            True if layers created successfully
        """
        if not armature_obj or not armature_obj.animation_data:
            return False
        
        # Push current action to NLA stack
        if armature_obj.animation_data.action:
            bpy.ops.nla.actionclip_add(action=armature_obj.animation_data.action.name)
        
        # Create additional layers
        for layer_name in layer_names:
            track = armature_obj.animation_data.nla_tracks.new()
            track.name = layer_name
        
        print(f"Created {len(layer_names)} NLA animation layers")
        return True
    
    @staticmethod
    def export_animation_data(armature_obj: bpy.types.Object,
                             output_path: str,
                             frame_start: int = 1,
                             frame_end: int = 250) -> bool:
        """
        Export animation data to external format
        
        Args:
            armature_obj: Armature with animation
            output_path: Output file path
            frame_start: Start frame
            frame_end: End frame
            
        Returns:
            True if export successful
        """
        if not armature_obj or not armature_obj.animation_data:
            return False
        
        animation_data = {
            'armature_name': armature_obj.name,
            'frame_range': [frame_start, frame_end],
            'bones': {},
            'fps': bpy.context.scene.render.fps
        }
        
        scene = bpy.context.scene
        
        # Sample animation data
        for frame in range(frame_start, frame_end + 1):
            scene.frame_set(frame)
            
            frame_data = {}
            for bone in armature_obj.pose.bones:
                bone_matrix = bone.matrix
                
                frame_data[bone.name] = {
                    'location': list(bone_matrix.translation),
                    'rotation': list(bone_matrix.to_euler()),
                    'scale': list(bone_matrix.to_scale())
                }
            
            animation_data['bones'][frame] = frame_data
        
        # Export to JSON
        import json
        try:
            with open(output_path, 'w') as f:
                json.dump(animation_data, f, indent=2)
            
            print(f"Exported animation data to {output_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting animation: {str(e)}")
            return False
    
    @staticmethod
    def create_pose_library(armature_obj: bpy.types.Object,
                           pose_frames: List[int],
                           library_name: str = "Dance_Poses") -> bool:
        """
        Create pose library from specific frames
        
        Args:
            armature_obj: Armature object
            pose_frames: List of frame numbers to capture as poses
            library_name: Name for the pose library
            
        Returns:
            True if pose library created successfully
        """
        if not armature_obj or armature_obj.type != 'ARMATURE':
            return False
        
        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='POSE')
        
        # Create pose library if it doesn't exist
        if not armature_obj.pose_library:
            bpy.ops.poselib.new()
            armature_obj.pose_library.name = library_name
        
        scene = bpy.context.scene
        
        # Add poses from specified frames
        for i, frame in enumerate(pose_frames):
            scene.frame_set(frame)
            
            # Select all bones
            bpy.ops.pose.select_all(action='SELECT')
            
            # Add pose to library
            bpy.ops.poselib.pose_add(frame=frame, name=f"Pose_{i+1:03d}")
        
        bpy.ops.object.mode_set(mode='OBJECT')
        print(f"Created pose library '{library_name}' with {len(pose_frames)} poses")
        return True

# Utility functions
def get_bone_chain(armature_obj: bpy.types.Object, 
                  start_bone: str, 
                  end_bone: str) -> List[str]:
    """
    Get chain of bones from start to end bone
    
    Args:
        armature_obj: Armature object
        start_bone: Name of start bone
        end_bone: Name of end bone
        
    Returns:
        List of bone names in chain
    """
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return []
    
    chain = []
    current_bone = armature_obj.data.bones.get(end_bone)
    
    while current_bone and current_bone.name != start_bone:
        chain.append(current_bone.name)
        current_bone = current_bone.parent
    
    if current_bone and current_bone.name == start_bone:
        chain.append(start_bone)
        chain.reverse()
    
    return chain

def calculate_bone_length(armature_obj: bpy.types.Object, bone_name: str) -> float:
    """
    Calculate length of a bone
    
    Args:
        armature_obj: Armature object
        bone_name: Name of bone
        
    Returns:
        Length of bone
    """
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return 0.0
    
    bone = armature_obj.data.bones.get(bone_name)
    if bone:
        return bone.length
    
    return 0.0

def create_bone_visualization(armature_obj: bpy.types.Object, 
                             bone_name: str,
                             size: float = 0.1) -> Optional[bpy.types.Object]:
    """
    Create visual representation of a bone
    
    Args:
        armature_obj: Armature object
        bone_name: Name of bone to visualize
        size: Size of visualization
        
    Returns:
        Created visualization object or None
    """
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return None
    
    bone = armature_obj.data.bones.get(bone_name)
    if not bone:
        return None
    
    # Create sphere at bone location
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=size,
        location=armature_obj.matrix_world @ bone.head_local
    )
    
    viz_obj = bpy.context.active_object
    viz_obj.name = f"{bone_name}_viz"
    
    # Create material
    mat = bpy.data.materials.new(name=f"{bone_name}_mat")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 0, 0, 1)  # Red
    viz_obj.data.materials.append(mat)
    
    return viz_obj

# Example usage and testing
if __name__ == "__main__":
    # Example of using animation utilities
    active_obj = bpy.context.active_object
    
    if active_obj and active_obj.type == 'ARMATURE':
        utils = AnimationUtils()
        
        # Smooth animation
        utils.smooth_keyframes(active_obj, 1, 250, 0.3)
        
        # Optimize keyframes
        removed = utils.optimize_keyframes(active_obj, 0.01)
        print(f"Removed {removed} keyframes")
        
        # Create pose library from every 10th frame
        pose_frames = list(range(1, 251, 10))
        utils.create_pose_library(active_obj, pose_frames)
    else:
        print("Please select an armature object")