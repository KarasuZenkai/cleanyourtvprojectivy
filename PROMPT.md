# Encargo para configurar Projectivy como HOME

Este encargo pertenece a la variante de [CleanYourTV de Gathin23](https://github.com/Gathin23/cleanyourtv) que asigna [Projectivy de Spocky](https://github.com/spocky/miproja1) como HOME. Úsalo con un asistente técnico que tenga acceso a una computadora con `adb`. Lee primero [README.md](README.md) y revisa el estado real de la TV antes de ejecutar cambios. Sustituye los datos entre corchetes.

---

Quiero que Projectivy Launcher, que ya instalé y configuré, sea el launcher predeterminado de mi Google TV. El objetivo de esta variante es desactivar el HOME principal de Google TV cuando sea necesario, asignar Projectivy como HOME real y conservar la posibilidad de restaurar el estado previo. Mi modelo es [MODELO], versión de Android [VERSIÓN], compilación [COMPILACIÓN]. La dirección y puerto actuales de Depuración inalámbrica son [IP:PUERTO].

Procede por etapas:

1. Conecta con `adb connect IP:PUERTO`; si es necesario, guíame para emparejar y aceptar la autorización en la pantalla. No presupongas el puerto 5555. Si el puerto cambió tras reiniciar, pídeme el nuevo valor.
2. Consulta modelo, firmware, HOME actual, candidatos HOME, estado de LauncherX y setupwraith, instalación de Projectivy y propietario de las redes guardadas en `dumpsys wifi`. Comprueba que Projectivy se abre.
3. Antes de modificar el HOME, guarda su componente exacto y qué paquetes estaban habilitados. No sobrescribas una copia previa. Si una red pertenece a setupwraith, detente y dime cómo olvidarla y reconectarla desde Ajustes de la TV. Si no puedes comprobar el dueño de la red, detente.
4. Si los datos coinciden con los requisitos de `tools/projectivy.py`, usa `status` y `apply` con `--serial` y un archivo `--backup` local. El flujo desactiva `com.google.android.apps.tv.launcherx` y, cuando sea necesario, `com.google.android.tungsten.setupwraith`. Si los datos no coinciden, explica la diferencia antes de decidir un procedimiento específico para ese modelo.
5. Verifica que `cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME` resuelva a `com.spocky.projengmenu/.ui.home.MainActivity`. Pídeme comprobar el botón físico Inicio, Fuentes/Entradas y Ajustes, y después un reinicio completo con arranque automático de Projectivy. Una tecla simulada no sustituye la prueba física.
6. Entrega la ruta de la copia y el comando exacto de restauración. Si falla el traspaso, restaura el HOME original antes de terminar. Al acabar, recuérdame apagar Depuración inalámbrica si ya no la necesito.

No desinstales paquetes del sistema ni cambies servicios de accesibilidad como requisito para HOME. No apliques listas de debloat de un modelo distinto sin revisar cada paquete. Si deseo debloat, consúltame qué funciones uso (TV en vivo, HDMI, casting, voz, actualizaciones y apps de streaming) y trátalo como una tarea aparte.

---

La experiencia documentada corresponde a una TCL 75A400 Pro NXTVISION con Android TV 14, `G08_4K_GB_NF`, `tcl9618` y compilación `UTT2.250416.001 AU02`. En esa TV, LauncherX y setupwraith competían por HOME; al desactivarlos y asignar Projectivy, éste abrió tras reinicio y el control conservó Inicio, Fuentes y Ajustes. No extrapoles ese resultado a otros equipos ni afirmes que se probó un corte de corriente.
