# Introduction
Point cloud renderer aims to render points which either loaded from a file or generated in place. 
This is an alternative to [Point Cloud Visualizer](https://github.com/uhlik/bpy), but more efficient and scalable. Scripts are polished
so that readability is promised. 
# Usage
point_cloud_maker.py alone can be used to render your point clouds. If you need to grab
an intuition about the usage, follow the steps below.
## Dependencies
- Install [Blender](https://blender.org/download) v2.8x.
- Install `pillow` & `h5py` into ***the Blender's Python interpreter***. Please follow this [thread](https://blender.stackexchange.com/a/56013)
if you are not familiar with Python package management of Blender.
This step can be skipped if there is no need to try `render_and_concat.py`.
## Demos
Please note that the default up direction of camera is along positive y. Feel free to change the blender file `render_demo.blend`.
- `blender -b render_demo.blend -P render_single_pcd.py` This command start a blender process that renders point clouds loaded from an ascii file.
- `blender -b render_demo.blend -P render_and_concat.py` This command start a blender process that renders several images containing
point clouds and concat them together. A mesh is loaded as a reference and points are all loaded from an h5 file and transformed accordingly. This script
is derived from a gallery renderer of our paper (Coming soon...). The original one renders batch of images, so you can see
a loop is maintained in the script. It is straightforward to modify this script and your h5 file to enable large batch rendering. 

![alt text](images/gallery.png?raw=true)
