# Divi 5: Centro de Mando (versión A/B orientada a conversión)

Esta guía complementa `LANDING_DIVI5_BLOQUES_DIVI.md` y está diseñada para montar un test A/B real en Divi con cambios de copy y jerarquía de contenido.

---

## 1) Objetivo del test

**Meta principal:** aumentar clics en CTA principal (**Probar Divi 5 hoy**) y mejorar la intención de uso del Centro de Mando.

**Métrica principal (Primary KPI):**

- CTR del CTA principal en hero.

**Métricas secundarias:**

- CTR de CTA secundario (demo/ejemplos).
- Scroll depth 50% y 75%.
- Interacción con FAQ.
- Click en CTA final.

---

## 2) Hipótesis

### Hipótesis A (velocidad)

Si el hero enfatiza ahorro de tiempo y menos clics, usuarios con dolor operativo harán clic más rápido en "Probar Divi 5 hoy".

### Hipótesis B (control)

Si el hero enfatiza precisión, estructura y control del flujo, usuarios avanzados y perfiles técnicos mostrarán mejor calidad de tráfico y mayor interacción.

---

## 3) Variante A (mensaje: velocidad inmediata)

### 3.1 Hero (Módulo Texto)

```html
<p class="cm-pill">Divi 5 · Menos clics, más resultados</p>
<h1>Diseña hasta más rápido con el Centro de Mando</h1>
<p class="cm-lead">
  Presiona <code>Cmd + K</code>, escribe el comando y ejecuta tareas complejas en segundos:
  crear elementos, aplicar preajustes y navegar sin romper tu flujo.
</p>
<ul>
  <li>Reduce pasos repetitivos.</li>
  <li>Construye estructuras completas en una sola secuencia.</li>
  <li>Mantén el foco de principio a fin.</li>
</ul>
```

### 3.2 Botones Hero (Módulo Botón)

- Primario: **Probar Divi 5 hoy**
- Secundario: **Ver comandos en acción**

### 3.3 Bloque de refuerzo corto bajo hero (Módulo Texto)

```html
<p><strong>Ideal para:</strong> diseñadores y equipos que quieren producir más páginas en menos tiempo.</p>
```

---

## 4) Variante B (mensaje: control y precisión)

### 4.1 Hero (Módulo Texto)

```html
<p class="cm-pill">Divi 5 · Flujo avanzado con control total</p>
<h1>Controla estructura y estilo desde un único comando</h1>
<p class="cm-lead">
  Con el Centro de Mando, defines exactamente cómo se crean y posicionan los elementos
  usando colas y operadores como <code>&gt;</code>, <code>*</code> y <code>^</code>.
</p>
<ul>
  <li>Mayor precisión en estructuras anidadas.</li>
  <li>Menos fricción al aplicar preajustes.</li>
  <li>Navegación instantánea entre páginas y áreas clave.</li>
</ul>
```

### 4.2 Botones Hero (Módulo Botón)

- Primario: **Probar Centro de Mando en Divi 5**
- Secundario: **Explorar operadores y colas**

### 4.3 Bloque de refuerzo corto bajo hero (Módulo Texto)

```html
<p><strong>Ideal para:</strong> usuarios avanzados que ya piensan en estructuras antes de hacer clic.</p>
```

---

## 5) Secciones intermedias recomendadas para ambas variantes

Mantén idénticas las secciones 1.1, 2.1, 2.2, 2.3, 2.4 para aislar el efecto del hero.

### 5.1 Bloque "Resultado en 10 segundos" (nuevo)

Ubicación sugerida: justo después del hero.

```html
<h2>De intención a ejecución en menos de 10 segundos</h2>
<pre class="cm-code"><code>blurb &gt; group &gt; button *2 + preajuste principal</code></pre>
<p>Una secuencia. Una ejecución. Estructura y estilo listos.</p>
```

### 5.2 Bloque de "objeciones" (nuevo)

Ubicación sugerida: antes de FAQ.

```html
<h2>¿Y si no soy usuario avanzado?</h2>
<p>
  Empieza con comandos simples y evoluciona gradualmente. El Centro de Mando acelera tanto flujos básicos
  como escenarios avanzados con operadores.
</p>
```

---

## 6) CTAs orientados a conversión

## Recomendación principal

Usar CTA con beneficio explícito y verbo de acción.

Opciones de CTA primario (test multivariante opcional):

1. **Probar Divi 5 hoy**
2. **Empezar con el Centro de Mando**
3. **Acelerar mi flujo en Divi 5**

Opciones de CTA secundario:

1. **Ver comandos en acción**
2. **Explorar ejemplos reales**
3. **Ver demo de 2 minutos**

Microcopy bajo botón principal:

```html
<small>Sin curva larga de aprendizaje. Abre con Cmd + K y empieza.</small>
```

---

## 7) Prueba social (bloque opcional recomendado)

Coloca este bloque después de la sección "Prueba Divi 5 hoy":

```html
<h2>Equipos que priorizan velocidad ya trabajan con este flujo</h2>
<p>Menos clics, menos fricción, más consistencia en páginas y componentes.</p>
<ul>
  <li>"Reducimos el tiempo de maquetación por página." — Equipo de Diseño</li>
  <li>"Ahora aplicamos estructura y estilo en una sola secuencia." — Frontend Lead</li>
</ul>
```

Si tienes datos reales, reemplaza frases por métricas verificables.

---

## 8) FAQ corta orientada a fricción de compra

Usa módulo Acordeón/Toggle con estas preguntas:

1. **¿Cuánto tardaré en adaptarme al Centro de Mando?**  
   Puedes empezar en minutos con comandos simples.
2. **¿Sirve si solo hago páginas básicas?**  
   Sí. Incluso en flujos simples, reduce clics y tiempo.
3. **¿Puedo usarlo para estructuras complejas?**  
   Sí. Las colas y operadores están hechas para eso.
4. **¿Me obliga a dejar el flujo visual tradicional?**  
   No. Es una capa adicional de productividad.

---

## 9) Implementación A/B en Divi (paso a paso)

1. Duplica la página base de la landing.
2. Nombra versiones internas:
   - `Landing CMD Divi5 - Variante A`
   - `Landing CMD Divi5 - Variante B`
3. Cambia solo:
   - Hero (headline, lead, bullets, texto CTA).
   - Bloque de refuerzo bajo hero.
4. Mantén igual el resto de secciones.
5. Configura reparto de tráfico 50/50 con tu herramienta de experimentación.
6. Lanza el test mínimo 14 días o hasta muestra estadística suficiente.

---

## 10) Esquema mínimo de eventos (analítica)

Si usas GTM/GA4, dispara estos eventos:

- `cta_hero_primary_click`
- `cta_hero_secondary_click`
- `scroll_50`
- `scroll_75`
- `faq_toggle_open`
- `cta_final_click`

Parámetros sugeridos:

- `variant`: `A` o `B`
- `page_type`: `landing_divi5_cmd`
- `cta_label`: texto del botón

---

## 11) Criterio para declarar ganador

Declara ganador cuando se cumplan ambos:

1. Mejora estadísticamente confiable en CTR del CTA principal.
2. Sin deterioro significativo en métricas secundarias (scroll, interacción, CTA final).

Si ambos ganan en segmentos distintos, considera personalización por audiencia:

- A para tráfico frío o generalista.
- B para audiencias técnicas/retorno.

---

## 12) Copys listos para test rápido (solo hero)

### A1

**Título:** Diseña más rápido con el Centro de Mando de Divi 5  
**Subtítulo:** Menos clics, más ejecución. Escribe, encola y publica.

### A2

**Título:** Haz en segundos lo que antes llevaba minutos  
**Subtítulo:** Cmd + K, comando, resultado.

### B1

**Título:** Precisión total para construir estructuras complejas  
**Subtítulo:** Controla jerarquía, posición y estilo con operadores y colas.

### B2

**Título:** Tu flujo avanzado, ahora sin fricción  
**Subtítulo:** Crea y estiliza desde un único punto de mando.

---

## 13) Checklist final de lanzamiento del experimento

- [ ] Variante A publicada.
- [ ] Variante B publicada.
- [ ] Eventos de analítica verificados en tiempo real.
- [ ] Segmentación de tráfico configurada al 50/50.
- [ ] Duración mínima definida.
- [ ] Criterio de éxito documentado antes de arrancar.
