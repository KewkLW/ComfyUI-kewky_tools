# with all due respect to cubiq for the original code https://github.com/cubiq/ComfyUI_essentials
import model_management
import torch
import gc
import psutil

class VRAM_Debug_Plus:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "empty_cache": ("BOOLEAN", {"default": True}),
                "gc_collect": ("BOOLEAN", {"default": True}),
                "unload_all_models": ("BOOLEAN", {"default": False}),
                "display_mode": (["Simple", "Detailed"], {"default": "Simple"}),
            },
            "optional": {
                "any_input": ("*", {}),
                "image_pass": ("IMAGE",),
                "model_pass": ("MODEL",),
            }
        }
        
    RETURN_TYPES = ("*", "IMAGE", "MODEL", "INT", "INT", "STRING")
    RETURN_NAMES = ("any_output", "image_pass", "model_pass", "freemem_before", "freemem_after", "memory_report")
    FUNCTION = "VRAMdebug"
    CATEGORY = "🧔🏻‍♂️🇰 🇪 🇼 🇰 "
    DESCRIPTION = """
    Performs VRAM management operations and provides detailed memory usage reports.
    Returns inputs unchanged, used as triggers. Reports free VRAM before and after operations.
    """

    def VRAMdebug(self, empty_cache, gc_collect, unload_all_models, display_mode, image_pass=None, model_pass=None, any_input=None):
        freemem_before = model_management.get_free_memory()
        total_memory = torch.cuda.get_device_properties(0).total_memory
        
        if empty_cache:
            torch.cuda.empty_cache()
            model_management.soft_empty_cache()
        if unload_all_models:
            model_management.unload_all_models()
        if gc_collect:
            gc.collect()
        
        freemem_after = model_management.get_free_memory()
        
        memory_report = self.generate_memory_report(freemem_before, freemem_after, total_memory, display_mode)
        
        return (any_input, image_pass, model_pass, int(freemem_before), int(freemem_after), memory_report)

    def generate_memory_report(self, freemem_before, freemem_after, total_memory, display_mode):
        used_before = total_memory - freemem_before
        used_after = total_memory - freemem_after
        freed_memory = freemem_after - freemem_before

        if display_mode == "Simple":
            return f"Free VRAM: {freemem_before:,.0f} -> {freemem_after:,.0f} ({freed_memory:+,.0f})"
        else:
            report = f"VRAM Report:\n"
            report += f"Total VRAM: {total_memory:,.0f}\n"
            report += f"Free VRAM Before: {freemem_before:,.0f} ({freemem_before/total_memory:.1%})\n"
            report += f"Free VRAM After: {freemem_after:,.0f} ({freemem_after/total_memory:.1%})\n"
            report += f"Used VRAM Before: {used_before:,.0f} ({used_before/total_memory:.1%})\n"
            report += f"Used VRAM After: {used_after:,.0f} ({used_after/total_memory:.1%})\n"
            report += f"VRAM Freed: {freed_memory:,.0f} ({freed_memory/total_memory:.1%})\n"
            report += f"System RAM Usage: {psutil.virtual_memory().percent:.1f}%"
            return report

# Node class mappings
NODE_CLASS_MAPPINGS = {
    "VRAM_Debug_Plus": VRAM_Debug_Plus
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VRAM_Debug_Plus": "VRAM Debug+"
}