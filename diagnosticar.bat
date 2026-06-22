@echo off
chcp 65001 >nul 2>&1
echo ===================================
echo  DIAGNOSTICO DE PUBLICACION
echo ===================================
python -c "import os,urllib.request,urllib.error; tp='dist/tokengenerarflipbook.txt' if os.path.exists('dist/tokengenerarflipbook.txt') else 'tokengenerarflipbook.txt'; rp='dist/repositorio.txt' if os.path.exists('dist/repositorio.txt') else 'repositorio.txt'; tok=open(tp,encoding='utf-8-sig').read().strip() if os.path.exists(tp) else ''; repo=open(rp,encoding='utf-8-sig').read().strip() if os.path.exists(rp) else 'dtabuyodesigner/generador_flipbook'; print('TOKEN:', ('SI, len='+str(len(tok))) if tok else 'NO ENCONTRADO', '  archivo:', tp); print('REPO :', repo); url='https://api.github.com/repos/'+repo+'/branches/gh-pages'; print('Probando:', url); req=urllib.request.Request(url); req.add_header('Authorization','token '+tok); req.add_header('User-Agent','diag'); req.add_header('Accept','application/vnd.github+json'); exec('try:\n r=urllib.request.urlopen(req,timeout=30); print(\'RESULTADO: CONEXION OK\')\nexcept urllib.error.HTTPError as e:\n print(\'RESULTADO: ERROR HTTP\', e.code, e.reason); print(e.read().decode(\'utf-8\',\'ignore\')[:300])\nexcept Exception as e:\n print(\'RESULTADO: ERROR DE RED O SSL:\', type(e).__name__, e)')"
echo.
pause
