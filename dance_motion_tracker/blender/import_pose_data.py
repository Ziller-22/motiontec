"""
Blender script to import pose data and animate 3D rigs
Compatible with Blender 3.6+
"""
import bpy
import bmesh
import json
import mathutils
from mathutils import Vector, Euler, Matrix
import os
from typing import Dict, List, Any, Optional

# Blender addon information
bl_info = {
    "name": "Dance Motion Tracker Importer",
    "author": "Dance Motion Tracker",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "File > Import > Dance Motion Data",
    "description": "Import pose tracking data from Dance Motion Tracker",
    "category": "Import-Export",
}

class PoseDataImporter:
    """
    Handles importing pose data into Blender and applying to rigs
    """
    
    def __init__(self):
        self.pose_data = None
        self.bone_mapping = {}
        self.armature = None
        self.frame_start = 1
        self.frame_end = 250
        
    def load_pose_data(self, filepath: str) -> bool:
        """
        Load pose data from JSON file
        
        Args:
            filepath: Path to pose data JSON file
            
        Returns:
            True if loaded successfully
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            if data.get('format') == 'blender_pose_data':
                self.pose_data = data
                self.bone_mapping = data.get('bone_mapping', {})
                
                export_info = data.get('export_info', {})
                self.frame_start = export_info.get('frame_start', 1)
                self.frame_end = export_info.get('frame_end', 250)
                
                print(f"Loaded pose data: {len(data.get('animation_data', []))} frames")
                return True
            else:
                print("Invalid pose data format")
                return False
                
        except Exception as e:
            print(f"Error loading pose data: {str(e)}")
            return False
    
    def find_or_create_armature(self, name: str = "PoseArmature") -> Optional[bpy.types.Object]:
        """
        Find existing armature or create a new one
        
        Args:
            name: Name for the armature
            
        Returns:
            Armature object or None if failed
        """
        # Look for existing armature
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                self.armature = obj
                print(f"Using existing armature: {obj.name}")
                return obj
        
        # Create new armature
        bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
        self.armature = bpy.context.active_object
        self.armature.name = name
        
        # Clear default bone
        bpy.ops.armature.select_all(action='SELECT')
        bpy.ops.armature.delete()
        
        # Create bones based on pose data
        self.create_pose_bones()
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        print(f"Created new armature: {name}")
        return self.armature
    
    def create_pose_bones(self):
        """Create bones for pose landmarks"""
        if not self.pose_data:
            return
        
        # Get first frame to determine bone structure
        animation_data = self.pose_data.get('animation_data', [])
        if not animation_data:
            return
        
        first_frame = animation_data[0]
        bones_data = first_frame.get('bones', {})
        
        # Create bones
        for bone_name, bone_data in bones_data.items():
            if bone_data.get('visibility', 0) > 0.5:  # Only create visible bones
                bone = self.armature.data.edit_bones.new(bone_name)
                
                location = bone_data.get('location', [0, 0, 0])
                bone.head = Vector(location)
                bone.tail = Vector([location[0], location[1], location[2] + 0.1])  # Small tail
        
        # Set up bone hierarchy (simplified)
        self.setup_bone_hierarchy()
    
    def setup_bone_hierarchy(self):
        """Set up parent-child relationships between bones"""
        if not self.armature:
            return
        
        # Define bone hierarchy
        bone_hierarchy = {
            'SPINE_LOWER': 'SPINE_UPPER',
            'SPINE_UPPER': 'NECK',
            'NECK': 'HEAD',
            'LEFT_ARM_UPPER': 'LEFT_SHOULDER',
            'LEFT_ARM_LOWER': 'LEFT_ARM_UPPER',
            'LEFT_HAND': 'LEFT_ARM_LOWER',
            'RIGHT_ARM_UPPER': 'RIGHT_SHOULDER',
            'RIGHT_ARM_LOWER': 'RIGHT_ARM_UPPER',
            'RIGHT_HAND': 'RIGHT_ARM_LOWER',
            'LEFT_LEG_UPPER': 'SPINE_LOWER',
            'LEFT_LEG_LOWER': 'LEFT_LEG_UPPER',
            'LEFT_FOOT': 'LEFT_LEG_LOWER',
            'RIGHT_LEG_UPPER': 'SPINE_LOWER',
            'RIGHT_LEG_LOWER': 'RIGHT_LEG_UPPER',
            'RIGHT_FOOT': 'RIGHT_LEG_LOWER',
        }
        
        edit_bones = self.armature.data.edit_bones
        
        for child_name, parent_name in bone_hierarchy.items():
            child_bone = edit_bones.get(child_name)
            parent_bone = edit_bones.get(parent_name)
            
            if child_bone and parent_bone:
                child_bone.parent = parent_bone
    
    def apply_pose_animation(self) -> bool:
        """
        Apply pose data as keyframe animation
        
        Returns:
            True if animation applied successfully
        """
        if not self.pose_data or not self.armature:
            print("No pose data or armature available")
            return False
        
        # Set frame range
        scene = bpy.context.scene
        scene.frame_start = self.frame_start
        scene.frame_end = self.frame_end
        
        # Switch to pose mode
        bpy.context.view_layer.objects.active = self.armature
        bpy.ops.object.mode_set(mode='POSE')
        
        # Clear existing animation data
        if self.armature.animation_data:
            self.armature.animation_data_clear()
        
        # Apply animation data
        animation_data = self.pose_data.get('animation_data', [])
        
        for frame_data in animation_data:
            frame_number = frame_data.get('frame', 1)
            bones_data = frame_data.get('bones', {})
            
            # Set current frame
            scene.frame_set(frame_number)
            
            # Apply bone transformations
            for bone_name, bone_data in bones_data.items():
                pose_bone = self.armature.pose.bones.get(bone_name)
                
                if pose_bone and bone_data.get('visibility', 0) > 0.5:
                    # Apply location
                    location = bone_data.get('location', [0, 0, 0])
                    pose_bone.location = Vector(location)
                    
                    # Apply rotation (if available)
                    rotation = bone_data.get('rotation', [0, 0, 0])
                    pose_bone.rotation_euler = Euler(rotation)
                    
                    # Apply scale
                    scale = bone_data.get('scale', [1, 1, 1])
                    pose_bone.scale = Vector(scale)
                    
                    # Insert keyframes
                    pose_bone.keyframe_insert(data_path="location")
                    pose_bone.keyframe_insert(data_path="rotation_euler")
                    pose_bone.keyframe_insert(data_path="scale")
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        print(f"Applied animation with {len(animation_data)} keyframes")
        return True
    
    def create_pose_visualization(self) -> Optional[bpy.types.Object]:
        """
        Create a mesh visualization of the pose landmarks
        
        Returns:
            Created mesh object or None if failed
        """
        if not self.pose_data:
            return None
        
        # Create new mesh
        mesh = bpy.data.meshes.new("PoseVisualization")
        obj = bpy.data.objects.new("PoseVisualization", mesh)
        
        # Link to scene
        bpy.context.collection.objects.link(obj)
        
        # Get animation data
        animation_data = self.pose_data.get('animation_data', [])
        if not animation_data:
            return obj
        
        # Create shape keys for each frame
        obj.shape_key_add(name="Basis")
        
        for i, frame_data in enumerate(animation_data):
            frame_number = frame_data.get('frame', i + 1)
            bones_data = frame_data.get('bones', {})
            
            # Create vertices for this frame
            vertices = []
            for bone_name, bone_data in bones_data.items():
                if bone_data.get('visibility', 0) > 0.5:
                    location = bone_data.get('location', [0, 0, 0])
                    vertices.append(location)
            
            if i == 0:
                # Create base mesh
                bm = bmesh.new()
                for vertex in vertices:
                    bm.verts.new(vertex)
                
                # Create edges between related points
                self.create_pose_connections(bm)
                
                bm.to_mesh(mesh)
                bm.free()
            else:
                # Add shape key
                shape_key = obj.shape_key_add(name=f"Frame_{frame_number}")
                
                for j, vertex in enumerate(vertices):
                    if j < len(shape_key.data):
                        shape_key.data[j].co = Vector(vertex)
        
        return obj
    
    def create_pose_connections(self, bm):
        """Create edges between related pose landmarks"""
        # Define connections between landmarks
        connections = [
            # Torso
            (0, 1), (1, 2), (2, 3),  # Spine connections
            # Arms
            (4, 5), (5, 6), (6, 7),  # Left arm
            (8, 9), (9, 10), (10, 11),  # Right arm
            # Legs
            (12, 13), (13, 14), (14, 15),  # Left leg
            (16, 17), (17, 18), (18, 19),  # Right leg
        ]
        
        # Ensure we have enough vertices
        num_verts = len(bm.verts)
        
        for start_idx, end_idx in connections:
            if start_idx < num_verts and end_idx < num_verts:
                try:
                    bm.edges.new([bm.verts[start_idx], bm.verts[end_idx]])
                except ValueError:
                    pass  # Edge already exists
    
    def import_pose_data(self, filepath: str, create_armature: bool = True, 
                        create_visualization: bool = False) -> bool:
        """
        Main import function
        
        Args:
            filepath: Path to pose data file
            create_armature: Whether to create/use armature
            create_visualization: Whether to create mesh visualization
            
        Returns:
            True if import successful
        """
        # Load data
        if not self.load_pose_data(filepath):
            return False
        
        # Create or find armature
        if create_armature:
            if not self.find_or_create_armature():
                print("Failed to create armature")
                return False
            
            # Apply animation
            if not self.apply_pose_animation():
                print("Failed to apply animation")
                return False
        
        # Create visualization
        if create_visualization:
            viz_obj = self.create_pose_visualization()
            if viz_obj:
                print("Created pose visualization")
        
        print("Pose data import completed successfully")
        return True

# Blender operator for importing pose data
class ImportPoseData(bpy.types.Operator):
    """Import Dance Motion Tracker pose data"""
    bl_idname = "import_anim.pose_data"
    bl_label = "Import Pose Data"
    bl_options = {'REGISTER', 'UNDO'}
    
    # File browser properties
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for importing the pose data file",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    
    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255
    )
    
    # Import options
    create_armature: bpy.props.BoolProperty(
        name="Create Armature",
        description="Create armature and apply animation",
        default=True
    )
    
    create_visualization: bpy.props.BoolProperty(
        name="Create Visualization",
        description="Create mesh visualization of pose data",
        default=False
    )
    
    def execute(self, context):
        importer = PoseDataImporter()
        
        if importer.import_pose_data(
            self.filepath, 
            self.create_armature, 
            self.create_visualization
        ):
            self.report({'INFO'}, "Pose data imported successfully")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to import pose data")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Menu function
def menu_func_import(self, context):
    self.layout.operator(ImportPoseData.bl_idname, text="Dance Motion Data (.json)")

# Registration
def register():
    bpy.utils.register_class(ImportPoseData)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportPoseData)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
    
    # Test the operator (uncomment for testing)
    # bpy.ops.import_anim.pose_data('INVOKE_DEFAULT')