from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import mongo, is_mongo_available
from app.decorators import admin_required
from bson.objectid import ObjectId
import logging

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

# @usuarios_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     ...

@usuarios_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if not is_mongo_available():
            flash('Error de conexión a la base de datos.', 'danger')
            return redirect(url_for('usuarios.register'))
        email = request.form['email']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        if mongo.db.users.find_one({'email': email}):
            flash('Este correo ya está registrado.', 'warning')
        else:
            mongo.db.users.insert_one({'email': email, 'password': hashed_pw})
            flash('Registro exitoso. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('usuarios.login'))

    return render_template('auth/register.html')

@usuarios_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('usuarios.login'))

@usuarios_bp.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        if not is_mongo_available():
            flash('Error de conexión a la base de datos.', 'danger')
            return redirect(url_for('usuarios.forgot'))
        email = request.form['email']
        user = mongo.db.users.find_one({'email': email})
        if user:
            flash('Si el correo existe, se enviarán instrucciones.', 'info')
        else:
            flash('Correo no encontrado.', 'warning')
    return render_template('auth/forgot.html')

@usuarios_bp.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'user_id' not in session:
        flash('Debes iniciar sesión.', 'warning')
        return redirect(url_for('usuarios.login'))
    if not is_mongo_available():
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('main.dashboard'))
    user = mongo.db.users.find_one({'_id': session['user_id']})

    if request.method == 'POST':
        new_email = request.form['email']
        mongo.db.users.update_one({'_id': user['_id']}, {'$set': {'email': new_email}})
        flash('Correo actualizado.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('auth/edit.html', user=user)

@usuarios_bp.route('/admin/usuarios')
@admin_required
def gestionar_usuarios():
    # solo accesible por admin
    pass

# NUEVO ENDPOINT: Forzar cambio de contraseña
@usuarios_bp.route('/force_password_change', methods=['GET', 'POST'])
def force_password_change():
    user_id = session.get('force_password_user_id')
    if not user_id:
        flash('No hay usuario para cambio de contraseña.', 'danger')
        return redirect(url_for('auth.login'))
    try:
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    except Exception:
        flash('ID de usuario inválido.', 'danger')
        session.pop('force_password_user_id', None)
        return redirect(url_for('auth.login'))
    if not user:
        flash('Usuario no encontrado.', 'danger')
        session.pop('force_password_user_id', None)
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        # Validaciones básicas
        if not new_password or not confirm_password:
            flash('Debes completar ambos campos.', 'danger')
            return render_template('force_password_change.html', user=user)
        if new_password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('force_password_change.html', user=user)
        if len(new_password) < 8 or not any(c.isupper() for c in new_password) or not any(c.islower() for c in new_password) or not any(c.isdigit() for c in new_password):
            flash('La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número.', 'danger')
            return render_template('force_password_change.html', user=user)
        # Guardar nueva contraseña y limpiar flags
        mongo.db.users.update_one(
            {'_id': user['_id']},
            {'$set': {
                'password': generate_password_hash(new_password),
                'must_change_password': False
            }}
        )
        session.pop('force_password_user_id', None)
        flash('Contraseña actualizada. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('force_password_change.html', user=user)