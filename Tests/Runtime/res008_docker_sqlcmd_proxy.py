#!/usr/bin/env python3
"""RES-008-Adapter für -C/-l/-y; gemeinsamer Containervertrag bleibt erhalten."""
import docker_sqlcmd_proxy as proxy

# Nur die tatsächlich vom öffentlichen RES-008-Controller erzeugten Optionen.
# Passwort-, Container-, stdin- und Prozessverhalten bleiben im gemeinsamen Proxy.
proxy.BOOLEAN_FLAGS = proxy.BOOLEAN_FLAGS | {'-C'}
proxy.VALUE_FLAGS = proxy.VALUE_FLAGS | {'-l', '-y'}

if __name__ == '__main__':
    raise SystemExit(proxy.main())
