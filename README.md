# ComfyUI-kewky_tools
Dumb shit to make life a lil more comfy

## Tools

1. text_append_node.py
    Appends text to existing text, line by line.
   - Takes two inputs: current_text and append_text
   - Appends each line of append_text to each line of current_text
   - Useful for generating combinations of text or expanding existing text in a structured way
   - Can be used in ComfyUI workflows for text preprocessing or generation tasks
     ![image](https://github.com/KewkLW/ComfyUI-kewky_tools/assets/57611539/c9774759-f1d5-4f38-bc44-4639d7c6762b)
2. vramdebugplus.py
   Monitors and manages VRAM usage.
   - Optionally clears CUDA cache and performs garbage collection
   - Can unload all models to free up VRAM
   - Provides detailed or simple reports on VRAM usage
   - Shows free VRAM before and after operations
   - Offers insights into system RAM usage
   - Useful for optimizing VRAM usage in complex ComfyUI workflows

3. tensordebugplus.py
   This script provides detailed information about tensors and neural network models.
   - Analyzes the structure of tensors, including nested tensors and PyTorch modules
   - Reports shape, data type, device, and memory usage of tensors
   - Optionally includes gradient information and statistical measures (min, max, mean, std)
   - Provides a summary of total parameters and memory usage
   - Useful for debugging and optimizing machine learning models in ComfyUI
	![image](https://github.com/KewkLW/ComfyUI-kewky_tools/assets/57611539/36012f09-d46a-4ec7-9373-5ce596657606)
	
4. animation_schedule_output.py
   Designed to format text input for animation keyframes. 
   - Takes unformatted prompts and formats them with keyframe numbers
   - Allows setting a custom keyframe interval
   - Supports an optional offset for keyframe numbering
   - Outputs formatted text suitable for animation schedules or keyframe-based systems
   - Useful for preparing text inputs for animated or time-based ComfyUI workflows
	![image](https://github.com/KewkLW/ComfyUI-kewky_tools/assets/57611539/7bf50966-6e6b-43cd-92ba-42aae291be8f)

	### Example pasting unformatted text 
	![image](https://github.com/KewkLW/ComfyUI-kewky_tools/assets/57611539/18a8cee5-3b13-47c5-87b1-6171fe7cd093)

	### Example scheduling of Interrogator output
	![image](https://github.com/KewkLW/ComfyUI-kewky_tools/assets/57611539/27b54da6-6b96-4adc-a601-508e4d3179c5)

5. open_py_feature.py
   Adds a context menu item that will open the py file for whatever node you want to review.


![image](https://github.com/user-attachments/assets/f57f1b62-4a7d-4d77-b39f-40487521fbd7)


## Getting Started

To use these tools, clone the repository to your local machine using:

```bash
cd Comfyui/custom_nodes
git clone https://github.com/KewkLW/ComfyUI-kewky_tools.git
