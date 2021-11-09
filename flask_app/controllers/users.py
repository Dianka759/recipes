from flask_app import app
from flask import render_template,flash,redirect,request,session
from flask_app.models.user import User
from flask_app.models.recipe import Recipe
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route("/")
def index():
    return render_template("index.html")

#  ====================================
#  Login and registration stuffs
#  ====================================

@app.route("/register",methods=["POST"])
def register():
    if User.validate(request.form):
        pw_hash = bcrypt.generate_password_hash(request.form["password"])
        data = {
        "first_name":request.form["first_name"],
        "last_name":request.form["last_name"],
        "email":request.form["email"],
        "password":pw_hash,
        "confirm_password":pw_hash
        }
        user_id = User.insert_user(data)
        flash("User created!", "register")  
        flash("Please login! :)", "login")
        # session["user_id"] = user_id       #creates the session
        return redirect("/")
    else:
        return redirect("/")

@app.route("/login",methods=["POST"])
def login():
    user_in_db = User.get_by_email(request.form)
    if not user_in_db:
        flash("invalid email/password", "login")
        return redirect("/")
    if not bcrypt.check_password_hash(user_in_db.password, request.form["password"]): 
        flash("invalid email/password", "login")
        return redirect("/")
    session["user_id"] = user_in_db.id   # CREATES THE SESSION
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    flash("logged out!", "login")
    return redirect("/")

# ==========================================
#  Main page 
#  =========================================

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:    #checks if you're logged in 
        flash("Must be registered or logged in!", "register")
        return redirect("/")
    else:
        data = {
            "user_id": session["user_id"]
        }
        user = User.get_user(data)
        recipes = Recipe.get_recipes(data)
        return render_template("dashboard.html", user=user, recipes=recipes)

# ==========================================
#  Recipes page 
#  =========================================

@app.route("/new_recipe/<int:user_id>")
def new_recipe(user_id):
    if "user_id" not in session:    #checks if you're logged in 
        flash("Must be registered or logged in!", "register")
        return redirect("/")
    data = {
        "user_id": session["user_id"]
    }
    recipe = Recipe.get_recipes(data)
    user = User.get_user(data)
    return render_template("create_recipe.html", recipe=recipe, user=user)

@app.route('/create_recipe/<int:user_id>', methods=["POST"])
def create_recipe(user_id):
    if Recipe.validate_recipe(request.form):
        data = {
            "name":request.form["name"],
            "under_30":request.form['under_30'],
            "description":request.form["description"],
            "instructions":request.form["instructions"],
            "created_at":request.form["created_at"],
            "user_id":user_id
            }
        Recipe.insert_recipe(data)
        return redirect("/dashboard")
    else:
        return redirect(f"/new_recipe/{user_id}")

# ==========================================
#  Delete recipe
#  =========================================

@app.route("/delete/<int:id>")
def delete_recipe(id):
    data = {
        "id":id
    }
    Recipe.delete_recipe(data)
    return redirect("/dashboard")

# ==========================================
#  Edit recipe
#  =========================================

@app.route("/edit/<int:id>")
def edit_recipe(id):
    if "user_id" not in session:    #checks if you're logged in 
        flash("Must be registered or logged in!", "register")
        return redirect("/")
    data = {
        "id":id
    }
    recipe = Recipe.get_recipe(data)
    return render_template("edit_recipe.html",recipe=recipe)

@app.route("/update/<int:id>",methods=["POST"])
def update(id):
    if Recipe.validate_recipe(request.form):
        data = {
            "name":request.form["name"],
            "under_30": request.form['under_30'],
            "description":request.form["description"],
            "instructions":request.form["instructions"],
            "created_at":request.form["created_at"],
            "id":id
            }
        Recipe.update_recipe(data)
        return redirect("/dashboard")
    else:
        return redirect(f"/edit/{id}")

# ==========================================
#  View one recipe
# =========================================

@app.route("/view_instructions/<int:id>")
def show_recipe(id):
    if "user_id" not in session:    #checks if you're logged in (the session above exists)
        flash("Must be registered or logged in!", "register")
        return redirect("/")
    data = {
        "id":id,
        "user_id":session["user_id"]
    }
    user = User.get_user(data)
    recipe = Recipe.get_recipe(data)
    return render_template("show_recipe.html", user=user, recipe=recipe)