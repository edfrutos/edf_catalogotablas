# Divi 5: Matriz de decision por audiencia y trafico (A/B)

Esta guia define **que variante mostrar (A o B)** segun el tipo de visitante y el contexto de campana para la landing del Centro de Mando.

- Variante **A** = mensaje de **velocidad** (menos clics, resultados rapidos).
- Variante **B** = mensaje de **control** (precision, operadores, estructura avanzada).

> Documento complementario de `LANDING_DIVI5_BLOQUES_DIVI_AB.md`.

---

## 1) Objetivo operativo

Asignar la variante con mayor probabilidad de conversion segun senales reales de trafico, sin improvisar cambios de copy en cada campana.

---

## 2) Variables de entrada para decidir variante

Usa estas senales en conjunto:

1. **Fuente y medio** (`utm_source`, `utm_medium`)
2. **Campana** (`utm_campaign`, `utm_content`)
3. **Tipo de usuario** (nuevo vs recurrente)
4. **Dispositivo** (mobile vs desktop)
5. **Comportamiento previo** (visitas a docs/tutoriales/funciones avanzadas)
6. **Intencion** (descubrimiento, comparacion, activacion)

---

## 3) Regla rapida (si necesitas decidir en 10 segundos)

- Si el trafico es **frio/generalista** -> **A**
- Si el trafico es **tecnico o caliente** (retorno, docs, tutoriales, features) -> **B**
- Si no hay datos suficientes -> **A** (control baseline)

---

## 4) Matriz principal de decision

| Segmento | Senales observables | Intencion dominante | Variante recomendada | CTA principal sugerido | KPI principal |
|---|---|---|---|---|---|
| Prospecting pago (Meta/TikTok/Display) | `utm_medium=paid_social`, audiencias amplias, usuario nuevo | Descubrimiento | **A** | Probar Divi 5 hoy | CTR hero |
| Search no branded (TOFU/MOFU) | keywords genericas, comparativas | Descubrimiento/consideracion | **A** | Empezar con el Centro de Mando | CTR hero |
| Search branded | busqueda de marca + features | Consideracion/activacion | **A/B** (test 50/50) | Probar Divi 5 hoy | CTR + CTA final |
| Retargeting de visitas a docs/tutoriales | visita previa a contenido tecnico | Activacion | **B** | Probar Centro de Mando en Divi 5 | CTR + scroll 75 |
| Email a base existente (producto) | usuarios ya suscritos, historial de uso | Activacion | **B** | Explorar operadores y colas | CTR secundario + CTA final |
| Comunidad tecnica (foros/dev) | trafico desde contenido tecnico | Evaluacion profunda | **B** | Explorar operadores y colas | Tiempo en pagina + scroll 75 |
| Afiliados/influencers generalistas | trafico mixto con baja profundidad inicial | Descubrimiento | **A** | Ver comandos en accion | CTR hero |
| Usuarios recurrentes sin consumo tecnico | retorna pero no visita docs avanzadas | Consideracion | **A** | Acelerar mi flujo en Divi 5 | CTR hero |
| Usuarios recurrentes con consumo tecnico | retorna + visita guias/funciones avanzadas | Activacion | **B** | Probar Centro de Mando en Divi 5 | CTA final |
| Mobile first | sesiones cortas, menor profundidad | Escaneo rapido | **A** | Probar Divi 5 hoy | CTR hero |
| Desktop + alta profundidad | sesiones largas, scroll alto | Evaluacion tecnica | **B** | Explorar operadores y colas | Scroll 75 + CTA final |

---

## 5) Matriz secundaria por nivel de madurez

| Madurez de audiencia | Descripcion | Variante base | Ajuste de CTA |
|---|---|---|---|
| Fria | No conoce bien Divi 5 ni Centro de Mando | A | Probar Divi 5 hoy |
| Tibia | Ya escucho sobre Divi 5, necesita claridad de valor | A (o A/B) | Empezar con el Centro de Mando |
| Caliente | Ya evalua funcionalidades concretas | B | Probar Centro de Mando en Divi 5 |
| Tecnica | Busca control, estructura, detalle operativo | B | Explorar operadores y colas |

---

## 6) Modelo de scoring para automatizar decision

Suma puntos por visitante:

### Score A (velocidad)

- +2 si usuario nuevo
- +2 si `utm_medium` es prospecting/pago frio
- +1 si mobile
- +1 si no hay visitas previas a docs/tutoriales tecnicos

### Score B (control)

- +2 si usuario recurrente
- +2 si hay visitas previas a docs/tutoriales/features avanzadas
- +1 si desktop
- +1 si `utm_campaign` o `utm_content` contiene `advanced`, `workflow`, `operators`, `preset`

### Regla final

- Si `Score B >= Score A + 1` -> mostrar **B**
- En cualquier otro caso -> mostrar **A**

---

## 7) Reglas UTM recomendadas

Define convencion para simplificar asignacion:

- Campanas TOFU: `utm_campaign=divi5_cmd_awareness` -> **A**
- Campanas MOFU: `utm_campaign=divi5_cmd_consideration` -> **A/B**
- Campanas BOFU/retargeting tecnico: `utm_campaign=divi5_cmd_activation` -> **B**

Keywords utiles en `utm_content` para forzar B:

- `operators`
- `advanced`
- `workflow`
- `presets`
- `productivity-pro`

---

## 8) Implementacion practica en Divi/WordPress

## Opcion 1 (simple)

- Mantener dos paginas publicadas:
  - `/divi5-centro-de-mando-a`
  - `/divi5-centro-de-mando-b`
- En campanas, enviar trafico segun matriz.

## Opcion 2 (recomendada)

- Una URL canonica (`/divi5-centro-de-mando`) + router de variante:
  - GTM/AB tool decide variante al cargar.
  - Guarda variante en cookie/localStorage por 7 dias para consistencia.

---

## 9) Eventos minimos por variante (GA4/GTM)

Registrar con parametro `variant`:

- `page_view_landing_cmd` (`variant=A|B`)
- `cta_hero_primary_click`
- `cta_hero_secondary_click`
- `scroll_50`
- `scroll_75`
- `faq_toggle_open`
- `cta_final_click`

Parametros recomendados:

- `variant`
- `segment` (frio, tibio, caliente, tecnico)
- `source_medium`
- `campaign`

---

## 10) Guardrails para no tomar malas decisiones

Antes de declarar ganador:

1. Mantener al menos 14 dias de experimento.
2. No cambiar simultaneamente layout completo + oferta + precio.
3. Revisar que no haya sesgo por dispositivo o fuente dominante.
4. Excluir trafico interno y QA.
5. Confirmar que el tracking de eventos sea consistente en A y B.

---

## 11) Playbook semanal de optimizacion

### Semana 1

- Validar tracking y reparto de trafico.
- Detectar segmentos con mayor diferencia de CTR.

### Semana 2

- Ajustar solo microcopy de CTA en el segmento mas grande.
- Mantener hero base para preservar lectura del test.

### Semana 3

- Optimizar bloque de objeciones segun FAQ mas abierta.
- Revisar impacto en `cta_final_click`.

### Semana 4

- Consolidar reglas por segmento.
- Promover variante ganadora a baseline por audiencia.

---

## 12) Tabla de decision final (resumen ejecutivo)

| Caso | Variante |
|---|---|
| Trafico frio o desconocido | **A** |
| Retorno con comportamiento tecnico | **B** |
| Campana branded sin claridad de perfil | **A/B 50/50** |
| Comunidad tecnica / docs avanzadas | **B** |
| Mobile con baja profundidad | **A** |
| Desktop con alta profundidad | **B** |

---

## 13) Checklist de despliegue

- [ ] Matriz compartida con equipo de marketing y producto.
- [ ] Convencion UTM documentada.
- [ ] Segmentos configurados en analitica.
- [ ] Variante asignada por segmento.
- [ ] QA de eventos por variante.
- [ ] Fecha de revision de resultados definida.
