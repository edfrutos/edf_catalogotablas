<?php
// Script de acceso directo para administrador
session_start();

// Configurar la sesión como administrador
$_SESSION['user_id'] = 'admin_id';
$_SESSION['username'] = 'administrator';
$_SESSION['email'] = 'admin@example.com';
$_SESSION['role'] = 'admin';
$_SESSION['logged_in'] = true;

// Mostrar mensaje de éxito
echo '<html>
<head>
    <meta charset="UTF-8">
    <title>Acceso Administrador</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
        .success { color: green; font-weight: bold; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; border-radius: 5px; }
        .btn { display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Acceso de Administrador</h1>
        <p class="success">¡Sesión de administrador configurada correctamente!</p>
        <p>Ahora puedes acceder al panel de administración.</p>
        <div>
            <a href="/admin/" class="btn">Ir al Panel de Administración</a>
            <a href="/" class="btn">Ir a la Página Principal</a>
        </div>
        <hr>
        <h3>Información de sesión:</h3>
        <pre>' . print_r($_SESSION, true) . '</pre>
    </div>
</body>
</html>';
?>
