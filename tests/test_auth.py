import pytest

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_user(client):
    response = client.post('/register', data={
        'nombre': 'TestUser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    data = response.data.decode('utf-8')
    assert 'Registro exitoso' in data or '¡Registro exitoso!' in data

def test_login_success(client):
    # Registrar usuario primero
    client.post('/register', data={
        'nombre': 'TestLogin',
        'email': 'testlogin@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    # Login correcto
    response = client.post('/login', data={
        'login_input': 'testlogin@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    data = response.data.decode('utf-8')
    assert 'Inicio de sesi' in data or 'dashboard' in data

def test_login_fail(client):
    response = client.post('/login', data={
        'login_input': 'noexiste@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    data = response.data.decode('utf-8')
    assert 'Usuario no encontrado' in data or 'Credenciales inv' in data

def test_logout(client):
    # Registrar y loguear
    client.post('/register', data={
        'nombre': 'TestLogout',
        'email': 'testlogout@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    client.post('/login', data={
        'login_input': 'testlogout@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    # Logout
    response = client.get('/logout', follow_redirects=True)
    data = response.data.decode('utf-8')
    assert 'login' in data or 'cerrado sesi' in data

def test_forgot_password(client):
    client.post('/register', data={
        'nombre': 'TestForgot',
        'email': 'testforgot@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    response = client.post('/forgot-password', data={
        'usuario': 'testforgot@example.com'
    }, follow_redirects=True)
    data = response.data.decode('utf-8')
    assert 'recuperación' in data or 'enlace' in data or 'correo' in data

def test_protected_route_requires_login(client):
    response = client.get('/dashboard', follow_redirects=True)
    data = response.data.decode('utf-8')
    assert 'iniciar sesión' in data or 'login' in data or 'Debes iniciar sesión' in data

def test_user_dashboard_access(client):
    client.post('/register', data={
        'nombre': 'TestPanel',
        'email': 'testpanel@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    client.post('/login', data={
        'login_input': 'testpanel@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    response = client.get('/dashboard_user', follow_redirects=True)
    data = response.data.decode('utf-8')
    assert 'tablas' in data or 'catálogo' in data or 'usuario' in data

def test_tables_access_after_login(client):
    client.post('/register', data={
        'nombre': 'TestTables',
        'email': 'testtables@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    client.post('/login', data={
        'login_input': 'testtables@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    response = client.get('/tables', follow_redirects=True)
    data = response.data.decode('utf-8')
    assert 'tablas' in data or 'catálogo' in data or 'crear' in data

def test_admin_panel_access(client, app):
    # Crear usuario admin directamente en la base de datos
    with app.app_context():
        admin_email = 'admintest@example.com'
        admin_user = app.users_collection.find_one({'email': admin_email})
        if not admin_user:
            from werkzeug.security import generate_password_hash
            app.users_collection.insert_one({
                'nombre': 'AdminTest',
                'email': admin_email,
                'password': generate_password_hash('adminpass'),
                'role': 'admin',
                'username': 'admintest'
            })
    # Login como admin
    client.post('/login', data={
        'login_input': 'admintest@example.com',
        'password': 'adminpass'
    }, follow_redirects=True)
    response = client.get('/admin/', follow_redirects=True)
    data = response.data.decode('utf-8')
    assert 'admin' in data or 'panel' in data or 'usuarios' in data

def test_user_cannot_access_admin_panel(client):
    client.post('/register', data={
        'nombre': 'TestNoAdmin',
        'email': 'testnoadmin@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    client.post('/login', data={
        'login_input': 'testnoadmin@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    response = client.get('/admin/', follow_redirects=True)
    data = response.data.decode('utf-8')
    assert 'permiso' in data or 'acceso' in data or 'login' in data

def test_admin_cannot_access_user_dashboard(client, app):
    # Login como admin
    client.post('/login', data={
        'login_input': 'admintest@example.com',
        'password': 'adminpass'
    }, follow_redirects=True)
    response = client.get('/dashboard_user', follow_redirects=True)
    data = response.data.decode('utf-8')
    assert 'permiso' in data or 'acceso' in data or 'admin' in data 