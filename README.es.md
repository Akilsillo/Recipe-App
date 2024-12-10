# Recipe App

## 🍲 Descripción
Recipe App es una aplicación desarrollada con **Python**, **FastAPI** y **SQLModel**, diseñada para facilitar la búsqueda y recomendación de recetas basadas en una lista de ingredientes.

El proyecto surgió para solucionar un problema común entre los entusiastas de la cocina: ¡decidir qué cocinar! Además, ofrece herramientas para gestionar recetas con un sistema de autenticación simple, permitiendo asociar las recetas a los usuarios que las crean y otorgando operaciones especiales a los administradores ("superusers").

El objetivo principal es mostrar mis habilidades en FastAPI, el manejo de bases de datos relacionales y la implementación de relaciones many-to-many. Es una aplicación real que también utilizo a diario.

---

## 🌍 Características principales
- **Recomendación de recetas por ingredientes**: Ingresa una lista de ingredientes y recibe recetas que puedes preparar.
- **Gestor CRUD de recetas e ingredientes**:
  - Crear nuevas recetas.
  - Buscar recetas por nombre o ID.
  - Actualizar y borrar recetas existentes.
- **Sistema de autenticación**:
  - Asociar recetas con el usuario creador.
  - Autorización de acciones para usuarios normales y superusuarios (admins).
- **Base de datos relacional**: Relación many-to-many entre recetas e ingredientes para mayor flexibilidad.

---

## 🚀 Tecnologías utilizadas
- **FastAPI**: Para el backend.
- **SQLModel**: Manejo de la base de datos relacional.
- **SQLite** (por defecto): Base de datos ligera para desarrollo local (se puede migrar a otras bases de datos como PostgreSQL).
- **Uvicorn**: Servidor de desarrollo ASGI.
- **JWT**: Autenticación segura.

---

## 🔧 Instalación
Sigue estos pasos para ejecutar el proyecto localmente:

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu_usuario/recipe-app.git
   cd recipe-app
   ```

2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecuta la aplicación:
   ```bash
   uvicorn main:app --reload
   ```

5. Accede a la documentación interactiva de la API en tu navegador:
   - **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🌐 Uso
### Endpoints principales:

- **Recetas**:
  - `GET /recipes/{id}`: Busca una receta por ID.
  - `GET /recipes/recipe_by_name/{name}`: Busca una receta por nombre.
  - `POST /recipes/recipe_by_ingredients`: Busca recetas que coincidan con los ingredientes entregados.
  - `POST /recipes/create_recipe`: Crea una nueva receta (autenticación requerida).
  - `PUT /recipes/update_recipe/{recipe_name}`: Actualiza una receta existente (autorización requerida).
  - `DELETE /recipes/{recipe_id}`: Elimina una receta por su ID (autorización requerida).

- **Ingredientes**:
  - `GET /recipes/ingredient_by_name/{ingredient_name}`: Obtiene un ingrediente por su nombre.
  - `GET /recipes/ingredient_by_id/{ingredient_id}`: Obtiene un ingrediente por su ID.
  - `POST /recipes/create_ingredient`: Crea un nuevo ingrediente.
  - `DELETE /recipes/delete_ingredient/{id}`: Elimina un ingrediente por su ID (autorización requerida).

- **Autenticación**:
  - `POST /auth/login`: Inicia sesión y recibe un token JWT.
  - `POST /auth/signup`: Registra un nuevo usuario.

Para más detalles, consulta la documentación en Swagger UI.

---

## 💎 Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más información.
