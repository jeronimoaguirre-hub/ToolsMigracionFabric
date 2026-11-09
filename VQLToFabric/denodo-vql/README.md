# denodo-vql/

Deja aquí los archivos VQL exportados que te proporcione el equipo de origen (uno o varios `.vql`). El harness solo los lee localmente; no se conecta a Denodo.

- Incluye report views (`rv_`), base views (`bv_`) y las definiciones disponibles de sus dependencias para que `vql-explorer` pueda trazar la cadena completa.
- Los exports suelen ser archivos grandes: los agentes los buscan con grep por
  nombre de vista y leen solo el rango necesario.
- Esta carpeta es del desarrollador; no se actualiza con la plantilla.
