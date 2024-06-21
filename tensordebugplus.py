# with all due respect to cubiq for the original code https://github.com/cubiq/ComfyUI_essentials

import torch
import torch.nn as nn
import sys

class TensorDebugPlus:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tensor": (any, {}),
                "include_gradients": ("BOOLEAN", {"default": False}),
                "include_statistics": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CATEGORY = "🧔🏻‍♂️🇰 🇪 🇼 🇰 "
    OUTPUT_NODE = True

    def execute(self, tensor, include_gradients, include_statistics):
        shapes = []
        shape_counts = {}
        total_params = 0
        total_memory = 0

        def format_size(size_bytes):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024.0

        def tensorShape(tensor, name=''):
            nonlocal total_params, total_memory

            if isinstance(tensor, dict):
                for k, v in tensor.items():
                    tensorShape(v, f"{name}.{k}" if name else k)
            elif isinstance(tensor, list):
                for i, item in enumerate(tensor):
                    tensorShape(item, f"{name}[{i}]")
            elif isinstance(tensor, torch.Tensor):
                shape = tuple(tensor.shape)
                dtype = str(tensor.dtype)
                device = str(tensor.device)
                requires_grad = tensor.requires_grad
                grad = tensor.grad

                num_params = tensor.numel()
                memory_size = tensor.element_size() * num_params

                total_params += num_params
                total_memory += memory_size

                info = {
                    'name': name,
                    'shape': shape,
                    'dtype': dtype,
                    'device': device,
                    'requires_grad': requires_grad,
                    'num_params': num_params,
                    'memory': format_size(memory_size)
                }

                if include_gradients and grad is not None:
                    info['grad_shape'] = tuple(grad.shape)

                if include_statistics:
                    info['min'] = tensor.min().item()
                    info['max'] = tensor.max().item()
                    info['mean'] = tensor.mean().item()
                    info['std'] = tensor.std().item()

                shapes.append(info)
                shape_counts[shape] = shape_counts.get(shape, 0) + 1

            elif isinstance(tensor, nn.Module):
                for name, param in tensor.named_parameters():
                    tensorShape(param, name)
                for name, module in tensor.named_children():
                    tensorShape(module, name)
            elif hasattr(tensor, 'model') and isinstance(tensor.model, nn.Module):
                tensorShape(tensor.model, 'model')
            else:
                print(f"Unexpected tensor type: {type(tensor)}", file=sys.stderr)

        tensorShape(tensor)

        # Generate detailed output
        output = []
        for info in shapes:
            line = f"Name: {info['name']}, Shape: {info['shape']}, Type: {info['dtype']}, Device: {info['device']}"
            line += f", Requires Grad: {info['requires_grad']}, Params: {info['num_params']}, Memory: {info['memory']}"
            if include_gradients and 'grad_shape' in info:
                line += f", Grad Shape: {info['grad_shape']}"
            if include_statistics:
                line += f", Min: {info['min']:.4f}, Max: {info['max']:.4f}, Mean: {info['mean']:.4f}, Std: {info['std']:.4f}"
            output.append(line)

        # Add summary
        summary = [
            f"Total shapes: {len(shapes)}",
            f"Unique shapes: {len(shape_counts)}",
            f"Total parameters: {total_params:,}",
            f"Total memory usage: {format_size(total_memory)}",
            "Shape distribution:"
        ]
        for shape, count in shape_counts.items():
            summary.append(f"  {shape}: {count}")

        # Combine output and summary
        full_output = "\n".join(output + ["\nSummary:"] + summary)

        print(f"\033[96m{full_output}\033[0m")  # Console output in cyan

        return (full_output,)

# borrowed from https://github.com/pythongosssss/ComfyUI-Custom-Scripts
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

EPSILON = 1e-5

# Node class mappings
NODE_CLASS_MAPPINGS = {
    "TensorDebugPlus": TensorDebugPlus
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TensorDebugPlus": "Tensor Debug++"
}
