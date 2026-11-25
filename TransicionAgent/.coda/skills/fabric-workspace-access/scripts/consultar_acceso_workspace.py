"""
Consulta roles de usuarios y capacidad de un workspace de Fabric
vía API REST (solo lectura).

Lista los roleAssignments del workspace (Admin/Member/Contributor/Viewer)
con UPN de usuarios, appId de service principals y tipo de grupos, y muestra
los datos de la capacidad asociada (sku, región, estado) si hay permiso.

Ejemplos:
    uv run python consultar_acceso_workspace.py --workspace <workspaceId>
    uv run python consultar_acceso_workspace.py --workspace <ws> --solo-roles
    uv run python consultar_acceso_workspace.py --workspace <ws> --output roles.csv
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parent.parent.parent
        / "fabric-rest-api"
        / "scripts"
    ),
)

from fabric_rest_client import FabricRestClient, FabricRestError  # noqa: E402


def _identificador_principal(principal: dict) -> str:
    tipo = principal.get("type", "?")
    if tipo == "User":
        return (principal.get("userDetails") or {}).get("userPrincipalName", "")
    if tipo == "ServicePrincipal":
        return (principal.get("servicePrincipalDetails") or {}).get("aadAppId", "")
    if tipo == "Group":
        return (principal.get("groupDetails") or {}).get("groupType", "")
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Roles y capacidad de un workspace de Fabric (solo lectura)."
    )
    parser.add_argument("--workspace", required=True, help="ID del workspace.")
    parser.add_argument(
        "--solo-roles", action="store_true", help="No consultar capacidad."
    )
    parser.add_argument(
        "--output", "-o", default=None, help="Guardar roles como CSV."
    )
    args = parser.parse_args()

    client = FabricRestClient()

    # ---------------- Roles ---------------- #
    try:
        asignaciones = client.get_all(
            f"/workspaces/{args.workspace}/roleAssignments"
        )
    except FabricRestError as error:
        print(f"ERROR listando roles: {error}")
        if getattr(error, "status_code", None) == 403:
            print(
                "Se necesita rol Member o superior en el workspace "
                "(el rol Viewer no alcanza)."
            )
        return 1

    filas = []
    for asignacion in asignaciones:
        principal = asignacion.get("principal") or {}
        filas.append(
            {
                "rol": asignacion.get("role", ""),
                "principal": principal.get("displayName", ""),
                "tipo": principal.get("type", ""),
                "identificador": _identificador_principal(principal),
            }
        )

    if not filas:
        print("Sin roleAssignments visibles.")
        return 0

    anchos = {
        clave: max(len(str(fila[clave])) for fila in filas)
        for clave in filas[0]
    }
    encabezado = list(filas[0].keys())
    print(" | ".join(k.ljust(anchos[k]) for k in encabezado))
    print("-+-".join("-" * anchos[k] for k in encabezado))
    for fila in filas:
        print(" | ".join(str(fila[k]).ljust(anchos[k]) for k in encabezado))

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=encabezado)
            writer.writeheader()
            writer.writerows(filas)
        print(f"\nCSV guardado en: {Path(args.output).resolve()}")

    # ---------------- Capacidad ---------------- #
    if args.solo_roles:
        return 0

    try:
        workspace = client.get(f"/workspaces/{args.workspace}")
        capacity_id = (workspace.get("capacityId") or "").strip()
        print(f"\nCapacidad del workspace: {capacity_id or '(sin capacidad asignada)'}")
        print(f"  Región: {workspace.get('capacityRegion', '?')} | "
              f"Tipo: {workspace.get('type', '?')}")
        if capacity_id:
            capacidades = client.get_all("/capacities")
            for capacidad in capacidades:
                if (capacidad.get("id") or "").lower() == capacity_id.lower():
                    print(f"  SKU: {capacidad.get('sku', '?')} | "
                          f"Estado: {capacidad.get('state', '?')}")
                    break
    except FabricRestError as error:
        print(f"  (Capacidad no consultada: {error})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
