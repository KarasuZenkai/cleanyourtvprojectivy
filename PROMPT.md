# Encargo para configurar Projectivy como HOME

Este encargo pertenece a la variante de [CleanYourTV de Gathin23](https://github.com/Gathin23/cleanyourtv) que asigna [Projectivy de Spocky](https://github.com/spocky/miproja1) como HOME. Úsalo con un asistente técnico que tenga acceso a una computadora con `adb`. Lee primero [README.md](README.md) y revisa el estado real de la TV antes de ejecutar cambios. Sustituye los datos entre corchetes.

---

Quiero que Projectivy Launcher, que ya instalé y configuré, sea el launcher predeterminado de mi Google TV. El objetivo de esta variante es desactivar el HOME principal de Google TV cuando sea necesario, asignar Projectivy como HOME real y conservar la posibilidad de restaurar el estado previo. Mi modelo es [MODELO], versión de Android [VERSIÓN], compilación [COMPILACIÓN]. La opción de depuración disponible es [DEPURACIÓN INALÁMBRICA / DEPURACIÓN USB] y la dirección de la TV es [IP]. Si la TV muestra un puerto, es [PUERTO].

Procede por etapas:

1. Identifica la opción de depuración real antes de conectar. Con Depuración inalámbrica, usa la IP y el puerto que muestra la TV y, si hace falta, guíame para emparejar. Con Depuración USB, comprueba si este firmware acepta `adb connect IP:5555`, como la 43Q5K observada; no lo presupongas para otros modelos. Pídeme aceptar la autorización en pantalla. Si la IP o el puerto cambian tras reiniciar, usa los nuevos valores.
2. Consulta modelo, firmware, HOME actual, candidatos HOME, estado de LauncherX y setupwraith, instalación de Projectivy y propietario de las redes guardadas en `dumpsys wifi`. Comprueba que Projectivy se abre.
3. Antes de modificar el HOME, guarda su componente exacto y qué paquetes estaban habilitados. No sobrescribas una copia previa. Si una red pertenece a setupwraith, detente y dime cómo olvidarla y reconectarla desde Ajustes de la TV; verifica después que el propietario cambió. Si no puedes comprobar el dueño de la red, detente.
4. Si los datos coinciden con los requisitos de `tools/projectivy.py`, usa `status` y `apply` con `--serial` y un archivo `--backup` local. El flujo desactiva `com.google.android.apps.tv.launcherx` y, cuando sea necesario, `com.google.android.tungsten.setupwraith`. Si los datos no coinciden, explica la diferencia antes de decidir un procedimiento específico para ese modelo.
5. Verifica que `cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME` resuelva a `com.spocky.projengmenu/.ui.home.MainActivity`. Pídeme comprobar el botón físico Inicio, Fuentes/Entradas y Ajustes, y después un reinicio completo con arranque automático de Projectivy. Una tecla simulada no sustituye la prueba física.
6. Si pido conservar funciones de accesibilidad y el servicio se apaga tras reiniciar, lee primero el `appops` real de Projectivy. En la 43Q5K se observó `APP_AUTO_START: ignore`; al cambiarlo a `allow` y activar el servicio desde Ajustes de la TV, persistió tras otro reinicio. No uses `AUTO_START` o `APP_AUTO_START` sin comprobar cuál existe en este firmware. Pídeme aceptar personalmente la confirmación de accesibilidad del sistema.
7. Entrega la ruta de la copia y el comando exacto de restauración. Si falla el traspaso, restaura el HOME original antes de terminar. Al acabar, recuérdame apagar la opción de depuración activada si ya no la necesito.

No desinstales paquetes del sistema ni cambies servicios de accesibilidad como requisito para HOME. La accesibilidad es una elección separada del usuario y su cambio debe tener recuperación documentada. No apliques listas de debloat de un modelo distinto sin revisar cada paquete. Si deseo debloat, consúltame qué funciones uso (TV en vivo, HDMI, casting, voz, actualizaciones y apps de streaming) y trátalo como una tarea aparte.

---

Hay dos experiencias documentadas: una TCL 75A400 Pro NXTVISION con Android TV 14, `G08_4K_GB_NF`, `tcl9618`, compilación `UTT2.250416.001 AU02`; y una [TCL 43Q5K](docs/tcl-43q5k.md) con Android TV 12, `G10_4K_GB_NF_32BIT`, `STT2.230203.001/AS11`. En ambas, Projectivy abrió tras reiniciar y el control conservó Inicio, Fuentes y Ajustes. En la 43Q5K también persistió accesibilidad tras permitir `APP_AUTO_START`. No extrapoles esos resultados a otros equipos ni afirmes que se probó un corte de corriente.
