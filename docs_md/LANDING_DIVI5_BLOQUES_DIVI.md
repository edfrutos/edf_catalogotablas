# Divi 5: Centro de Mando (versión por bloques para Divi)

Esta guía está pensada para montar la landing en el constructor de Divi usando módulos estándar.

## Estructura recomendada en Divi

1. **Sección Hero**
   - Fila 1 columna
   - Módulo Texto (pill + título + subtítulo)
   - Módulo Botones (CTA principal + CTA secundaria)
2. **Sección Tabla de contenido + beneficios**
   - Fila 2 columnas
   - Columna izquierda: Módulo Texto (índice con anclas)
   - Columna derecha: Módulo Texto (beneficios)
3. **Sección 1 + 1.1**
   - Fila 1 columna
   - Módulo Texto
4. **Secciones 2.1, 2.2, 2.3, 2.4**
   - Fila 1 columna por sección
   - Módulo Texto en cada bloque
5. **Secciones 3, 4, 5**
   - Fila 1 columna por sección
   - Módulo Texto + Módulo Botón
6. **FAQ**
   - Módulo Acordeón o Toggle (4 preguntas)

---

## 0) CSS opcional (Módulo Código o CSS de página)

> Si prefieres estilos de tu tema/Divi, puedes omitir este bloque.

```css
.cm-pill{display:inline-block;padding:.3rem .65rem;border:1px solid #d8def0;border-radius:999px;font-size:.9rem}
.cm-kicker{color:#28b57a;font-weight:700;letter-spacing:.02em;font-size:.95rem}
.cm-lead{font-size:1.1rem}
.cm-card{border:1px solid #d8def0;border-radius:10px;padding:16px}
.cm-code{background:#0f172a;color:#e2e8f0;padding:12px;border-radius:8px;overflow:auto}
```

---

## 1) Hero (Módulo Texto)

Usa este contenido en un **Módulo Texto**:

```html
<p class="cm-pill">Divi 5 · Productividad de diseño</p>
<h1>Centro de Mando: crea, ajusta y navega con <code>Cmd + K</code></h1>
<p class="cm-lead">
  Ejecuta acciones complejas en segundos: añade elementos, aplica preajustes, abre modales y navega por tu sitio sin salir del teclado.
</p>
```

### Botones Hero (Módulo Botón o Botones)

- Botón 1: **Probar Divi 5 hoy** → `#seccion-3`
- Botón 2: **Ver ejemplos del Centro de Mando** → `#seccion-2`

---

## 2) Tabla de contenido (Módulo Texto)

Pon este bloque en la columna izquierda:

```html
<h2>Tabla de contenido</h2>
<ol>
  <li><a href="#seccion-1">El centro de mando</a></li>
  <li><a href="#seccion-11">Categorías de comandos</a></li>
  <li><a href="#seccion-2">Operadores de comando</a></li>
  <li><a href="#seccion-21">Comandos de cola</a></li>
  <li><a href="#seccion-22">Operadores de cola de comandos</a></li>
  <li><a href="#seccion-23">Combine ajustes preestablecidos y elementos en una sola cola</a></li>
  <li><a href="#seccion-24">Filtrar sobre la marcha</a></li>
  <li><a href="#seccion-3">Prueba Divi 5 hoy</a></li>
  <li><a href="#seccion-4">¿Has probado los nuevos módulos de menú de Divi 5?</a></li>
  <li><a href="#seccion-5">Más actualizaciones de Divi 5 están en camino</a></li>
</ol>
```

## 2b) Beneficios (Módulo Texto)

Pon este bloque en la columna derecha:

```html
<div class="cm-card">
  <h3>Qué resuelve</h3>
  <ul>
    <li><strong>Menos clics:</strong> pasas de menús largos a comandos directos.</li>
    <li><strong>Más velocidad:</strong> ejecuta secuencias completas en una cola.</li>
    <li><strong>Más control:</strong> define dónde y cómo se insertan elementos.</li>
    <li><strong>Más foco:</strong> reduces interrupciones y mantienes el ritmo.</li>
  </ul>
</div>
```

---

## 3) Sección 1: El centro de mando (Módulo Texto)

En la **Sección/Fila**, asigna ID CSS: `seccion-1`.

```html
<p class="cm-kicker">1. El centro de mando</p>
<h2>Piensa el resultado, escribe el comando, ejecútalo</h2>
<p>
  Si ya sabes lo que vas a construir antes de mover el ratón, el Centro de Mando se vuelve tu flujo natural.
  Abres con <code>Cmd + K</code>, escribes el objetivo y lo ejecutas en una sola acción.
</p>
<blockquote>
  “Añadir un módulo de descripción, añadir un grupo dentro, añadir dos módulos de botón dentro, aplicar mi preajuste principal…”
</blockquote>
<p>
  En lugar de varias interacciones manuales, puedes lanzar una secuencia y obtener la estructura completa al instante.
</p>
```

---

## 4) Sección 1.1: Categorías de comandos (Módulo Texto)

ID CSS de sección/fila: `seccion-11`.

```html
<p class="cm-kicker">1.1 Categorías de comandos</p>
<h2>Una sola entrada, múltiples tipos de acciones</h2>

<h3>Elemento</h3>
<p>Añade módulos y estructuras anidadas completas.</p>
<pre class="cm-code"><code>blurb &gt; group &gt; button *2</code></pre>

<h3>Modal</h3>
<p>Abre ventanas específicas como variables o exportación sin navegar por menús.</p>

<h3>Configuración</h3>
<p>Salta a grupos de opciones concretos, por ejemplo: <code>animación</code>.</p>

<h3>Ver</h3>
<p>Alterna modos visuales, breakpoints y wireframe en segundos.</p>

<h3>Modificar</h3>
<p>Duplicar, eliminar, copiar, cortar, pegar y restablecer desde comandos.</p>

<h3>Navegar</h3>
<p>Cambia de página o entra a áreas del sitio escribiendo su nombre.</p>

<h3>Preajuste</h3>
<p>Aplica preajustes directamente por nombre, incluso varios en cola.</p>
<pre class="cm-code"><code>Preajuste de descripción (Cmd+Intro)
Preajuste de borde (Cmd+Intro)
Preajuste de espaciado (Intro)</code></pre>

<h3>Página</h3>
<p>Acciones de nivel global: guardar, salir y vista previa.</p>
```

---

## 5) Sección 2: Operadores de comando (Módulo Texto)

ID CSS de sección/fila: `seccion-2`.

```html
<p class="cm-kicker">2. Operadores de comando</p>
<h2>Encadena acciones y define la estructura exacta</h2>
<p>
  El Centro de Mando permite colas de ejecución con operadores para construir diseños más complejos de forma predecible.
</p>
```

---

## 6) Sección 2.1: Comandos de cola (Módulo Texto)

ID CSS de sección/fila: `seccion-21`.

```html
<p class="cm-kicker">2.1 Comandos de cola</p>
<h3>Cómo encolar</h3>
<ol>
  <li>Ejecuta con <code>Cmd + Intro</code> para añadir un comando a la cola.</li>
  <li>Repite el paso para seguir sumando elementos o preajustes.</li>
  <li>Pulsa <code>Intro</code> para lanzar toda la cola.</li>
</ol>
```

---

## 7) Sección 2.2: Operadores de cola de comandos (Módulo Texto)

ID CSS de sección/fila: `seccion-22`.

```html
<p class="cm-kicker">2.2 Operadores de cola de comandos</p>
<h3>Operadores disponibles</h3>
<ul>
  <li><code>&gt;</code> coloca un elemento dentro del elemento anterior en la cola.</li>
  <li><code>*</code> multiplica elementos en la secuencia.</li>
  <li><code>^</code> coloca un elemento por encima del elemento editado.</li>
</ul>
<pre class="cm-code"><code>blurb &gt; button *2</code></pre>
```

---

## 8) Sección 2.3: Combinar preajustes y elementos (Módulo Texto)

ID CSS de sección/fila: `seccion-23`.

```html
<p class="cm-kicker">2.3 Combine ajustes preestablecidos y elementos en una sola cola</p>
<h3>Estructura + estilo en un mismo flujo</h3>
<p>Puedes combinar módulos y preajustes en la misma cola para crear y estilizar sin pasos intermedios.</p>
<pre class="cm-code"><code>Descripción &gt; Grupo &gt; Botón + Ajuste preestablecido principal *2</code></pre>
```

---

## 9) Sección 2.4: Filtrar sobre la marcha (Módulo Texto)

ID CSS de sección/fila: `seccion-24`.

```html
<p class="cm-kicker">2.4 Filtrar sobre la marcha</p>
<h3>Encuentra el comando correcto más rápido</h3>
<p>
  Usa el operador <code>:</code> para acotar resultados por categoría mientras escribes. Es especialmente útil
  cuando varios comandos comparten términos similares.
</p>
<pre class="cm-code"><code>modal</code></pre>
```

---

## 10) Sección 3: Prueba Divi 5 hoy (Módulo Texto + Botón)

ID CSS de sección/fila: `seccion-3`.

```html
<p class="cm-kicker">3. Prueba Divi 5 hoy</p>
<h2>Empieza en minutos, acelera desde el primer proyecto</h2>
<p>
  El Centro de Mando está diseñado para que pases de intención a ejecución en segundos.
  Abre con <code>Cmd + K</code>, escribe tu comando y continúa diseñando.
</p>
```

Botones recomendados:

- **Probar Divi 5 hoy** → URL real de producto
- **Ver demo del Centro de Mando** → URL real de demo/video

---

## 11) Sección 4: Nuevos módulos de menú (Módulo Texto + Botón)

ID CSS de sección/fila: `seccion-4`.

```html
<p class="cm-kicker">4. ¿Has probado los nuevos módulos de menú de Divi 5?</p>
<h2>Amplía tu navegación con más control visual</h2>
<ul>
  <li>Mayor flexibilidad para diseñar menús.</li>
  <li>Mejor consistencia entre estructura y experiencia.</li>
  <li>Integración natural con el flujo del Centro de Mando.</li>
</ul>
```

Botón recomendado:

- **Descubrir módulos de menú** → URL real de feature

---

## 12) Sección 5: Más actualizaciones en camino (Módulo Texto + Botón)

ID CSS de sección/fila: `seccion-5`.

```html
<p class="cm-kicker">5. Más actualizaciones de Divi 5 están en camino</p>
<h2>Producto vivo, mejoras continuas</h2>
<p>
  Divi 5 sigue evolucionando con nuevas capacidades de rendimiento, edición y productividad.
  Mantente atento a las siguientes publicaciones para incorporar mejoras apenas estén disponibles.
</p>
```

Botón recomendado:

- **Ver próximas actualizaciones** → URL real de roadmap/changelog

---

## 13) FAQ para módulo Acordeón/Toggle

Crea 4 toggles:

1. **¿Necesito ser un usuario avanzado?**  
   No. Puedes comenzar con comandos simples y avanzar hacia colas y operadores cuando quieras.
2. **¿Qué gano frente al flujo tradicional?**  
   Menos clics, más rapidez y mayor consistencia en tareas repetitivas.
3. **¿Puedo mezclar estructura y preajustes?**  
   Sí. Puedes crear elementos y aplicar estilos en una sola cola de comandos.
4. **¿También sirve para navegar por el sitio?**  
   Sí. Permite abrir páginas y áreas clave por nombre sin recorrer paneles.

---

## 14) Copy promocional final (Módulo Texto)

```html
<p>
  <strong>Divi 5 ya está aquí:</strong> abre el Centro de Mando con <code>Cmd + K</code>, crea estructuras completas
  en segundos y ejecuta tu flujo de diseño sin salir del teclado.
</p>
```

---

## Checklist de implementación en Divi

- [ ] Asignar IDs de sección para anclas internas (`seccion-1`, `seccion-2`, etc.).
- [ ] Sustituir URLs placeholder por URLs reales.
- [ ] Revisar jerarquía de títulos (H1 único, H2 por sección).
- [ ] Comprobar versión móvil (espaciado, botones, saltos de línea).
- [ ] Validar contraste y accesibilidad visual.
