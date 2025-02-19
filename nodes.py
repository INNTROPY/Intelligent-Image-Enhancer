import os
import torch
import numpy as np
from PIL import Image, ImageOps
from comfy.comfy_types import ComfyNodeABC, InputTypeDict
import folder_paths
import node_helpers
from ollama import Client
from io import BytesIO
import hashlib

class IIE_Upscaler(ComfyNodeABC):
    @classmethod
    def INPUT_TYPES(cls) -> InputTypeDict:
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {
            "required": {
                "image": (sorted(files), {"image_upload": True, "tooltip": "Upload an image."}),
                "ollama_vision": ("BOOLEAN", {"default": True, "tooltip": "Enable or disable the use of Ollama to generate the general prompt."}),
                "ollama_model": (cls.get_ollama_models(), {"tooltip": "Select an Ollama model to create the general_prompt."}),
                "ollama_url": ("STRING", {"default": "http://127.0.0.1:11434", "tooltip": "Ollama server URL."}),
                "ollama_prompt": ("STRING", {
                    "default": "Generate a detailed and professional image description using 4 sentences in present tense in a single paragraph, covering subjects, objects, backgrounds, colours, textures, designs, lighting, and artistic techniques to convey the scene and its emotion accurately. Provide only the image prompt text in British English, without additional formatting, explanations, questions, metacommentary, or introductory and closing remarks.",
                    "multiline": True,
                    "tooltip": "Editable prompt for Ollama."
                }),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1, "tooltip": "Seed for prompt generation and upscaling."}),
                "keep_alive": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 60,
                    "step": 1,
                    "tooltip": "Time in minutes to keep the model loaded in VRAM. Set to 0 to unload the model immediately after use."
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("upscaled_image", "general_prompt")
    FUNCTION = "process"

    CATEGORY = "image"

    @staticmethod
    def get_ollama_models():
        """
        Obtiene la lista de modelos disponibles desde el servidor de Ollama.
        """
        try:
            client = Client(host="http://127.0.0.1:11434")  # URL del servidor Ollama
            models = client.list().get('models', [])
            return [model['model'] for model in models]
        except Exception as e:
            print(f"[IIE_Upscaler] Error al obtener los modelos de Ollama: {e}")
            return ["default_model"]  # Modelo predeterminado en caso de error

    def process(self, image, ollama_vision, ollama_model, ollama_url, ollama_prompt, seed, keep_alive):
        """
        Procesa la imagen y genera el general_prompt utilizando Ollama si está habilitado.
        """
        # Validar la imagen cargada
        if not image:
            raise ValueError("No se ha seleccionado ninguna imagen. Por favor, sube una imagen para procesarla.")

        # Validar el rango del seed
        if not (0 <= seed <= 0xffffffff):
            raise ValueError(f"El seed debe estar entre 0 y 2**32 - 1. Valor recibido: {seed}")

        # Ruta completa de la imagen seleccionada
        image_path = folder_paths.get_annotated_filepath(image)

        # Cargar la imagen usando PIL
        img = node_helpers.pillow(Image.open, image_path)
        img = node_helpers.pillow(ImageOps.exif_transpose, img)

        # Convertir la imagen a un tensor de PyTorch
        image_tensor = np.array(img).astype(np.float32) / 255.0
        image_tensor = torch.from_numpy(image_tensor).unsqueeze(0)  # Añadir dimensión de batch

        # Generar el general_prompt si Ollama está habilitado
        general_prompt = ""
        if ollama_vision:
            general_prompt = self.generate_prompt(image_tensor, ollama_model, ollama_url, ollama_prompt, seed, keep_alive)

        return image_tensor, general_prompt

    def generate_prompt(self, image_tensor, ollama_model, ollama_url, ollama_prompt, seed, keep_alive):
        """
        Genera un prompt utilizando Ollama basado en la imagen proporcionada.
        """
        try:
            # Configurar el seed para la generación del prompt
            torch.manual_seed(seed)
            np.random.seed(seed)

            # Convertir la imagen a formato PNG en memoria
            img = (image_tensor[0].cpu().numpy() * 255).astype(np.uint8)  # Convertir tensor a numpy array
            img = Image.fromarray(img)
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_binary = buffered.getvalue()

            # Configurar el cliente de Ollama
            client = Client(host=ollama_url)

            # Mensajes de depuración
            print(f"[IIE_Upscaler] Enviando solicitud a Ollama:\n- Modelo: {ollama_model}\n- Prompt: {ollama_prompt}\n- Seed: {seed}\n- Keep Alive: {keep_alive} minutos")

            # Realizar la solicitud a Ollama
            response = client.generate(
                model=ollama_model,
                prompt=ollama_prompt,
                images=[img_binary],
                keep_alive=f"{keep_alive}m"
            )

            # Extraer el texto del prompt generado
            general_prompt = response.get("response", "No se pudo generar el prompt.")
            print(f"[IIE_Upscaler] Respuesta de Ollama: {general_prompt}")

            return general_prompt

        except Exception as e:
            print(f"[IIE_Upscaler] Error al generar el prompt: {e}")
            return "Error al generar el prompt."

    @classmethod
    def IS_CHANGED(cls, image, **kwargs):
        """
        Verificar si la imagen ha cambiado. Ignora argumentos adicionales.
        """
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, 'rb') as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(cls, image):
        """
        Validar si la imagen existe.
        """
        if not folder_paths.exists_annotated_filepath(image):
            return f"Archivo de imagen inválido: {image}"
        return True


# Registro del nodo
NODE_CLASS_MAPPINGS = {
    "IIE_Upscaler": IIE_Upscaler
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "IIE_Upscaler": "IIE Upscaler (Cargar Imagen)"
}
