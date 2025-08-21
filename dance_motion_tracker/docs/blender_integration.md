# Blender Integration Guide

This guide explains how to use the Dance Motion Tracker data in Blender for 3D character animation.

## Overview

The Blender integration allows you to:
- Import pose tracking data as armature animation
- Retarget motion to different character rigs
- Apply motion to various character types (Mixamo, Rigify, custom rigs)
- Create pose libraries and animation sequences
- Optimize and enhance the imported animation

## Installation

### 1. Install the Blender Addon

1. Open Blender 3.6 or later
2. Go to **Edit → Preferences → Add-ons**
3. Click **Install...** and select `blender/import_pose_data.py`
4. Enable the **"Dance Motion Tracker Importer"** addon
5. The import option will appear in **File → Import → Dance Motion Data**

### 2. Copy Support Scripts

Copy the following files to your Blender scripts directory:
- `blender/rig_mapper.py`
- `blender/animation_utils.py`

**Scripts Directory Locations:**
- **Windows**: `%APPDATA%\Blender Foundation\Blender\3.6\scripts\addons\`
- **macOS**: `~/Library/Application Support/Blender/3.6/scripts/addons/`
- **Linux**: `~/.config/blender/3.6/scripts/addons/`

## Basic Workflow

### 1. Export Data from Dance Motion Tracker

When processing your video, ensure you select **"Blender Compatible"** export format. This creates a JSON file optimized for Blender import.

### 2. Import into Blender

1. Open Blender and create a new scene
2. Go to **File → Import → Dance Motion Data**
3. Select your exported JSON file
4. Configure import options:
   - **Create Armature**: Generate bone structure and animation
   - **Create Visualization**: Add mesh representation of pose data

### 3. Review Imported Animation

- The imported armature will have keyframe animation applied
- Use the timeline to scrub through the motion
- Bones are named according to MediaPipe landmarks
- Animation length matches your video duration

## Working with Character Rigs

### Supported Rig Types

The system supports automatic retargeting to:
- **Mixamo**: Adobe Mixamo character rigs
- **Rigify**: Blender's Rigify addon rigs
- **UE4**: Unreal Engine 4 mannequin rigs
- **Generic**: Custom or unknown rig types

### Automatic Rig Detection

```python
# In Blender's Python console
import bpy
from rig_mapper import RigMapper

# Select your character rig
character_rig = bpy.context.active_object

# Detect rig type
mapper = RigMapper()
rig_type = mapper.detect_rig_type(character_rig)
print(f"Detected rig type: {rig_type}")
```

### Manual Rig Retargeting

#### Step 1: Import Pose Data
1. Import your pose data (creates `PoseArmature`)
2. Load or import your character with rig

#### Step 2: Create Retarget Constraints
```python
import bpy
from rig_mapper import RigMapper

# Get armatures
pose_armature = bpy.data.objects['PoseArmature']
character_rig = bpy.data.objects['YourCharacterRig']

# Create retarget constraints
mapper = RigMapper()
mapper.create_retarget_constraints(pose_armature, character_rig, 'mixamo')
```

#### Step 3: Bake Animation
```python
# Bake the constrained animation to keyframes
mapper.bake_retargeted_animation(character_rig, 1, 250)
```

## Advanced Techniques

### Custom Bone Mapping

For custom rigs, create your own bone mapping:

```python
from rig_mapper import RigMapper

# Create custom mapping
custom_mapping = {
    'HEAD': 'MyRig_Head_Bone',
    'NECK': 'MyRig_Neck_Bone',
    'LEFT_SHOULDER': 'MyRig_L_Shoulder',
    'RIGHT_SHOULDER': 'MyRig_R_Shoulder',
    'LEFT_ARM_UPPER': 'MyRig_L_UpperArm',
    'RIGHT_ARM_UPPER': 'MyRig_R_UpperArm',
    'LEFT_ARM_LOWER': 'MyRig_L_ForeArm',
    'RIGHT_ARM_LOWER': 'MyRig_R_ForeArm',
    'LEFT_HAND': 'MyRig_L_Hand',
    'RIGHT_HAND': 'MyRig_R_Hand',
    'SPINE_UPPER': 'MyRig_Spine_Upper',
    'SPINE_LOWER': 'MyRig_Spine_Lower',
    'LEFT_LEG_UPPER': 'MyRig_L_Thigh',
    'RIGHT_LEG_UPPER': 'MyRig_R_Thigh',
    'LEFT_LEG_LOWER': 'MyRig_L_Shin',
    'RIGHT_LEG_LOWER': 'MyRig_R_Shin',
    'LEFT_FOOT': 'MyRig_L_Foot',
    'RIGHT_FOOT': 'MyRig_R_Foot'
}

# Apply custom mapping
mapper = RigMapper()
mapper.map_pose_to_rig(pose_data, character_armature, custom_mapping)
```

### Animation Enhancement

#### Smooth Keyframes
```python
from animation_utils import AnimationUtils

# Smooth the imported animation
utils = AnimationUtils()
utils.smooth_keyframes(armature, frame_start=1, frame_end=250, smoothing_factor=0.5)
```

#### Add Ground Contact Constraints
```python
# Prevent feet from going through the ground
foot_bones = ['LEFT_FOOT', 'RIGHT_FOOT']
utils.create_ground_contact_constraints(armature, foot_bones, ground_level=0.0)
```

#### Optimize Animation
```python
# Remove redundant keyframes
removed_count = utils.optimize_keyframes(armature, tolerance=0.01)
print(f"Removed {removed_count} redundant keyframes")
```

### Creating Pose Libraries

Create reusable pose libraries from your animation:

```python
# Extract key poses every 10 frames
key_frames = list(range(1, 251, 10))
utils.create_pose_library(armature, key_frames, "Dance_Poses")
```

## Mixamo Character Workflow

### 1. Download Mixamo Character

1. Go to [Adobe Mixamo](https://www.mixamo.com/)
2. Download a character in FBX format
3. Import into Blender (**File → Import → FBX**)

### 2. Prepare Character

```python
# Select the imported character
character = bpy.context.active_object

# The armature is usually named 'Armature' or similar
armature = None
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE' and 'mixamo' in obj.name.lower():
        armature = obj
        break
```

### 3. Apply Dance Motion

```python
# Import pose data and retarget to Mixamo rig
from rig_mapper import RigMapper

pose_armature = bpy.data.objects['PoseArmature']
mixamo_armature = bpy.data.objects['Armature']  # Adjust name as needed

mapper = RigMapper()
mapper.create_retarget_constraints(pose_armature, mixamo_armature, 'mixamo')
mapper.bake_retargeted_animation(mixamo_armature, 1, 250)
```

## Rigify Character Workflow

### 1. Create Rigify Character

1. Add Armature: **Add → Armature → Basic → Human (Meta-Rig)**
2. Adjust bone positions to match your character
3. Generate rig: **Armature Properties → Rigify → Generate Rig**

### 2. Apply Motion to Rigify

```python
# Retarget to Rigify rig
rigify_armature = bpy.data.objects['rig']  # Generated Rigify rig
pose_armature = bpy.data.objects['PoseArmature']

mapper = RigMapper()
mapper.create_retarget_constraints(pose_armature, rigify_armature, 'rigify')
mapper.bake_retargeted_animation(rigify_armature, 1, 250)
```

## Troubleshooting

### Common Issues

#### Import Fails
- **Check Blender Version**: Ensure you're using Blender 3.6+
- **Verify File Format**: Make sure you're importing the Blender-compatible JSON file
- **Check File Path**: Ensure the file path doesn't contain special characters

#### Animation Doesn't Apply
- **Check Armature Selection**: Ensure the correct armature is selected
- **Verify Bone Names**: Check that bone names match the mapping
- **Timeline Range**: Ensure timeline covers the animation range

#### Poor Motion Quality
- **Enable Smoothing**: Use smoothing options during export
- **Adjust Constraints**: Fine-tune constraint settings
- **Manual Cleanup**: Edit keyframes manually for critical poses

### Performance Tips

#### Large Animations
- Process in segments for very long animations
- Reduce keyframe density for less critical sections
- Use NLA editor for managing multiple animation layers

#### Memory Usage
- Clear unused data regularly: **File → Clean Up → All**
- Use proxy objects for heavy scenes
- Consider using linked libraries for character assets

## Advanced Scripting

### Batch Processing Multiple Characters

```python
import bpy
from rig_mapper import RigMapper

# List of character armatures to apply motion to
character_armatures = ['Character1_Armature', 'Character2_Armature']
pose_armature = bpy.data.objects['PoseArmature']

mapper = RigMapper()

for char_name in character_armatures:
    char_armature = bpy.data.objects.get(char_name)
    if char_armature:
        # Detect rig type and apply motion
        rig_type = mapper.detect_rig_type(char_armature)
        mapper.create_retarget_constraints(pose_armature, char_armature, rig_type)
        mapper.bake_retargeted_animation(char_armature, 1, 250)
        print(f"Applied motion to {char_name} ({rig_type} rig)")
```

### Custom Animation Layers

```python
# Create multiple animation layers for different body parts
from animation_utils import AnimationUtils

utils = AnimationUtils()

# Create separate layers
layer_names = ['Base_Motion', 'Upper_Body', 'Lower_Body', 'Hands']
utils.create_animation_layers(armature, layer_names)

# Apply different animations to different layers
# (This would require more complex implementation)
```

### Export Enhanced Animation

```python
# Export the enhanced animation back to external format
utils.export_animation_data(armature, 'enhanced_animation.json', 1, 250)
```

## Integration with Other Software

### Unity Integration

1. Export from Blender as FBX with animation
2. Import into Unity
3. Configure as Humanoid rig in Unity
4. Apply to characters using Unity's animation retargeting

### Unreal Engine Integration

1. Export as FBX from Blender
2. Import into Unreal Engine
3. Retarget to UE4/UE5 mannequin or custom characters
4. Use Control Rig for advanced retargeting

### Motion Capture Software

The exported JSON data can be converted to other motion capture formats:
- BVH (Biovision Hierarchy)
- FBX animation
- Alembic caches

## Best Practices

### Quality Control

1. **Review Import**: Always check the imported animation in Blender
2. **Test Retargeting**: Verify motion looks correct on target character
3. **Manual Refinement**: Adjust key poses manually for better results
4. **Ground Contact**: Ensure feet don't penetrate the ground
5. **Natural Motion**: Add secondary animation for hair, cloth, etc.

### Performance Optimization

1. **Keyframe Reduction**: Remove unnecessary keyframes
2. **Constraint Baking**: Bake constraints to keyframes when done
3. **Layer Organization**: Use animation layers for complex scenes
4. **Proxy Usage**: Use proxy objects for heavy characters

### Workflow Efficiency

1. **Save Templates**: Create template files with common setups
2. **Script Automation**: Automate repetitive tasks with Python scripts
3. **Asset Libraries**: Build libraries of characters and poses
4. **Version Control**: Keep track of different animation versions

## Resources and References

### Blender Documentation
- [Blender Animation Manual](https://docs.blender.org/manual/en/latest/animation/)
- [Rigify Addon Documentation](https://docs.blender.org/manual/en/latest/addons/rigging/rigify/)
- [Python API Reference](https://docs.blender.org/api/current/)

### Community Resources
- Blender Artists Community
- Mixamo Character Downloads
- Free rig collections (Rigify, ManuelBastioni)

### Tutorials
- Character rigging fundamentals
- Animation retargeting techniques
- Python scripting for animation

This integration guide should help you effectively use Dance Motion Tracker data in Blender for professional-quality character animation. For specific questions or advanced techniques, consult the Blender documentation or community forums.