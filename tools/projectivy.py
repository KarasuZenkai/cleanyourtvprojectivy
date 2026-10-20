#!/usr/bin/env python3
"""Make an already installed Projectivy the Android TV HOME app, with a local undo record.

Uses the platform-tools adb client, including Android 11+ wireless debugging ports.
Only the known Google TV launcher is disabled automatically. No apps are uninstalled.
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
        raise DeviceError(f"adb {' '.join(args)}: {output or 'failed'}")
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
    # Older Android releases may lack this command. HOME resolution remains authoritative.
    output = shell(serial, "cmd role get-role-holders android.app.role.HOME", required=False)
    return PROJECTIVY if PROJECTIVY in output else (STOCK if STOCK in output else None)


def set_home(serial, component):
    if not COMPONENT.fullmatch(component):
        raise DeviceError(f"Invalid HOME component: {component!r}")
    shell(serial, f"cmd package set-home-activity {component}")


def set_role(serial, package):
    if package:
        shell(serial, f"cmd role add-role-holder android.app.role.HOME {package}", required=False)


def ensure_wifi_safe(serial):
    wifi = shell(serial, "dumpsys wifi")
    owners = re.findall(r"cname=([^\s]+)", wifi)
    if not owners:
        raise DeviceError(
            "Cannot determine who owns saved Wi-Fi networks. Leave setupwraith enabled; "
            "check on the TV or use a wired connection and restore manually."
        )
    if any("setupwraith" in owner.lower() for owner in owners):
        raise DeviceError(
            "A saved Wi-Fi network belongs to setupwraith. Forget and rejoin it in "
            "TV Settings > Network & Internet, then retry."
        )


def snapshot(serial):
    original_home = home(serial)
    if not original_home:
        raise DeviceError("HOME resolves to a chooser or nothing. Select the stock Home on the TV first.")
    if not original_home.startswith(STOCK + "/"):
        raise DeviceError(f"Expected {STOCK} as the current Home, found {original_home}.")
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
        raise DeviceError("The backup is invalid or has an unsupported format.")
    if data.get("device") != shell(serial, "getprop ro.product.device"):
        raise DeviceError("The backup is for another device. No changes were made.")
    if data.get("build") != shell(serial, "getprop ro.build.fingerprint"):
        raise DeviceError("The TV firmware changed since the backup. Restore manually after reviewing it.")
    return data


def restore(serial, data):
    # Enable original HOME candidates before setting the original component.
    if data["setup_enabled"] and installed(serial, SETUP):
        shell(serial, f"pm enable --user 0 {SETUP}")
    if data["stock_enabled"]:
        shell(serial, f"pm enable --user 0 {STOCK}")
    set_home(serial, data["original_home"])
    set_role(serial, data.get("role_holder") or data["original_home"].split("/")[0])
    current = home(serial)
    if current != data["original_home"]:
        raise DeviceError(f"Restore incomplete: HOME resolves to {current or 'nothing'}.")
    print(f"Restored HOME: {current}")


def apply(serial, backup):
    if backup.exists():
        raise DeviceError(f"{backup} already exists. Use it for restore; do not overwrite the original state.")
    if not installed(serial, PROJECTIVY):
        raise DeviceError("Install and configure Projectivy on the TV before running this command.")
    if not installed(serial, STOCK):
        raise DeviceError(f"{STOCK} is absent; this automated flow targets Google TV with LauncherX.")
    data = snapshot(serial)
    # The TCL G08 setup wizard can take HOME as soon as LauncherX is disabled.
    # Check before touching either package, while ADB and the stock launcher still work.
    if data["setup_enabled"]:
        ensure_wifi_safe(serial)
    started = shell(serial, f"am start -W -n {PROJECTIVY_HOME}")
    if "Status: ok" not in started or re.search(r"(?im)^error", started):
        raise DeviceError(f"Projectivy did not start: {started}")
    save(backup, data)
    print(f"Saved original state to {backup}")
    try:
        set_home(serial, PROJECTIVY_HOME)
        set_role(serial, PROJECTIVY)
        shell(serial, f"pm disable-user --user 0 {STOCK}")
        # Disabling a HOME claimant can clear Android's chosen HOME.
        set_home(serial, PROJECTIVY_HOME)
        # On the verified A400 Pro firmware, setupwraith reclaimed HOME on reboot.
        # Disable it even if Projectivy briefly resolves here.
        verified_tcl = ("G08_4K_GB_NF" in data["build"]
                        and "UTT2.250416.001/AU02" in data["build"])
        if data["setup_enabled"] and (home(serial) != PROJECTIVY_HOME or verified_tcl):
            shell(serial, f"pm disable-user --user 0 {SETUP}")
            set_home(serial, PROJECTIVY_HOME)
        current = home(serial)
        if current != PROJECTIVY_HOME:
            raise DeviceError(f"HOME resolves to {current or 'nothing'}, not Projectivy.")
        shell(serial, "input keyevent 3")
        print(f"Projectivy owns HOME: {current}. Press Home and verify Inputs and Settings on the remote.")
        print("Then perform a full reboot and check that Projectivy opens without accessibility.")
    except Exception as error:
        print(f"Handover failed: {error}. Attempting to restore the original HOME.", file=sys.stderr)
        try:
            restore(serial, data)
        except Exception as restore_error:
            print(f"Automatic restore failed: {restore_error}", file=sys.stderr)
            print(f"Keep {backup}; reconnect ADB and run the restore command.", file=sys.stderr)
        raise DeviceError("Projectivy handover did not complete.") from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("status", "apply", "restore"))
    parser.add_argument("--serial", required=True, help="ADB device serial, e.g. 192.168.100.107:44023")
    parser.add_argument("--backup", type=Path, default=Path("projectivy-backup.json"))
    args = parser.parse_args()
    try:
        if adb(args.serial, "get-state") != "device":
            raise DeviceError("ADB is not authorized or the TV is offline.")
        if args.action == "status":
            for package in (PROJECTIVY, STOCK, SETUP):
                print(f"{package}: " + ("absent" if not installed(args.serial, package)
                      else "disabled" if disabled(args.serial, package) else "enabled"))
            print(f"HOME: {home(args.serial) or 'chooser/unknown'}")
            print(f"HOME role: {role_holder(args.serial) or 'unknown'}")
        elif args.action == "apply":
            apply(args.serial, args.backup)
        else:
            restore(args.serial, load(args.backup, args.serial))
    except (DeviceError, OSError, ValueError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
