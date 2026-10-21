# CleanYourTV con Projectivy

> **Variante de [CleanYourTV](https://github.com/Gathin23/cleanyourtv), creado por [Gathin23](https://github.com/Gathin23).** Este fork conserva el enfoque reversible de ADB y usa [Projectivy Launcher, de Spocky](https://github.com/spocky/miproja1), como inicio predeterminado. No es una versión oficial de ninguno de los dos proyectos.

![Ejemplo público de la interfaz de Projectivy con accesos y canales](https://projectivylauncher.com/assets/screenshots/channels.jpg)

*Captura demostrativa del [sitio de Projectivy](https://projectivylauncher.com/); no corresponde a nuestra TCL ni a su configuración personal.*

![Ejemplo público de Projectivy con categorías de aplicaciones](https://projectivylauncher.com/assets/screenshots/cat.jpg)

*Otra configuración de muestra publicada por [Projectivy](https://projectivylauncher.com/). La apariencia final depende de los ajustes de cada usuario.*

Esta variante usa **Projectivy Launcher** como pantalla de inicio de Google TV. Projectivy es una aplicación independiente: este repositorio no la compila, distribuye ni modifica. El objetivo es conservar su configuración y asignarla como **HOME** de Android para que el botón Inicio y el arranque completo abran Projectivy. Al hacerlo, desactiva el inicio principal de Google TV (`LauncherX`) para el usuario 0; también puede desactivar `setupwraith` si reclama HOME.

## Modelos comprobados

| Modelo | Firmware observado | Resultado |
| --- | --- | --- |
| TCL 75A400 Pro NXTVISION | Android TV 14, `G08_4K_GB_NF`, `UTT2.250416.001 AU02` | Projectivy abrió con Inicio y tras reiniciar; Fuentes y Ajustes funcionaron. |
| TCL 43Q5K | Android TV 12, `G10_4K_GB_NF_32BIT`, `STT2.230203.001/AS11` | Projectivy abrió con Inicio y tras dos reinicios; Fuentes, Ajustes y accesibilidad siguieron funcionando. [Registro del procedimiento](docs/tcl-43q5k.md). |

En ambos equipos hubo que desactivar LauncherX y `setupwraith` para que Projectivy resolviera HOME. **No se ha comprobado un corte eléctrico real** en ninguno. Los resultados no garantizan compatibilidad con otro firmware, tamaño o región.

## Qué hace

1. Comprueba que Projectivy (`com.spocky.projengmenu`) ya esté instalado y que pueda abrir `/.ui.home.MainActivity`.
2. Lee el HOME actual, el estado de LauncherX y setupwraith, la versión de firmware y el dueño de las redes Wi-Fi guardadas.
3. Guarda el estado original en un archivo JSON local **antes** de modificar la TV.
4. Asigna Projectivy a HOME, intenta asignar el rol HOME cuando Android lo admite y desactiva LauncherX **solo para el usuario 0**.
5. En la TCL A400 Pro comprobada, desactiva `setupwraith` tras verificar la red Wi-Fi y vuelve a asignar Projectivy. En otros Google TV solo lo desactiva si toma HOME.
6. Verifica que Android resuelva HOME a Projectivy. Si falla, intenta restaurar LauncherX y el HOME anterior.

La herramienta no instala APKs, no desinstala paquetes, no cambia accesibilidad, no activa autoinicio y no ejecuta una lista de debloat. Las preferencias, filas y aplicaciones de Projectivy se configuran en la propia app. Ser el HOME real evita depender de accesibilidad para el arranque o el botón Inicio. Si quieres mantener las funciones adicionales de Projectivy que sí usan accesibilidad, consulta el [caso de la 43Q5K](docs/tcl-43q5k.md#accesibilidad-opcional): requiere una configuración separada.

## Antes de empezar

- TV Google TV con **Projectivy instalado y configurado**. Ábrelo una vez desde Apps.
- Computadora con Python 3 y [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools) (`adb` en PATH).
- TV y computadora en una red de confianza. Activa la opción de depuración disponible en tu firmware y autoriza la computadora en la pantalla de la TV. La 75A400 Pro mostró **Depuración inalámbrica** con puerto variable; la 43Q5K mostró **Depuración USB** y aceptó ADB por la red en el puerto `5555`. No supongas que todos los puertos USB de TV admiten una conexión ADB por cable.
- Acceso físico al control de la TV y a Ajustes, por si hay que volver a activar el inicio original.
- Usa el puerto **actual** que muestra Depuración inalámbrica si tu TV ofrece esa opción. En Android 14 puede cambiar después de cada reinicio. Prueba `5555` solo cuando el firmware exponga ADB por red, como se comprobó en la 43Q5K; no lo presupongas en otros modelos.

La herramienta automatizada reconoce únicamente `com.google.android.apps.tv.launcherx` como inicio original. Se detiene si encuentra otro HOME, un selector de launcher, un firmware diferente al de su copia de seguridad o si no puede comprobar la propiedad de las redes Wi-Fi antes de tocar setupwraith. En otros modelos, revisa primero sus componentes HOME y adapta el procedimiento manualmente.

## Aplicar

```bash
adb connect IP_DE_TU_TV:PUERTO_ACTUAL
adb devices
python3 tools/projectivy.py status --serial IP_DE_TU_TV:PUERTO_ACTUAL
python3 tools/projectivy.py apply --serial IP_DE_TU_TV:PUERTO_ACTUAL --backup backup/projectivy-home.json
```

Sustituye la IP y el puerto por los de **tu** TV; no reutilices las direcciones de los ejemplos. En la 43Q5K comprobada, usa `IP_DE_TU_TV:5555` con Depuración USB activada. Si Android pide emparejamiento, usa `adb pair IP:PUERTO_DE_EMPAREJAMIENTO` con el código que muestre la TV y después `adb connect IP:PUERTO_DE_DEPURACIÓN`. Son dos puertos distintos. Si aparece `unauthorized`, acepta el aviso en pantalla y repite `adb connect`.

El archivo `backup/projectivy-home.json` contiene el HOME y el firmware original. Consérvalo. La herramienta se niega a sobrescribirlo para no perder el estado previo. **Si ya hiciste el cambio manualmente, no crees una copia como si reflejara el estado anterior.** `status` sí sirve para revisar esa TV.

Después de aplicar, comprueba en la TV: botón Inicio, Fuentes/Entradas y Ajustes. Reinicia completamente y comprueba que Projectivy aparezca **sin pulsar Inicio**. Si solo pruebas suspensión, la prueba no confirma el arranque en frío. La depuración inalámbrica puede cambiar de puerto tras reiniciar.

## Restaurar el inicio original

```bash
adb connect IP_DE_TU_TV:PUERTO_ACTUAL
python3 tools/projectivy.py restore --serial IP_DE_TU_TV:PUERTO_ACTUAL --backup backup/projectivy-home.json
```

La restauración vuelve a habilitar los componentes que estaban habilitados en la copia y asigna el HOME original. No borra Projectivy ni sus ajustes. Si la TV perdió la conexión y ya no aparece HOME, vuelve a conectar ADB por el puerto disponible; una conexión USB física solo sirve si el hardware la admite. Para las dos TCL comprobadas, la recuperación manual del HOME es:

```bash
adb -s IP:PUERTO shell pm enable --user 0 com.google.android.tungsten.setupwraith
adb -s IP:PUERTO shell pm enable --user 0 com.google.android.apps.tv.launcherx
adb -s IP:PUERTO shell cmd package set-home-activity com.google.android.apps.tv.launcherx/.home.HomeActivity
```

Usa esos comandos manuales solo si coinciden con el HOME y los componentes que tenía tu TV. La copia JSON es la fuente de verdad para la restauración automatizada. En Android TV 12 de la 43Q5K, `cmd role get-role-holders` no estaba disponible; verifica el HOME efectivo con `status`.

## Por qué se revisa setupwraith y el Wi-Fi

En las TCL comprobadas, `com.google.android.tungsten.setupwraith/.RecoveryActivity` era candidato HOME. Fue necesario desactivarlo para que Projectivy resolviera HOME. Si una red Wi-Fi fue guardada por ese componente durante la configuración inicial, Android puede eliminarla al desactivarlo y cortar ADB. La herramienta lee `dumpsys wifi` y se detiene si detecta que setupwraith es dueño de una red o no puede determinarlo. En la 43Q5K se olvidó y reconectó la red desde Ajustes antes de proceder; después, el propietario registrado fue `com.android.tv.settings`.

En la 75A400 Pro, el permiso interno `AUTO_START` y `accessibility_enabled` se restablecían tras reiniciar. En la 43Q5K, el permiso observado fue **`APP_AUTO_START`**: figuraba en `ignore` y, tras cambiarlo a `allow` y activar accesibilidad desde la TV, ambos valores persistieron al reiniciar. Son firmwares diferentes; no intercambies los nombres de permiso sin comprobarlos. Projectivy no necesita accesibilidad para ser HOME real, pero sí puede usarla para otras funciones.

## Debloat y procedencia

El cambio de HOME no requiere desactivar telemetría, Chromecast, actualizaciones, TV en vivo ni otros paquetes. Las listas en [`examples/`](examples/) pertenecen a otros televisores; **no apliques una lista de otro modelo a la A400 Pro ni a la 43Q5K** por compartir placa o versión. Si quieres debloat, revisa cada paquete de tu equipo y usa [`tools/disable.sh`](tools/disable.sh) y [`tools/restore.sh`](tools/restore.sh) de forma independiente, con sus propias copias.

Las listas de [`examples/`](examples/) provienen del proyecto principal y se conservan como referencias históricas de otros modelos. Sus comentarios pueden describir paquetes o decisiones que no aplican a esta TV; no equivalen a una validación de Projectivy en esos equipos. Los scripts generales de debloat y restauración también derivan de CleanYourTV. El código y las imágenes del launcher propio del proyecto original se consultan en el [repositorio de Gathin23](https://github.com/Gathin23/cleanyourtv); fueron retirados de esta variante para que no se confundan con Projectivy.

Este fork mantiene la [licencia MIT original](LICENSE) y reconoce la autoría de [Gathin23](https://github.com/Gathin23) para CleanYourTV y de [Spocky](https://github.com/spocky) para Projectivy. La opción de [apoyar al autor original](https://buymeacoffee.com/gathint) permanece en el repositorio. Las capturas de arriba pertenecen al material público de Projectivy y se muestran desde su sitio. [`PROMPT.md`](PROMPT.md) contiene el encargo actualizado para un asistente técnico.

Al terminar, desactiva la opción de depuración que activaste en la TV si ya no la necesitas. Un cambio de firmware puede volver a habilitar LauncherX o alterar prioridades HOME; en ese caso revisa `status` antes de repetir pasos.
