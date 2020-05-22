# CPE-462 Final Project
## What is this?
- Class Final Project for CPE-462 (S2020)
- Author: PMARINA
- Concept: Quantify camera motion from cameras attached to moving vehicles with the intention of helping solve the problem of drone navigation in GPS-Denied situations. Note that this could be applied to self-driving vehicles relying on cameras, however, the motion tends to occur in different axes. 
- Current status: This has only been tested on a small scale video input with quanitization taking 2-4x longer than realtime. This should be solvable by using high resolution, but lower framerate, depending on the speed. On a small scale with sub-1 m/s velocities at 24 fps, this is accurate to +- 5%. 
## Setup:
- This has only been tested on Windows.
1. Install [Python3](https://www.python.org/downloads/)
2. Get OpenCV with nonfree options. You will most likely need to compile from source:
    - Download the **source code (zip)** from [OpenCV Releases](https://github.com/opencv/opencv/releases)
    - Download the matching version of **source** from [OpenCV_Contrib Releases](https://github.com/opencv/opencv_contrib/releases)
    - Create a folder called **src** and decompress both directories to **src**. 
    - Download & Install [Visual Studio](https://visualstudio.microsoft.com/) (the leftmost option)
    - Download & Install [CMake](https://cmake.org/download/)
    - Restart machine to allow path updates and force updating for all environments
    - Open CMake
        - **Source code**: `path/to/src/opencv-*` (replace `*` with actual version)
        - **Build**: Make a new directory adjacent to src and name it build. Put its path here. 
        - Mark the **grouped** option. 
    - Hit **Configure**. Set compiler to latest version of VisualStudio available. 
    - Modify the parameters that become available:
        - `PYTHON3`: Ensure the paths autodetected are correct. If you have multiple versions of Python, this may not go smoothly. Prioritize the correct version of Python in the order of your PATH variable and try again. 
            - `PYTHON_DEBUG_LIBRARY-NOTFOUND`: Perfectly fine
        - `OPENCV`:
            - `OPENCV_ENABLE_NONFREE`: Enable
            - `OPENCV_EXTRA_MODULES_PATH`: Set to `/path/to/src/opencv_contrib-*/modules` (again, replacing * with version)
    - Hit **Configure**
    - Look at the output:
        - `PYTHON3`: Ensure that all paths match the version of python and install location. If not, modify your path so the correct version of python appears first, reboot, invalidate caches in CMake, and try again. 
        - `OpenCV Modules`: Should have `To be built: Aruco` and many more nonfree packages in the same line that aren't traditionally included with OpenCV. 
        - If anything seems wrong, fix it using a combination of the above parameters and your PATH/environment variables. 
    - While there are red entries, hit **Configure** and take a look at the output every time to ensure the parameters are still correct. 
    - Hit `Generate`
    - Close CMake and open VisualStudio and open solution: `/path/to/build/ALL_BUILD.vcxproj`
    - Near the top of the window, change the version from **Debug** to **Release**, ensuring the correct bit setting is chosen (64-bit should work for most modern non-SBC applications). 
    - Open **CMake Targets** in the **Solution Explorer** (panel on the right side)
    - Right click **ALL_BUILD** and hit build. This will take ~30 minutes. 
    - Right click **INSTALL** and hit build. This will install the OpenCV to the correct locations. 
    - Open your python interpreter: 
        - `import cv2`: failure indicates improper installation/build of the OpenCV package. 
        - `cv2.xfeatures2d.SIFT_create()`: failure indicates improper build of the contrib/nonfree features. 
        - If either of these steps fail, you need to restart from the point where we open CMake, hit File>>clear cache.
            - Checking certain options has tended to break the install for me (opengl)
    - Close all tools. Do NOT delete the build directory. There seem to be dependencies in there that I'm not sure how to separate from the actual build files. This is something that should be addressed; however, as the build files on my machine took upwards of 30 GB. 
## Running:
- Look at the variables defined in `Main.py` and update variables according to your inputs. 
