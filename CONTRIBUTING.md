# Cómo contribuir

Esta es una variante de [CleanYourTV, de Gathin23](https://github.com/Gathin23/cleanyourtv). Aquí se documenta y automatiza la asignación de [Projectivy Launcher, de Spocky](https://github.com/spocky/miproja1), como HOME. Las contribuciones a la aplicación Projectivy deben presentarse en su repositorio; este fork solo cambia la configuración del sistema mediante ADB.

## Información útil para un reporte

- Modelo exacto, versión de Android, producto y compilación.
- Componentes que responden a HOME antes y después.
- Estado de Projectivy, LauncherX y setupwraith.
- Resultado de los botones físicos Inicio, Fuentes y Ajustes, y de un reinicio completo.
- Si dumpsys wifi muestra redes cuyo dueño sea setupwraith.

Oculta direcciones IP, nombres de red, identificadores de la TV y claves ADB antes de compartir capturas o registros. No publiques la copia de seguridad de tu dispositivo.

## Listas de debloat

Las listas heredadas en [examples/](examples/) son datos aportados al proyecto principal para equipos concretos. No copies una lista a otro modelo por coincidir el chipset. Si aportas una lista, indica modelo, compilación, paquetes desactivados y funciones verificadas. Nunca incluyas comandos de desinstalación.

## Código y documentación

Mantén el procedimiento reversible y comprueba el estado antes de desactivar un candidato HOME. Explica qué firmware probaste y qué ocurrió tras un reinicio completo. Para una nueva captura, usa una imagen auténtica de Projectivy con permiso o enlace a su fuente. La [licencia MIT](LICENSE) conserva el aviso de autoría original.
