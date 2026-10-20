# CleanYourTV Projectivy

Fork de [CleanYourTV](https://github.com/Gathin23/cleanyourtv) adaptado para usar **Projectivy Launcher** como pantalla de inicio de Google TV. Projectivy es una aplicación independiente: este repositorio no la compila, distribuye ni modifica. El objetivo es conservar su configuración y asignarla como **HOME** de Android para que el botón Inicio y el arranque completo abran Projectivy.

El cambio se comprobó en una **TCL 75A400 Pro NXTVISION**, Android TV 14, placa `tcl9618`, producto `G08_4K_GB_NF`, compilación `UTT2.250416.001 AU02`. Tras desactivar LauncherX y, cuando tomó HOME, el componente de recuperación `setupwraith`, Projectivy abrió con el botón Inicio y después de un reinicio completo. Los botones físicos de Fuentes y Ajustes siguieron funcionando. **No se ha comprobado un corte eléctrico real** ni se garantiza el mismo comportamiento en otro firmware.

## Qué hace

1. Comprueba que Projectivy (`com.spocky.projengmenu`) ya esté instalado y que pueda abrir `/.ui.home.MainActivity`.
2. Lee el HOME actual, el estado de LauncherX y setupwraith, la versión de firmware y el dueño de las redes Wi-Fi guardadas.
3. Guarda el estado original en un archivo JSON local **antes** de modificar la TV.
4. Asigna Projectivy a HOME y al rol HOME, y desactiva LauncherX **solo para el usuario 0**.
5. Si setupwraith toma HOME, lo desactiva y vuelve a asignar Projectivy.
6. Verifica que Android resuelva HOME a Projectivy. Si falla, intenta restaurar LauncherX y el HOME anterior.

No instala APKs, no desinstala paquetes, no cambia accesibilidad, no activa autoinicio y no ejecuta una lista de debloat. Las preferencias, filas y aplicaciones de Projectivy se configuran en la propia app. La configuración de accesibilidad puede desactivarse en algunas TCL al reiniciar; ser el HOME real evita depender de ella para el arranque o el botón Inicio.

## Antes de empezar

- TV Google TV con **Projectivy instalado y configurado**. Ábrelo una vez desde Apps.
- Computadora con Python 3 y [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools) (`adb` en PATH).
- TV y computadora en una red de confianza; activa **Opciones para desarrolladores → Depuración inalámbrica** y autoriza la computadora en la pantalla de la TV.
- Acceso físico al control de la TV y a Ajustes, por si hay que volver a activar el inicio original.
- Usa el puerto **actual** que muestra Depuración inalámbrica. En Android 14 puede cambiar después de cada reinicio. No asumas que es 5555.

La herramienta automatizada reconoce únicamente `com.google.android.apps.tv.launcherx` como inicio original. Se detiene si encuentra otro HOME, un selector de launcher, un firmware diferente al de su copia de seguridad o si no puede comprobar la propiedad de las redes Wi-Fi antes de tocar setupwraith. En otros modelos, revisa primero sus componentes HOME y adapta el procedimiento manualmente.

## Aplicar

```bash
adb connect 192.168.100.107:PUERTO_ACTUAL
adb devices
python3 tools/projectivy.py status --serial 192.168.100.107:PUERTO_ACTUAL
python3 tools/projectivy.py apply --serial 192.168.100.107:PUERTO_ACTUAL --backup backup/projectivy-home.json
```

Sustituye la IP y el puerto por los que muestre **tu** TV. Si Android pide emparejamiento, usa `adb pair IP:PUERTO_DE_EMPAREJAMIENTO` con el código que muestre la TV y después `adb connect IP:PUERTO_DE_DEPURACIÓN`. Son dos puertos distintos. Si aparece `unauthorized`, acepta el aviso en pantalla y repite `adb connect`.

El archivo `backup/projectivy-home.json` contiene el HOME y el firmware original. Consérvalo. La herramienta se niega a sobrescribirlo para no perder el estado previo. **Si ya hiciste el cambio manualmente, no crees una copia como si reflejara el estado anterior.** `status` sí sirve para revisar esa TV.

Después de aplicar, comprueba en la TV: botón Inicio, Fuentes/Entradas y Ajustes. Reinicia completamente y comprueba que Projectivy aparezca **sin pulsar Inicio**. Si solo pruebas suspensión, la prueba no confirma el arranque en frío. La depuración inalámbrica puede cambiar de puerto tras reiniciar.

## Restaurar el inicio original

```bash
adb connect 192.168.100.107:PUERTO_ACTUAL
python3 tools/projectivy.py restore --serial 192.168.100.107:PUERTO_ACTUAL --backup backup/projectivy-home.json
```

La restauración vuelve a habilitar los componentes que estaban habilitados en la copia y asigna el HOME original. No borra Projectivy ni sus ajustes. Si la TV perdió la conexión y ya no aparece HOME, vuelve a conectar ADB por el nuevo puerto o mediante USB. Para la TCL indicada, la recuperación manual es:

```bash
adb -s IP:PUERTO shell pm enable --user 0 com.google.android.tungsten.setupwraith
adb -s IP:PUERTO shell pm enable --user 0 com.google.android.apps.tv.launcherx
adb -s IP:PUERTO shell cmd package set-home-activity com.google.android.apps.tv.launcherx/.home.HomeActivity
adb -s IP:PUERTO shell cmd role add-role-holder android.app.role.HOME com.google.android.apps.tv.launcherx
```

Usa esos comandos manuales solo si coinciden con el HOME y los componentes que tenía tu TV. La copia JSON es la fuente de verdad para la restauración automatizada.

## Por qué se revisa setupwraith y el Wi-Fi

En la TCL probada, al desactivar LauncherX, `com.google.android.tungsten.setupwraith/.RecoveryActivity` quedó como candidato HOME y apareció la pantalla de Google TV. Fue necesario desactivar también setupwraith para que Projectivy resolviera HOME. Si una red Wi-Fi fue guardada por ese componente durante la configuración inicial, Android puede eliminarla al desactivarlo y cortar ADB. La herramienta lee `dumpsys wifi` y se detiene si detecta que setupwraith es dueño de una red o no puede determinarlo. En nuestra TV se olvidó y reconectó la red desde Ajustes antes de proceder.

En este firmware TCL, el permiso interno `AUTO_START` y `accessibility_enabled` se restablecían tras reiniciar. Por eso este flujo usa el HOME del sistema. No afirmamos que Projectivy no necesite accesibilidad para **otras** funciones opcionales.

## Debloat y contenido heredado

El cambio de HOME no requiere desactivar telemetría, Chromecast, actualizaciones, TV en vivo ni otros paquetes. Las listas en [`examples/`](examples/) pertenecen a otros televisores; **no apliques la lista de TCL C755 o QM6K a la A400 Pro** por compartir placa o versión. Si quieres debloat, revisa cada paquete de tu equipo y usa [`tools/disable.sh`](tools/disable.sh) y [`tools/restore.sh`](tools/restore.sh) de forma independiente, con sus propias copias.

El launcher estilo Apple TV, sus temas, scripts de compilación, ejemplos, pruebas y documentación originales permanecen en el fork como contenido heredado. El flujo principal de este fork es Projectivy. Consulta [la documentación original](README.upstream.md) si necesitas esas herramientas; sus instrucciones sobre construir `com.gathin.tvhome` **no forman parte del procedimiento Projectivy**. [`PROMPT.md`](PROMPT.md) contiene el encargo actualizado para un asistente técnico.

Al terminar, desactiva Depuración inalámbrica en la TV si ya no la necesitas. Un cambio de firmware puede volver a habilitar LauncherX o alterar prioridades HOME; en ese caso revisa `status` antes de repetir pasos.
