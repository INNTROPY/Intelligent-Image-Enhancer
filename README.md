# Intelligent-Image-Enhancer

## **1. Contexto y Objetivo del Proyecto**
El proyecto **Intelligent Image Enhancer (IIE)** tiene como objetivo principal desarrollar un conjunto de nodos personalizados para **ComfyUI** que permitan escalar imágenes de manera ****inteligente gracias a:
1. Escalado mediante modelos avanzados de superresolución.
2. **Integración en el procedo de escalado de descripciones automáticas detalladas de las imágenes** (prompts) mediante el uso de modelos de lenguaje de **Ollama en local**. La solución p**ermite la edición de los prompts generados** para que el usuario pueda ajustar los resultados y volver a ejecutar el flujo si lo desea.
3. **División de la imagen escalada en mosaicos (tiles)** para procesarlas por partes, facilitando el manejo de imágenes grandes y optimizando el uso de memoria. Cada tile es mejorado con la introducción de detalles también fortalecidos por prompts específicos de cada tile.

El flujo de trabajo está diseñado para ser modular y flexible, permitiendo a los usuarios personalizar cada etapa del proceso según sus necesidades.

## **2. Nodos y Funcionalidades**
### **2.1. Nodo IIE_Upscaler**
- **Objetivo**: Este nodo se encarga del escalado inicial y la generación de un general_prompt:
    1. **Generación del general_prompt**:
        - Genera una descripción detallada de la imagen de entrada utilizando el modelo de lenguaje **Ollama**.
        - Este prompt se utiliza como entrada para el escalado de la imagen y para fases posteriores del flujo.
    2. **Edición del general_prompt:**
        - Permite al usuario editar el prompt generado si no está satisfecho con los resultados iniciales.
        - Los prompts editados se pueden reutilizar para volver a ejecutar el flujo.
    3. **Superresolución**:
        - Escala la imagen de entrada utilizando modelos avanzados de superresolución y el general_prompt generado.
- **Estado Actual**:
    - **Generación del general_prompt:** Implementada y funcional.
    - **Edición del general_prompt**: En desarrollo. El texto generado por Ollama no se muestra correctamente en el campo editable.
    - **Superresolución**: Pendiente de implementación.
- **Basado en**:
    - **OllamaGenerate** y **OllamaVision**: Para la generación de prompts utilizando el modelo de lenguaje Ollama.
    - **TextEdit**: Para la funcionalidad de edición de texto en tiempo real.
    - InvSRSampler: Para el escalado mediante superresolución.

### **2.2. Nodo IIE_TileProcessor**
- **Objetivo**: Dividir la imagen escalada en mosaicos (tiles) para procesarlos por partes.
- **Funcionalidades**:
    - Divide la imagen en mosaicos de tamaño configurable.
    - Genera un prompt para cada mosaico utilizando el modelo de lenguaje Ollama.
    - Reconstruye la imagen final combinando los mosaicos procesados.
- **Estado Actual**: Pendiente de implementación.
- **Basado en**:
    - **Ultimate SD Upscale**: Para la lógica de división en mosaicos.
    - **OllamaGenerate**: Para la generación de prompts para cada mosaico.

### **2.3. Nodo Secundario: IIE_TileUpscaler**
- **Objetivo**: Aplicar upscaling a cada mosaico y combinar los resultados en una imagen final.
- **Funcionalidades**:
    - Procesa cada mosaico utilizando un modelo de escalado/superresolución.
    - Combina los mosaicos procesados en una imagen final.
    - Redimensiona la imagen final a las medidas indicadas por el usuario
- **Estado Actual**: Pendiente de implementación.
- **Basado en**:
    - **Ultimate SD Upscale**: Para la lógica de reconstrucción de la imagen final.

### **3. Flujo de Trabajo**
1. **Entrada de Imagen**:
    - El usuario proporciona una imagen de entrada que será procesada.
2. **Generación de Prompt General**:
    - El nodo **IIE_Upscaler** utiliza el modelo de lenguaje **Ollama** para generar una descripción detallada de la imagen.
    - Este prompt se utiliza como entrada para el escalado de la imagen en el mismo nodo.
3. Escalado de la imagen:
    - El nodo utiliza el general_prompt y la tecnología InvSR para escalar la imagen
4. **División en Mosaicos**:
    - La imagen escalada se divide en mosaicos utilizando el nodo **IIE_TileProcessor**.
    - Se genera un prompt para cada mosaico.
5. **Procesamiento de Mosaicos**:
    - Cada mosaico se procesa utilizando el nodo **IIE_TileUpscaler**, que aplica upscale/superresolución y mejora de detalle con tecnología Detail Daemon.
    - Los mosaicos procesados se combinan para formar la imagen final.
    - La imagen final se redimensiona a las medidas indicadas por el usuario
6. **Edición de Prompts**:
    - Si el usuario no está satisfecho con los resultados, puede editar los prompts generados y volver a ejecutar el flujo.

### **4. Siguientes Pasos (Nodo IIE_Upscaler)**
1. **Resolver Problemas del Campo Editable**:
    - Asegurarse de que el texto generado por Ollama se muestre correctamente en el campo `general_prompt`.
    - Validar que los cambios realizados por el usuario se reflejen en el flujo.
2. **Implementar Superresolución**:
    - Aplicar un modelo de superresolución en el nodo

## Nodo Intelligent Upscale Sampler (IUS)
### Inputs conectores
- image
- checkpoint_model
- vae
- positive
- negative
- upscale_model
### Inputs dentro del nodo
Parámetros de sampler:
- ollama_model: desplegable
- url: campo editable
- debug: booleano
- keep_alive: campo editable
- ollama_vision: booleano
- ollama_prompt: campo editable
- general_prompt: campo editable
- seed: campo editable
- control_after_generate: desplegable
- upscale_by: campo editable
- steps: campo editable
- cfg: campo editable
- sampler_name: desplegable
- scheduler: desplegable
- denoise: desplegable
### Outputs dentro del nodo
- general_prompt campo editable
### Outputs conectores
- general_prompt
- upscaled_image
