# Workplane

A small addon which adds a workplane like tool to blender.

The main idea is that it allows for quickly setting up a custom transform orientation, which is used for finding the major two axis the user is viewing - these can then be used as constraints for translate/rotate/scale operations without the need to type it in manually. So for example instead of "g" "Shift-Y" "Shift-Y" you can just do that with on command.

## Installation
Just enable the addon under 3D View > Workplane

![enable_addon](https://github.com/BenjaminSauder/Workplane/blob/master/doc/enable_addon.png)

The tools itself is under 3D View > Sidebar Tools > Workplane
![tool_bar](https://github.com/BenjaminSauder/Workplane/blob/master/doc/tool_bar.png)

## Usage
Just select something, and hit "set workplane" - a grid will show up, its a visualisation on what plane you would work on if you would start an transform operation.

![overview](https://github.com/BenjaminSauder/Workplane/blob/master/doc/overview.png)

Observe how the workplane adapts to the view
![view_adapt](https://github.com/BenjaminSauder/Workplane/blob/master/doc/view_adapt.png)

