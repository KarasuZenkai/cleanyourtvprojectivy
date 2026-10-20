#!/usr/bin/env python3
"""Asigna Projectivy como HOME de Android TV y guarda un registro local para restaurar.

Usa adb de Platform Tools, incluidos los puertos de depuración inalámbrica.
Solo desactiva automáticamente el LauncherX reconocido. No desinstala aplicaciones.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PROJECTIVY = "com.spocky.projengmenu"
PROJECTIVY_HOME = PROJECTIVY + "/.ui.home.MainActivity"
STOCK = "com.google.android.apps.tv.launcherx"
SETUP = "com.google.android.tungsten.setupwraith"
HOME_QUERY = ("cmd package resolve-activity --brief -a android.intent.action.MAIN "
              "-c android.intent.category.HOME")
COMPONENT = re.compile(r"^[A-Za-z_][\w.]*/[A-Za-z_.][\w.$]*$")


class DeviceError(Exception):
    pass


def adb(serial, *args, required=True):
    proc = subprocess.run(["adb", "-s", serial, *args], capture_output=True, text=True)
    output = (proc.stdout + proc.stderr).strip()
    if required and (proc.returncode or re.search(r"(?im)^(error:|exception|failure)", output)):
        raise DeviceError(f"adb {' '.join(args)}: {output or 'falló'}")
    return output


def shell(serial, command, required=True):
    return adb(serial, "shell", command, required=required)


def home(serial):
    answer = shell(serial, HOME_QUERY).splitlines()
    candidate = answer[-1].strip() if answer else ""
    return candidate if COMPONENT.fullmatch(candidate) else None


def installed(serial, package):
    return bool(re.search(r"(?m)^package:", shell(serial, f"pm path {package}", required=False)))


def disabled(serial, package):
    return f"package:{package}" in shell(serial, "pm list packages -d").splitlines()


def role_holder(serial):
    # Algunas versiones de Android no tienen este comando. La resolución HOME es decisiva.
    output = shell(serial, "cmd role get-role-holders android.app.role.HOME", required=False)
    return PROJECTIVY if PROJECTIVY in output else (STOCK if STOCK in output else None)


def set_home(serial, component):
    if not COMPONENT.fullmatch(component):
        raise DeviceError(f"Componente HOME inválido: {component!r}")
    shell(serial, f"cmd package set-home-activity {component}")


def set_role(serial, package):
    if package:
        shell(serial, f"cmd role add-role-holder android.app.role.HOME {package}", required=False)


def ensure_wifi_safe(serial):
    wifi = shell(serial, "dumpsys wifi")
    owners = re.findall(r"cname=([^\s]+)", wifi)
    if not owners:
        raise DeviceError(
            "No se pudo determinar quién guardó las redes Wi-Fi. Se conserva setupwraith; "
            "comprueba el estado en la TV o usa una conexión por cable y restaura manualmente."
        )
    if any("setupwraith" in owner.lower() for owner in owners):
        raise DeviceError(
            "Una red Wi-Fi guardada pertenece a setupwraith. Olvídala y vuelve a conectarla "
            "en Ajustes > Red e Internet de la TV; después, reintenta."
        )


def snapshot(serial):
    original_home = home(serial)
    if not original_home:
        raise DeviceError("HOME resuelve al selector o a nada. Selecciona primero el inicio original en la TV.")
    if not original_home.startswith(STOCK + "/"):
        raise DeviceError(f"Se esperaba {STOCK} como HOME actual; se encontró {original_home}.")
    return {
        "version": 1,
        "device": shell(serial, "getprop ro.product.device"),
        "build": shell(serial, "getprop ro.build.fingerprint"),
        "original_home": original_home,
        "stock_enabled": not disabled(serial, STOCK),
        "setup_enabled": installed(serial, SETUP) and not disabled(serial, SETUP),
        "role_holder": role_holder(serial),
    }


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def load(path, serial):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not COMPONENT.fullmatch(data.get("original_home", "")):
        raise DeviceError("La copia es inválida o tiene un formato no admitido.")
    if data.get("device") != shell(serial, "getprop ro.product.device"):
        raise DeviceError("La copia pertenece a otro dispositivo. No se hicieron cambios.")
    if data.get("build") != shell(serial, "getprop ro.build.fingerprint"):
        raise DeviceError("El firmware cambió desde la copia. Revísala y restaura manualmente.")
    return data


def restore(serial, data):
    # Habilitar candidatos HOME originales antes de asignar el componente original.
    if data["setup_enabled"] and installed(serial, SETUP):
        shell(serial, f"pm enable --user 0 {SETUP}")
    if data["stock_enabled"]:
        shell(serial, f"pm enable --user 0 {STOCK}")
    set_home(serial, data["original_home"])
    set_role(serial, data.get("role_holder") or data["original_home"].split("/")[0])
    current = home(serial)
    if current != data["original_home"]:
        raise DeviceError(f"Restauración incompleta: HOME resuelve a {current or 'nada'}.")
    print(f"HOME restaurado: {current}")


def apply(serial, backup):
    if backup.exists():
        raise DeviceError(f"{backup} ya existe. Úsalo para restaurar; no sobrescribas el estado original.")
    if not installed(serial, PROJECTIVY):
        raise DeviceError("Instala y configura Projectivy en la TV antes de ejecutar este comando.")
    if not installed(serial, STOCK):
        raise DeviceError(f"{STOCK} no está instalado; este flujo automatizado requiere Google TV con LauncherX.")
    data = snapshot(serial)
    # En TCL G08, setupwraith puede tomar HOME al desactivar LauncherX.
    # Comprobar antes de tocar paquetes, mientras ADB y el inicio original funcionan.
    if data["setup_enabled"]:
        ensure_wifi_safe(serial)
    started = shell(serial, f"am start -W -n {PROJECTIVY_HOME}")
    if "Status: ok" not in started or re.search(r"(?im)^error", started):
        raise DeviceError(f"Projectivy no se abrió: {started}")
    save(backup, data)
    print(f"Estado original guardado en {backup}")
    try:
        set_home(serial, PROJECTIVY_HOME)
        set_role(serial, PROJECTIVY)
        shell(serial, f"pm disable-user --user 0 {STOCK}")
        # Desactivar un candidato HOME puede borrar la selección de Android.
        set_home(serial, PROJECTIVY_HOME)
        # En el firmware A400 Pro comprobado, setupwraith retomaba HOME al reiniciar.
        # Desactivarlo aunque Projectivy resuelva temporalmente aquí.
        verified_tcl = ("G08_4K_GB_NF" in data["build"]
                        and "UTT2.250416.001/AU02" in data["build"])
        if data["setup_enabled"] and (home(serial) != PROJECTIVY_HOME or verified_tcl):
            shell(serial, f"pm disable-user --user 0 {SETUP}")
            set_home(serial, PROJECTIVY_HOME)
        current = home(serial)
        if current != PROJECTIVY_HOME:
            raise DeviceError(f"HOME resuelve a {current or 'nada'}, no a Projectivy.")
        shell(serial, "input keyevent 3")
        print(f"Projectivy es HOME: {current}. Comprueba Inicio, Fuentes y Ajustes en el control.")
        print("Reinicia completamente y comprueba que Projectivy se abra sin accesibilidad.")
    except Exception as error:
        print(f"Falló el cambio: {error}. Intentando restaurar el HOME original.", file=sys.stderr)
        try:
            restore(serial, data)
        except Exception as restore_error:
            print(f"Falló la restauración automática: {restore_error}", file=sys.stderr)
            print(f"Conserva {backup}; reconecta ADB y ejecuta restore.", file=sys.stderr)
        raise DeviceError("No se completó el cambio a Projectivy.") from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("status", "apply", "restore"))
    parser.add_argument("--serial", required=True, help="Identificador ADB, por ejemplo 192.168.100.107:44023")
    parser.add_argument("--backup", type=Path, default=Path("projectivy-backup.json"))
    args = parser.parse_args()
    try:
        if adb(args.serial, "get-state") != "device":
            raise DeviceError("ADB no está autorizado o la TV está desconectada.")
        if args.action == "status":
            for package in (PROJECTIVY, STOCK, SETUP):
                print(f"{package}: " + ("ausente" if not installed(args.serial, package)
                      else "desactivado" if disabled(args.serial, package) else "activado"))
            print(f"HOME: {home(args.serial) or 'selector/desconocido'}")
            print(f"Rol HOME: {role_holder(args.serial) or 'desconocido'}")
        elif args.action == "apply":
            apply(args.serial, args.backup)
        else:
            restore(args.serial, load(args.backup, args.serial))
    except (DeviceError, OSError, ValueError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
