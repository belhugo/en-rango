# En Rango

**Informe personalizado de glucosa a partir del CSV de LibreView.** Cargás el archivo, elegís las fechas que quieras (el informe oficial solo ofrece intervalos de hasta 90 días contados hacia atrás desde hoy, sin poder elegir las fechas) y ves el tiempo en rango, el patrón de glucosa, un calendario y los eventos de glucosa baja. Todo se procesa en el navegador: **los datos no salen del dispositivo**.

🔗 **En vivo:** https://enrango.netlify.app/ (tiene un botón para probarlo con datos de ejemplo)

> Herramienta informativa, sin relación con Abbott. FreeStyle Libre y LibreView son marcas de Abbott. No es un producto sanitario ni reemplaza el informe oficial ni la interpretación de un profesional de la salud.

*[English summary below](#in-english)*

<!-- Agregá acá una captura: docs/captura.png (hacela con los datos de ejemplo, nunca con datos reales) -->

## Qué hace

- **Período a gusto:** rango de fechas libre y atajos (14 días, 30, 90, 6 meses, 1 año, todo).
- **Tiempo en rango:** muy alto, alto, en rango, bajo y muy bajo, con las metas del consenso internacional y los totales de bajos y altos agrupados como en el informe oficial.
- **Rangos ajustables:** los cuatro límites se pueden cambiar y la preferencia se recuerda en el navegador.
- **Indicadores:** glucosa promedio, GMI (en % y en mmol/mol), variabilidad (CV) y sensor activo.
- **Comparación** con el período anterior de la misma duración (solo si hay datos comparables).
- **Gráficos:** patrón de glucosa (mediana y banda de percentiles 5–95), momentos del día, tendencia diaria.
- **Calendario** con el promedio y el % en rango de cada día; al tocar un día se abre su curva de 24 horas.
- **Eventos de glucosa baja** con fecha, hora, duración y valor mínimo.
- **Copiar resumen** al portapapeles e **imprimir / guardar PDF** (hoja A4, con todos los meses del período).
- Pensada para **celular**: un mes del calendario por vez, ejes de los gráficos que se adaptan al ancho.

## Privacidad (cómo está resuelta)

- El CSV se lee con `FileReader` + PapaParse en el navegador. No hay backend, base de datos, analítica ni cookies.
- En producción, una **política de seguridad de contenido (CSP)** bloquea cualquier conexión de salida (`connect-src 'none'`) y solo permite cargar scripts, estilos y fuentes del propio sitio. Se aplica por cabecera (`netlify/_headers`) y, como respaldo, dentro del HTML.
- Las librerías (Chart.js, PapaParse) y las fuentes se sirven desde el propio sitio: no se le avisa a ningún tercero que alguien abrió la página.
- Lo único que se guarda en el navegador (`localStorage`) son los cuatro **límites de rango** que el usuario ajuste. Nunca las lecturas.

## Formato de datos admitido

CSV exportado de LibreView. Se reconoce la fila de encabezados y estas columnas, en español o en inglés:

| Dato | Encabezado (ejemplos) |
| --- | --- |
| Fecha y hora | `Marca de hora del dispositivo` / `Device Timestamp` |
| Lecturas automáticas | `Historial de glucosa mg/dL` / `Historic Glucose mg/dL` |
| Escaneos manuales | `Escanear glucosa mg/dL` / `Scan Glucose mg/dL` |

- Las fechas pueden venir como `DD-MM-AAAA` o `MM-DD-AAAA`; se detecta solo (hay un selector para forzarlo).
- Por defecto solo cuentan las **lecturas automáticas**, como en el informe oficial; los escaneos son opcionales.
- Si el archivo está en mmol/L se convierte a mg/dL.
- Probado con la exportación en español de FreeStyle LibreLink. Otros idiomas u otros dispositivos pueden traer columnas distintas y no se reconocerían.

## Cálculos

- **Rangos por defecto:** muy bajo <54, bajo 54–69, en rango 70–180, alto 181–250, muy alto >250 mg/dL.
- **Metas** (consenso internacional, adultos con diabetes tipo 1 y 2): en rango >70 %, bajo+muy bajo <4 %, muy bajo <1 %, alto+muy alto <25 %, muy alto <5 %. Con rangos personalizados las metas se siguen mostrando, pero son las generales.
- **GMI (%)** = 3,31 + 0,02392 × glucosa media (mg/dL). **GMI (mmol/mol)** = 12,71 + 4,70587 × glucosa media (mmol/L).
- **CV** = desvío estándar / media. **Sensor activo** = lecturas recibidas sobre las esperadas (una cada 15 minutos).
- **Evento de glucosa baja:** dos o más lecturas automáticas seguidas por debajo del límite inferior (al menos 15 minutos).

## Decisiones técnicas

- **HTML + JavaScript sin framework**, en un solo archivo fuente (`index.html`) para poder abrirlo con doble clic mientras se desarrolla.
- **Chart.js** para los gráficos, **PapaParse** para el CSV, **Tailwind CSS** para los estilos.
- En desarrollo usa CDN; el script `tools/build.py` genera la versión de producción: Tailwind compilado y minificado (~15 KB), librerías y fuentes locales, y el JavaScript en un archivo aparte para poder usar `script-src 'self'`.
- **Impresión:** `@page` en A4; los gráficos se redibujan al ancho de la hoja justo antes de imprimir (evento `beforeprint`), porque en el celular quedaban del ancho de la pantalla.
- **Formato de fechas en Argentina** (DD/MM/AAAA) en todos los textos. Los campos de fecha nativos siguen el idioma del navegador.

## Desarrollo

```bash
# 1. Para desarrollar: abrí index.html en el navegador (usa CDN, necesita internet).

# 2. Para generar la versión de producción:
npm install
python3 tools/build.py          # crea dist/ ; con --zip también en-rango-netlify.zip
```

Hacen falta Node.js y Python 3. Para publicar, subí la carpeta `dist/` a Netlify (arrastrándola en netlify.com/drop o desde el panel «Deploys»). El archivo `_headers` tiene que quedar en la raíz de lo que se sube.

`tools/og.html` es el origen de la imagen de vista previa (`og.png`, 1200 × 630); se abre en el navegador y se captura.

## Estado de validación

- [x] Resultados contrastados contra un informe oficial de LibreView del mismo período (en rango, promedio, GMI).
- [x] Lectura del CSV probada con las columnas reales de la exportación en español.
- [x] Política de seguridad probada en un navegador real, sin bloqueos ni errores de consola.
- [x] Impresión probada en un teléfono real.

## Licencia

[MIT](LICENSE): se puede usar, copiar, modificar y distribuir, incluso con fines comerciales, conservando el aviso de copyright.

Dependencias de terceros: Chart.js, PapaParse y Tailwind CSS (MIT); fuentes Bricolage Grotesque e Instrument Sans (SIL Open Font License). FreeStyle Libre y LibreView son marcas de Abbott; este proyecto no tiene relación con ella.

## Autor

Desarrollado por [HB Systems](https://hbsystems.com.ar/), con asistencia de IA (Claude, de Anthropic).

---

### In English

**En Rango** is a privacy-first, client-side web app that turns a LibreView (FreeStyle Libre) CSV export into a custom-period glucose report: time in range, an ambulatory glucose profile, a calendar with per-day curves, low-glucose events and a printable A4 PDF. Everything runs in the browser; a strict Content Security Policy blocks any outbound request. It is an informational tool, not a medical device, and is not affiliated with Abbott.
