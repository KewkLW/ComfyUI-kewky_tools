#edit of https://github.com/cubiq/ComfyUI_essentials
class TensorDebugPlus:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tensor": (any, {}),
            },
        }

    RETURN_TYPES = ("STRING",)  # Add string output type
    FUNCTION = "execute"
    CATEGORY = "kewky_tools"
    OUTPUT_NODE = True

    def execute(self, tensor):
        shapes = []

        def tensorShape(tensor):
            if isinstance(tensor, dict):
                for k in tensor:
                    tensorShape(tensor[k])
            elif isinstance(tensor, list):
                for i in range(len(tensor)):
                    tensorShape(tensor[i])
            elif hasattr(tensor, 'shape'):
                shapes.append(list(tensor.shape))

        tensorShape(tensor)
        shapes_output = f"{shapes}"
        print(f"\033[96m{shapes_output}\033[0m")  # Keep the print statement for console output

        return (shapes_output,)  # Return the string output

#borrowed from https://github.com/pythongosssss/ComfyUI-Custom-Scripts
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False
any = AnyType("*")

EPSILON = 1e-5
