# Recipe App

## 🍲 Description
Recipe App is an application developed with **Python**, **FastAPI**, and **SQLModel**, designed to facilitate the search and recommendation of recipes based on a list of ingredients.

This project was created to solve a common problem among cooking enthusiasts: deciding what to cook! Additionally, it provides tools to manage recipes with a simple authentication system, allowing recipes to be associated with the users who create them and granting special operations to administrators ("superusers").

The primary goal is to showcase my skills in FastAPI, handling relational databases, and implementing many-to-many relationships. It is a real application that I also use daily.

---

## 🌍 Main Features
- **Recipe recommendations by ingredients**: Enter a list of ingredients and receive recipes you can prepare.
- **CRUD manager for recipes and ingredients**:
  - Create new recipes.
  - Search recipes by name or ID.
  - Update and delete existing recipes.
- **Authentication system**:
  - Associate recipes with the creating user.
  - Authorization for actions by normal users and superusers (admins).
- **Relational database**: Many-to-many relationship between recipes and ingredients for greater flexibility.

---

## 🚀 Technologies Used
- **FastAPI**: For the backend.
- **SQLModel**: For handling the relational database.
- **SQLite** (default): Lightweight database for local development (can be migrated to other databases like PostgreSQL).
- **Uvicorn**: ASGI server for development.
- **JWT**: Secure authentication.

---

## 🔧 Installation
Follow these steps to run the project locally:

1. Clone this repository:
   ```bash
   git clone https://github.com/your_username/recipe-app.git
   cd recipe-app
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

5. Access the interactive API documentation in your browser:
   - **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🌐 Usage
### Main Endpoints:

- **Recipes**:
  - `GET /recipes/{id}`: Retrieve a recipe by ID.
  - `GET /recipes/recipe_by_name/{name}`: Retrieve a recipe by name.
  - `POST /recipes/recipe_by_ingredients`: Retrieve recipes that match the ingredients provided. 
  - `POST /recipes/create_recipe`: Create a new recipe (authentication required).
  - `PUT /recipes/{recipe_name}`: Update an existing recipe (authorization required).
  - `DELETE /recipes/{recipe_id}`: Delete a recipe (authorization required).

- **Ingredients**:
  - `GET /recipes/ingredient_by_name/{ingredient_name}`: Retrieve an ingredient by name.
  - `GET /recipes/ingredient_by_id/{ingredient_id}`: Retrieve an ingredient by ID.
  - `POST /recipes/create_ingredient`: Add new ingredients to the database.
  - `DELETE /recipes/delete_ingredient/{id}`: Delete an ingredient by ID (authorization required).

- **Authentication**:
  - `POST /auth/login`: Log in and receive a JWT token.
  - `POST /auth/signup`: Register a new user.

For more details, check the documentation in Swagger UI.

---

## 💎 License
This project is licensed under the MIT License. See the `LICENSE` file for more information.
