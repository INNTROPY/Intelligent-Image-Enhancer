# Intelligent-Image-Enhancer

## **Contexto y Objetivo del Proyecto**

El proyecto **Intelligent Image Enhancer (IIE)** tiene como objetivo principal desarrollar un conjunto de nodos personalizados para **ComfyUI** que permitan escalar imágenes de manera inteligente gracias a:

1. Escalado mediante modelos avanzados de superresolución.
2. Integración en el procedo de escalado de descripciones automáticas detalladas de las imágenes (prompts) mediante el uso de modelos de lenguaje de Ollama en local. La solución permite la edición de los prompts generados para que el usuario pueda ajustar los resultados y volver a ejecutar el flujo si lo desea.
3. División de la imagen escalada en mosaicos para procesarlas por partes, facilitando el manejo de imágenes grandes y optimizando el uso de memoria. Cada tile es mejorado con la introducción de detalles también fortalecidos por prompts específicos para cada tile.

## **Esquema Estratégico Completo del Proyecto Intelligent Image Enhancer (IIE)**

### **1. Nodo: IIE_Upscaler**

#### **Funcionalidades:**

1. **Generación del `general_prompt`**:
    - Utiliza Ollama para generar una descripción detallada de la imagen completa.
    - Este prompt se utiliza como contexto en el escalado inicial y en la generación de los `tile_prompts`.
2. **Escalado inicial con superresolución**:
    - Escala la imagen de entrada utilizando un modelo avanzado de superresolución, guiado por el `general_prompt`.
3. **División en tiles**:
    - Divide la imagen escalada en mosaicos (`tiles`) de tamaño configurable.
4. **Generación de `tile_prompts`**:
    - Genera un prompt específico para cada mosaico utilizando Ollama.
    - Cada `tile_prompt` incluye el `general_prompt` como contexto, estructurado como:`"a portion of general_prompt, tile_prompt"`.
5. **Visualización de la imagen escalada con tiles etiquetados**:
    - Genera una imagen con los bordes de los tiles dibujados y etiquetados con identificadores únicos (`Tile 1`, `Tile 2`, etc.).
    - Esta imagen se envía al siguiente nodo para facilitar la edición de los prompts.
6. **Salida de datos**:
    - Envía:
        - La imagen escalada.
        - El `general_prompt`.
        - Los `tile_prompts` (estructurados en un diccionario con identificadores únicos).
        - La imagen con los tiles etiquetados.

### **2. Nodo: IIE_Prompt_Editor**

**Funcionalidades:**

1. **Visualización de la imagen escalada con tiles etiquetados**:
    - Muestra la imagen generada por el nodo `IIE_Upscaler` en un campo `PreviewImage`.
2. **Generación de campos editables**:
    - Genera dinámicamente un número de campos editables igual al número de tiles + 1 (para el `general_prompt`).
    - Cada campo editable está asociado a un identificador único (`general_prompt`, `Tile 1`, `Tile 2`, etc.).
3. **Edición de prompts**:
    - Permite al usuario modificar los prompts generados automáticamente por Ollama.
4. **Salida de datos**:
    - Envía:
        - Los prompts editados por el usuario.
        - Los identificadores de los prompts editados (para que el siguiente nodo pueda combinarlos con los originales).

### **3. Nodo: IIE_Tile_Detailer**

**Funcionalidades:**

1. **Recepción y combinación de prompts**:
    - Recibe:
        - Los prompts generados automáticamente (`general_prompt` y `tile_prompts`) desde el nodo `IIE_Upscaler`.
        - Los prompts editados por el usuario desde el nodo `IIE_Prompt_Editor`.
    - Combina ambos conjuntos de datos:
        - Prioriza los prompts editados por el usuario.
        - Utiliza los prompts generados automáticamente para los tiles que no fueron editados.
2. **Escalado y mejora de detalles en cada tile**:
    - Escala cada mosaico utilizando un modelo de superresolución.
    - Añade detalles a cada mosaico, guiado por los `tile_prompts` combinados y el `general_prompt`.
3. **Unión de tiles en una imagen final**:
    - Combina los mosaicos procesados en una única imagen final.
4. **Redimensionamiento de la imagen final**:
    - Ajusta la imagen final al tamaño deseado por el usuario.
5. **Salida de datos**:
    - Envía la imagen final procesada para que pueda ser guardada o utilizada en etapas posteriores.

### **Flujo de Datos**

1. **Nodo 1 (IIE_Upscaler)**:
    - Genera y envía:
        - `general_prompt`.
        - `tile_prompts`.
        - Imagen escalada.
        - Imagen con tiles etiquetados.
2. **Nodo 2 (IIE_Prompt_Editor)**:
    - Recibe:
        - Los prompts generados automáticamente.
        - La imagen con tiles etiquetados.
    - Permite la edición de los prompts y envía los editados al siguiente nodo.
3. **Nodo 3 (IIE_Tile_Detailer)**:
    - Recibe:
        - Los prompts generados automáticamente.
        - Los prompts editados por el usuario.
    - Procesa los tiles y genera la imagen final.

### **Puntos Clave**

- **Estructura de los `tile_prompts`**:
    - Cada `tile_prompt` incluye el `general_prompt` como contexto.
    - Ejemplo: `"a portion of an image of a sunset over the ocean, a detailed description of the tile."`
- **Visualización en el nodo `IIE_Prompt_Editor`**:
    - La imagen con los tiles etiquetados facilita al usuario identificar qué prompt corresponde a cada mosaico.
- **Flexibilidad en la edición**:
    - El usuario puede editar solo los prompts que considere necesarios, manteniendo los originales para los demás tiles.
