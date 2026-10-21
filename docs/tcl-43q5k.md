# TCL 43Q5K: Projectivy como inicio

Registro de una **TCL 43Q5K** con Android TV 12, dispositivo `G10`, producto `G10_4K_GB_NF_32BIT` y compilación `STT2.230203.001/AS11`. Se comprobó el 20 de octubre de 2026. Este procedimiento describe el firmware observado; otros modelos o actualizaciones pueden comportarse de otra manera.

## Resultado observado

- Projectivy (`com.spocky.projengmenu`) ya estaba instalado y configurado.
- En Opciones para desarrolladores aparecía **Depuración USB**, pero no **Depuración inalámbrica**. Con esa opción activada, `adb connect IP_DE_TU_TV:5555` funcionó por la red y la autorización se aceptó en la pantalla.
- HOME original: `com.google.android.apps.tv.launcherx/.home.HomeActivity`. Los otros candidatos fueron `com.google.android.tungsten.setupwraith/.RecoveryActivity`, Projectivy y `com.android.tv.settings/.system.FallbackHome`.
- Asignar Projectivy con `cmd package set-home-activity` sin desactivar los competidores no cambió la resolución de HOME: LauncherX siguió ganando.
- La red Wi-Fi guardada pertenecía inicialmente a `setupwraith`. Se olvidó y reconectó **desde Ajustes de la TV**, sin compartir la contraseña. ADB confirmó después que el propietario pasó a `com.android.tv.settings`.
- `tools/projectivy.py apply` guardó el estado original, desactivó LauncherX y `setupwraith` solo para el usuario 0, y dejó a Projectivy como HOME. Inicio, Fuentes/Entradas y Ajustes funcionaron con el control físico. Projectivy abrió automáticamente tras el primer reinicio.
- Tras el primer reinicio, Projectivy mostró un aviso de accesibilidad. Se permitió `APP_AUTO_START`, se activó el servicio en Ajustes de la TV y, tras un segundo reinicio, Projectivy abrió sin aviso. ADB confirmó HOME, servicio de accesibilidad y autoinicio activos.

**Límite de la comprobación:** hubo reinicios completos por ADB, pero no se probó un corte de energía ni un restablecimiento de fábrica.

## Antes de cambiar HOME

Instala y configura Projectivy. En la TV, activa Opciones para desarrolladores y **Depuración USB**. Conecta la computadora a la misma red y sustituye `IP_DE_TU_TV` por la dirección actual:

```bash
adb connect IP_DE_TU_TV:5555
adb devices
python3 tools/projectivy.py status --serial IP_DE_TU_TV:5555
```

Si ADB muestra `unauthorized` o `failed to authenticate`, acepta la solicitud en la TV y vuelve a consultar `adb devices`. Si el puerto `5555` no responde, este método no está disponible en ese firmware: no continúes con comandos de paquetes. Una toma USB del televisor puede ser solo para memorias y periféricos; comprueba su capacidad antes de intentar ADB por cable.

Confirma que HOME sea LauncherX y que Projectivy se pueda abrir. La herramienta se detiene si una red Wi-Fi guardada pertenece a `setupwraith` o si no puede verificarlo. En ese caso, olvida la red desde **Ajustes → Red e Internet** en la TV, reconéctala allí y repite la comprobación. Es posible que cambie la IP; usa la nueva. No desactives `setupwraith` mientras sea propietario de la única conexión que usas para ADB.

## Aplicar y comprobar

Elige un archivo de respaldo nuevo y propio de esa TV. El directorio `backup/` está excluido de Git porque el JSON contiene datos del firmware y del dispositivo.

```bash
python3 tools/projectivy.py apply --serial IP_DE_TU_TV:5555 --backup backup/tcl-43q5k-home.json
python3 tools/projectivy.py status --serial IP_DE_TU_TV:5555
```

Comprueba físicamente Inicio, Fuentes/Entradas y Ajustes. Reinicia la TV y verifica que Projectivy aparezca **sin pulsar Inicio**. La herramienta verifica la resolución de HOME durante `apply`, pero no sustituye esta comprobación tras el arranque.

## Accesibilidad opcional

La accesibilidad **no es requisito para que Projectivy sea HOME**. Si quieres las funciones adicionales que la usan y Projectivy muestra el aviso después de reiniciar, revisa primero el permiso observado en ese firmware:

```bash
adb -s IP_DE_TU_TV:5555 shell appops get com.spocky.projengmenu APP_AUTO_START
```

En nuestra 43Q5K figuraba `APP_AUTO_START: ignore`. Se cambió a `allow`:

```bash
adb -s IP_DE_TU_TV:5555 shell appops set com.spocky.projengmenu APP_AUTO_START allow
```

Después se abrió **Ajustes → Accesibilidad → Projectivy Launcher** en la TV y se activó el servicio aceptando la confirmación de Android. El servicio tiene acceso amplio a la interacción en pantalla; actívalo solo si deseas esas funciones. En el segundo reinicio se conservó `APP_AUTO_START: allow`, `accessibility_enabled: 1` y el servicio `com.spocky.projengmenu.services.ProjectivyAccessibilityService`. El aviso desapareció. **No presupongas este nombre de permiso en otra TCL**: en otros firmwares aparece `AUTO_START`.

## Restaurar

Conserva el JSON creado por `apply` en la misma computadora. Para recuperar el HOME original:

```bash
adb connect IP_DE_TU_TV:5555
python3 tools/projectivy.py restore --serial IP_DE_TU_TV:5555 --backup backup/tcl-43q5k-home.json
```

La restauración habilita los componentes que estaban activos y reasigna el HOME guardado. Si configuraste la accesibilidad opcional y también quieres volver al estado previo de esta TV, desactiva Projectivy en **Ajustes → Accesibilidad** y revierte el permiso observado originalmente:

```bash
adb -s IP_DE_TU_TV:5555 shell appops set com.spocky.projengmenu APP_AUTO_START ignore
```

El script no modifica accesibilidad ni `APP_AUTO_START`, por lo que esos dos pasos son independientes de la restauración de HOME. En este Android TV 12, `cmd role get-role-holders` no estaba disponible; la comprobación decisiva fue `cmd package resolve-activity`.
