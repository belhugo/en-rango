#!/usr/bin/env python3
"""Genera dist/ (la versión para publicar) a partir de index.html.

Uso:   npm install && python3 tools/build.py [--zip]

- Saca los scripts y fuentes de CDN y los reemplaza por copias locales (nada de terceros en producción).
- Compila Tailwind en un solo CSS minificado.
- Separa el JavaScript en assets/app.js para poder usar una política de seguridad estricta (script-src 'self').
- Copia netlify/_headers (cabeceras de seguridad) y og.png (vista previa al compartir el link).
"""
import os, re, shutil, subprocess, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NM = 'node_modules'

src = open('index.html', encoding='utf-8').read()
style = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
script = re.findall(r'<script>(.*?)</script>', src, re.S)[-1]

html = src
for pat in [r'<script src="https://cdn\.tailwindcss\.com"></script>\n',
            r'<script src="https://cdnjs[^"]*PapaParse[^"]*"></script>\n',
            r'<script src="https://cdnjs[^"]*Chart\.js[^"]*"></script>\n',
            r'<link rel="stylesheet" href="https://fonts\.googleapis[^>]*>\n']:
    html = re.sub(pat, '', html)
html = re.sub(r'<style>.*?</style>', '<link rel="stylesheet" href="assets/app.css">', html, flags=re.S)
html = re.sub(r'<script>.*?</script>',
              '<script src="assets/papaparse.min.js"></script>\n<script src="assets/chart.umd.js"></script>\n<script src="assets/app.js"></script>',
              html, flags=re.S)

# En producción la política completa también va dentro del HTML (respaldo de _headers).
CSP_DEV = '<meta http-equiv="Content-Security-Policy" content="connect-src \'none\'">'
CSP_PROD = ('<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'self\'; '
            'style-src \'self\' \'unsafe-inline\'; font-src \'self\'; img-src \'self\' data:; connect-src \'none\'; '
            'base-uri \'none\'; form-action \'none\'">')
assert html.count(CSP_DEV) == 1, 'No encontré la etiqueta CSP de desarrollo en index.html'
html = html.replace(CSP_DEV, CSP_PROD)
assert not re.search(r'(src|href)="https?://', html), 'Quedó una carga externa en el HTML'

shutil.rmtree('dist', ignore_errors=True)
os.makedirs('dist/assets/fonts')
open('dist/index.html', 'w', encoding='utf-8').write(html)
open('dist/assets/app.js', 'w', encoding='utf-8').write(script.strip() + '\n')
shutil.copy(f'{NM}/papaparse/papaparse.min.js', 'dist/assets/')
shutil.copy(f'{NM}/chart.js/dist/chart.umd.js', 'dist/assets/')
FONTS = [('Bricolage Grotesque', 'bricolage-grotesque', [700, 800]), ('Instrument Sans', 'instrument-sans', [400, 500, 600])]
css_fonts = ''
for fam, pkg, weights in FONTS:
    for w in weights:
        f = f'{pkg}-latin-{w}-normal.woff2'
        shutil.copy(f'{NM}/@fontsource/{pkg}/files/{f}', 'dist/assets/fonts/')
        css_fonts += f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:normal;font-display:swap;src:url(fonts/{f}) format('woff2');}}\n"
shutil.copy('og.png', 'dist/og.png')
shutil.copy('netlify/_headers', 'dist/_headers')

open('tools/.input.css', 'w').write('@tailwind base;\n@tailwind components;\n@tailwind utilities;\n' + css_fonts + style)
npx = 'npx.cmd' if sys.platform == 'win32' else 'npx'
subprocess.run([npx, 'tailwindcss', '-c', 'tools/tailwind.config.js', '-i', 'tools/.input.css', '-o', 'dist/assets/app.css', '--minify'], check=True)
subprocess.run(['node', '--check', 'dist/assets/app.js'], check=True)

if '--zip' in sys.argv:
    out = 'en-rango-netlify.zip'
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for r, _, files in os.walk('dist'):
            for f in files:
                p = os.path.join(r, f)
                z.write(p, os.path.join('en-rango', os.path.relpath(p, 'dist')))
    print('Creado', out)
print('Listo: dist/ (subí esa carpeta a Netlify)')
