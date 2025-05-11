import { app } from "../../../../scripts/app.js"; // Path relative to js folder in custom_nodes
import { api } from "../../../../scripts/api.js";   // Path relative to js folder in custom_nodes

async function handleOpenPyFile(node) {
    const nodeTypeName = node.type;
    if (!nodeTypeName) {
        console.error("Node type name is undefined for node:", node.title);
        app.ui.dialog.show("Error: Could not identify node type.");
        return;
    }

    console.log(`Requesting to open Python file for node type: ${nodeTypeName}`);

    try {
        const response = await api.fetchApi('/open_node_source', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ node_type: nodeTypeName }),
        });

        const result = await response.json(); 
        if (!response.ok) {
            const errorMessage = result.error || response.statusText || 'Could not open file.';
            console.error("Error opening Python file:", errorMessage, "Status:", response.status, "Response:", result);
            app.ui.dialog.show(`Error: ${errorMessage}`);
            return;
        }
        
        const successMessage = result.message || "File open request sent successfully.";
        console.log(successMessage, "Response:", result);
        // Optionally, show a brief success message. 
        // The file opening is the primary feedback, so this might be redundant.
        // app.ui.dialog.show(successMessage); 
        
    } catch (error) {
        console.error("Failed to send 'open py' request or parse response:", error);
        app.ui.dialog.show("Error: Failed to communicate with server to open file. Check console for details.");
    }
}

app.registerExtension({
    name: "comfy.helper.openPyFile", // Unique name for the extension
    async setup() {
        console.log("ComfyUI 'Open Py File' Extension: Setup complete.");
    },
    beforeRegisterNodeDef(nodeType, nodeData, appInstance) {
        // Get the original getExtraMenuOptions function from the node's prototype
        const original_getExtraMenuOptions = nodeType.prototype.getExtraMenuOptions;

        nodeType.prototype.getExtraMenuOptions = function(_, options) {
            // `this` refers to the specific node instance that was right-clicked
            
            if (original_getExtraMenuOptions) {
                original_getExtraMenuOptions.apply(this, arguments);
            }
            
            if (!Array.isArray(options)) {
                console.warn("Node context menu options is not an array for node type:", nodeType.comfyClass, "Options:", options);
            }

            options.unshift(
                {
                    content: "Open Py File 📜", 
                    callback: () => {
                        console.log("Open Py File clicked for node:", this.title, "(Type:", this.type, ", ID:", this.id + ")");
                        handleOpenPyFile(this); 
                    }
                }
            );

            if (options.length > 1 && original_getExtraMenuOptions) { 
                if (options[1] !== null) {
                    options.splice(1, 0, null); 
                }
            }
        };
    }
});