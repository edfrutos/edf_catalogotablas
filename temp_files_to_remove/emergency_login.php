<?php
// Script de emergencia para acceso administrativo
// Crear conexión directa a MongoDB
$mongo_uri = getenv('MONGO_URI');
if (!$mongo_uri) {
    // Si no está disponible como variable de entorno, intentar leerlo desde config.py
    $config_file = file_get_contents(__DIR__ . '/config.py');
    preg_match('/MONGO_URI\s*=\s*[\'"](.+?)[\'"]/', $config_file, $matches);
    if (isset($matches[1])) {
        $mongo_uri = $matches[1];
    }
}

// Función para mostrar mensajes de error
function show_error($message) {
    header('Content-Type: text/html; charset=utf-8');
    echo '<!DOCTYPE html>
    <html>
    <head>
        <title>Error de Acceso de Emergencia</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }
            .error { color: red; background: #ffeeee; padding: 10px; border: 1px solid #ff0000; }
            .info { color: blue; background: #eeeeff; padding: 10px; border: 1px solid #0000ff; }
            pre { background: #f4f4f4; padding: 10px; overflow: auto; }
        </style>
    </head>
    <body>
        <h1>Error de Acceso de Emergencia</h1>
        <div class="error">' . htmlspecialchars($message) . '</div>
    </body>
    </html>';
    exit;
}

// Verificar que tenemos la URI de MongoDB
if (empty($mongo_uri)) {
    show_error("No se pudo obtener la URI de MongoDB. Verifica la configuración.");
}

// Intentar conectar a MongoDB
try {
    $mongo = new MongoDB\Client($mongo_uri);
    $db_name = parse_url($mongo_uri, PHP_URL_PATH);
    $db_name = ltrim($db_name, '/');
    $db = $mongo->selectDatabase($db_name);
    $users = $db->users;
    
    // Buscar el usuario administrador
    $admin = $users->findOne(['email' => 'admin@example.com']);
    
    if (!$admin) {
        show_error("No se encontró el usuario administrador en la base de datos.");
    }
    
    // Crear cookie de sesión directamente (esto es solo para emergencias)
    session_start();
    $_SESSION['user_id'] = (string)$admin->_id;
    $_SESSION['email'] = $admin->email;
    $_SESSION['username'] = isset($admin->username) ? $admin->username : 'administrator';
    $_SESSION['role'] = isset($admin->role) ? $admin->role : 'admin';
    $_SESSION['logged_in'] = true;
    
    // Redirigir al dashboard
    header("Location: /admin/dashboard");
    exit;
    
} catch (Exception $e) {
    show_error("Error al conectar con MongoDB: " . $e->getMessage());
}
?>
