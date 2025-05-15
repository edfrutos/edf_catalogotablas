<?php
// Establecer cabeceras para evitar problemas de caché
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");
header("X-Content-Type-Options: nosniff");

// Función para mostrar errores de forma amigable
function mostrar_error($mensaje, $detalles = null) {
    echo '<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Error - Panel de Emergencia</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
            .error { color: #721c24; background: #f8d7da; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
            .detalles { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 20px; font-family: monospace; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <h1>Error en el Panel de Emergencia</h1>
        <div class="error">' . htmlspecialchars($mensaje) . '</div>';
    
    if ($detalles) {
        echo '<div class="detalles">' . htmlspecialchars($detalles) . '</div>';
    }
    
    echo '<p><a href="panel_emergencia.php">Volver al panel</a></p>
    </body>
    </html>';
    exit;
}

// Función para mostrar página básica del panel
function mostrar_panel($titulo, $contenido, $mensajes = []) {
    echo '<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>' . htmlspecialchars($titulo) . ' - Panel de Emergencia</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background: #f4f6f9; }
            .container { width: 95%; max-width: 1200px; margin: 0 auto; padding: 20px; }
            header { background: #343a40; color: white; padding: 15px 0; margin-bottom: 20px; }
            .header-inner { display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 20px; }
            .panel { background: white; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }
            h1, h2, h3 { margin-top: 0; color: #343a40; }
            .success { color: #155724; background: #d4edda; padding: 10px; border-radius: 4px; margin-bottom: 15px; }
            .error { color: #721c24; background: #f8d7da; padding: 10px; border-radius: 4px; margin-bottom: 15px; }
            .info { color: #0c5460; background: #d1ecf1; padding: 10px; border-radius: 4px; margin-bottom: 15px; }
            .warning { color: #856404; background: #fff3cd; padding: 10px; border-radius: 4px; margin-bottom: 15px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            table, th, td { border: 1px solid #dee2e6; }
            th { background: #f8f9fa; padding: 10px; text-align: left; }
            td { padding: 10px; }
            .actions { display: flex; gap: 5px; }
            .btn { display: inline-block; padding: 8px 12px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; border: none; cursor: pointer; font-size: 14px; }
            .btn:hover { background: #0069d9; }
            .btn-danger { background: #dc3545; }
            .btn-danger:hover { background: #c82333; }
            .btn-success { background: #28a745; }
            .btn-success:hover { background: #218838; }
            .btn-warning { background: #ffc107; color: #212529; }
            .btn-warning:hover { background: #e0a800; }
            form { margin-bottom: 20px; }
            input, select, textarea { padding: 8px; margin-bottom: 10px; border: 1px solid #ced4da; border-radius: 4px; width: 100%; box-sizing: border-box; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            .form-row { margin-bottom: 15px; }
            .nav { list-style: none; padding: 0; margin: 0; display: flex; }
            .nav li { margin-right: 15px; }
            .nav a { color: white; text-decoration: none; }
            .nav a:hover { text-decoration: underline; }
            .footer { text-align: center; padding: 20px; color: #6c757d; background: #f8f9fa; margin-top: 20px; }
        </style>
    </head>
    <body>
        <header>
            <div class="header-inner">
                <h1>Panel Administrativo de Emergencia</h1>
                <ul class="nav">
                    <li><a href="panel_emergencia.php">Inicio</a></li>
                    <li><a href="panel_emergencia.php?accion=usuarios">Usuarios</a></li>
                    <li><a href="panel_emergencia.php?accion=crear_admin">Crear Admin</a></li>
                    <li><a href="panel_emergencia.php?accion=reparar">Reparar Sistema</a></li>
                </ul>
            </div>
        </header>
        
        <div class="container">';
        
    // Mostrar mensajes
    foreach ($mensajes as $tipo => $mensaje) {
        echo '<div class="' . $tipo . '">' . htmlspecialchars($mensaje) . '</div>';
    }
    
    echo '<div class="panel">
            <h2>' . htmlspecialchars($titulo) . '</h2>
            ' . $contenido . '
          </div>
        </div>
        
        <footer class="footer">
            <p>Panel Administrativo de Emergencia - Creado para restaurar acceso al sistema principal</p>
        </footer>
    </body>
    </html>';
    exit;
}

// Intentar conectar a MongoDB usando la extensión MongoDB para PHP
try {
    // Obtener la URI de MongoDB desde config.py
    $config_path = __DIR__ . '/config.py';
    $mongo_uri = null;
    
    if (file_exists($config_path)) {
        $config_content = file_get_contents($config_path);
        if (preg_match('/MONGO_URI\s*=\s*[\'"](.+?)[\'"]/', $config_content, $matches)) {
            $mongo_uri = $matches[1];
        }
    }
    
    // Si no se encontró en config.py, buscar en el archivo de entorno
    if (!$mongo_uri) {
        $env_path = '/etc/default/edefrutos2025';
        if (file_exists($env_path)) {
            $env_content = file_get_contents($env_path);
            if (preg_match('/MONGO_URI\s*=\s*(.+)/', $env_content, $matches)) {
                $mongo_uri = trim($matches[1]);
            }
        }
    }
    
    // Si aún no se encontró, usar el valor hardcodeado
    if (!$mongo_uri) {
        $mongo_uri = "mongodb+srv://edfrutos:rYjwUC6pUNrLtbaI@cluster0.pmokh.mongodb.net/app_catalogojoyero?retryWrites=true&w=majority";
    }
    
    // Verificar si la extensión MongoDB está disponible
    $mongo_extension_available = false;
    if (extension_loaded('mongodb')) {
        $mongo_extension_available = true;
        
        // Conectar a MongoDB
        $cliente = new MongoDB\Client($mongo_uri);
        $db_name = "app_catalogojoyero";
        $db = $cliente->$db_name;
        
        // Verificar la conexión a la base de datos
        $colecciones = $db->listCollections();
        $colecciones_nombres = [];
        foreach ($colecciones as $coleccion) {
            $colecciones_nombres[] = $coleccion->getName();
        }
    }
} catch (Exception $e) {
    // Manejar el error silenciosamente para mostrarlo después en la interfaz
    $error_conexion = $e->getMessage();
}

// Procesar formularios y acciones
$mensajes = [];
$accion = isset($_GET['accion']) ? $_GET['accion'] : 'inicio';

// Crear un usuario administrador (POST)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['accion']) && $_POST['accion'] === 'crear_admin') {
    if (!$mongo_extension_available) {
        $mensajes['error'] = "No se puede crear el usuario: la extensión MongoDB no está disponible.";
    } else {
        try {
            $email = isset($_POST['email']) ? trim($_POST['email']) : '';
            $password = isset($_POST['password']) ? trim($_POST['password']) : '';
            $username = isset($_POST['username']) ? trim($_POST['username']) : 'administrator';
            
            if (empty($email) || empty($password)) {
                $mensajes['error'] = "El email y la contraseña son obligatorios.";
            } else {
                // Verificar si el usuario ya existe
                $usuario_existente = $db->users->findOne(['email' => $email]);
                
                // Generar hash de contraseña (compatible con Werkzeug)
                $salt = bin2hex(random_bytes(8));
                $hashed_password = crypt($password, '$2a$12$' . $salt);
                
                if ($usuario_existente) {
                    // Actualizar usuario existente
                    $db->users->updateOne(
                        ['email' => $email],
                        ['$set' => [
                            'password' => $hashed_password,
                            'username' => $username,
                            'role' => 'admin',
                            'updated_at' => new MongoDB\BSON\UTCDateTime()
                        ]]
                    );
                    $mensajes['success'] = "Usuario administrador actualizado correctamente.";
                } else {
                    // Crear nuevo usuario
                    $db->users->insertOne([
                        'email' => $email,
                        'password' => $hashed_password,
                        'username' => $username,
                        'role' => 'admin',
                        'created_at' => new MongoDB\BSON\UTCDateTime(),
                        'updated_at' => new MongoDB\BSON\UTCDateTime()
                    ]);
                    $mensajes['success'] = "Usuario administrador creado correctamente.";
                }
            }
        } catch (Exception $e) {
            $mensajes['error'] = "Error al crear/actualizar usuario: " . $e->getMessage();
        }
    }
}

// Contenido según la acción solicitada
$contenido = '';
$titulo = '';

switch ($accion) {
    case 'usuarios':
        $titulo = 'Gestión de Usuarios';
        
        if (!$mongo_extension_available) {
            $contenido = "<p>La extensión MongoDB de PHP no está disponible. No se pueden mostrar los usuarios.</p>";
        } else {
            if (isset($error_conexion)) {
                $contenido = "<p class='error'>Error de conexión a MongoDB: {$error_conexion}</p>";
            } else {
                // Obtener usuarios
                $usuarios = $db->users->find([]);
                
                $contenido = "
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Email</th>
                            <th>Username</th>
                            <th>Rol</th>
                        </tr>
                    </thead>
                    <tbody>";
                
                $contador = 0;
                foreach ($usuarios as $usuario) {
                    $contador++;
                    $id = isset($usuario->_id) ? (string)$usuario->_id : 'N/A';
                    $email = isset($usuario->email) ? htmlspecialchars($usuario->email) : 'N/A';
                    $username = isset($usuario->username) ? htmlspecialchars($usuario->username) : 'N/A';
                    $role = isset($usuario->role) ? htmlspecialchars($usuario->role) : 'user';
                    
                    $contenido .= "
                        <tr>
                            <td>{$id}</td>
                            <td>{$email}</td>
                            <td>{$username}</td>
                            <td>{$role}</td>
                        </tr>";
                }
                
                $contenido .= "
                    </tbody>
                </table>";
                
                if ($contador === 0) {
                    $contenido = "<p>No se encontraron usuarios en la base de datos.</p>";
                }
            }
        }
        break;
        
    case 'crear_admin':
        $titulo = 'Crear Usuario Administrador';
        
        if (!$mongo_extension_available) {
            $contenido = "<p class='error'>La extensión MongoDB de PHP no está disponible. No se puede crear el administrador.</p>";
        } else {
            $contenido = "
            <form method='post' action='panel_emergencia.php'>
                <input type='hidden' name='accion' value='crear_admin'>
                
                <div class='form-row'>
                    <label for='email'>Email:</label>
                    <input type='email' id='email' name='email' value='admin@example.com' required>
                </div>
                
                <div class='form-row'>
                    <label for='username'>Nombre de usuario:</label>
                    <input type='text' id='username' name='username' value='administrator'>
                </div>
                
                <div class='form-row'>
                    <label for='password'>Contraseña:</label>
                    <input type='password' id='password' name='password' value='admin123' required>
                </div>
                
                <button type='submit' class='btn btn-success'>Crear/Actualizar Administrador</button>
            </form>";
        }
        break;
        
    case 'reparar':
        $titulo = 'Reparar Sistema';
        $contenido = "<p>Esta función intentará reparar problemas comunes del sistema.</p>";
        
        // Intentar ejecutar el script repair_admin.py
        $output = [];
        $codigo = 0;
        $comando = "cd " . escapeshellarg(__DIR__) . " && python3 repair_admin.py 2>&1";
        exec($comando, $output, $codigo);
        
        if ($codigo === 0) {
            $contenido .= "<div class='success'>El script de reparación se ejecutó correctamente.</div>";
        } else {
            $contenido .= "<div class='error'>El script de reparación falló con código {$codigo}.</div>";
        }
        
        $contenido .= "<h3>Resultado:</h3><pre>" . htmlspecialchars(implode("\n", $output)) . "</pre>";
        
        // Intentar reiniciar servicios
        $contenido .= "<h3>Intentando reiniciar servicios...</h3>";
        
        $output_restart = [];
        $codigo_restart = 0;
        exec("sudo systemctl restart edefrutos2025 apache2 2>&1", $output_restart, $codigo_restart);
        
        if ($codigo_restart === 0) {
            $contenido .= "<div class='success'>Los servicios se reiniciaron correctamente.</div>";
        } else {
            $contenido .= "<div class='error'>Error al reiniciar servicios.</div>";
            $contenido .= "<pre>" . htmlspecialchars(implode("\n", $output_restart)) . "</pre>";
        }
        break;
        
    default: // inicio
        $titulo = 'Información del Sistema';
        
        $contenido = "<h3>Estado de la conexión a MongoDB</h3>";
        
        if (!$mongo_extension_available) {
            $contenido .= "<p class='error'>La extensión MongoDB de PHP no está disponible. Este panel tiene funcionalidad limitada.</p>";
        } else if (isset($error_conexion)) {
            $contenido .= "<p class='error'>Error de conexión a MongoDB: {$error_conexion}</p>";
        } else {
            $contenido .= "<p class='success'>Conexión a MongoDB establecida correctamente.</p>";
            $contenido .= "<p>Base de datos: {$db_name}</p>";
            $contenido .= "<p>Colecciones disponibles: " . implode(', ', $colecciones_nombres) . "</p>";
        }
        
        $contenido .= "<h3>Información del servidor</h3>";
        $contenido .= "<p>Servidor: " . htmlspecialchars($_SERVER['SERVER_SOFTWARE']) . "</p>";
        $contenido .= "<p>PHP version: " . phpversion() . "</p>";
        
        $contenido .= "<h3>Archivos de configuración</h3>";
        $contenido .= "<ul>";
        
        if (file_exists(__DIR__ . '/config.py')) {
            $contenido .= "<li class='success'>config.py - Disponible</li>";
        } else {
            $contenido .= "<li class='error'>config.py - No disponible</li>";
        }
        
        if (file_exists('/etc/default/edefrutos2025')) {
            $contenido .= "<li class='success'>/etc/default/edefrutos2025 - Disponible</li>";
        } else {
            $contenido .= "<li class='error'>/etc/default/edefrutos2025 - No disponible</li>";
        }
        
        $contenido .= "</ul>";
        
        $contenido .= "<h3>Acciones rápidas</h3>";
        $contenido .= "<a href='panel_emergencia.php?accion=reparar' class='btn btn-warning'>Ejecutar reparación automática</a> ";
        $contenido .= "<a href='panel_emergencia.php?accion=crear_admin' class='btn btn-success'>Crear/Actualizar administrador</a>";
        break;
}

// Mostrar el panel
mostrar_panel($titulo, $contenido, $mensajes);
?>
