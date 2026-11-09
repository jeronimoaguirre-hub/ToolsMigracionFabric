# ddl/

DDL **propuesto** por `tsql-view-architect`: un archivo `{vista}.sql` por vista
(`CREATE OR ALTER VIEW [esquema].[vista] AS ...`).

- Los agentes pueden proponer y editar el DDL; **nunca lo despliegan**.
- El ingeniero revisa el DDL, sus supuestos y las decisiones pendientes. Si lo
  aprueba, lo despliega en Fabric con el método documentado en `producto.yml`
  (`despliegue.metodo`).
- Anota fecha y responsable en el ledger.
- La revisión del harness es estática y/o usa metadatos de Fabric en solo
  lectura. No equivale a una comparación de resultados contra Denodo.
