# Simulacro de divulgación coordinada — borrador de aviso

- Repositorio: https://github.com/alejandrorevillaEng/reportaudit-lab
- Canal: Security → Report a vulnerability (private vulnerability reporting, activado vía API)
- Identificador: `GHSA-h9wj-g8cp-pwgx`
- URL (privada; visible solo para colaboradores del aviso): https://github.com/alejandrorevillaEng/reportaudit-lab/security/advisories/GHSA-h9wj-g8cp-pwgx
- Estado: **draft** — no publicado; `published_at` es `null`
- CVE: no solicitado (el laboratorio no pide CVE)
- Severidad: `high` — vector `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L` (8.2)
- CWE: CWE-89 (SQL Injection)
- Paquete declarado: `reportaudit` (ecosystem `other`)
- Versión afectada: `< 1.0.0`; versión corregida: `1.0.0`
- Créditos: `isramrtnz` (reporter), `alejandrorevillaEng` (remediation_developer)

## Hallazgo

En la versión inicial, `app/reporte_auditoria.py` interpolaba el parámetro `cliente` directamente
en una consulta SQL. Con `cliente=o'brien_ltd` el endpoint `/reportes` respondía HTTP 500. La
corrección (PR #20) usa una consulta parametrizada; la comprobación funcional devuelve 1 reporte.

## Por qué sigue siendo un borrador

El objetivo del simulacro es practicar el flujo privado, no publicar un aviso ni pedir un CVE.
Publicarlo ahora no aportaría valor: la vulnerabilidad ya está corregida y liberada en v1.0.0.
El borrador queda como evidencia de que el canal privado existe y de que la versión corregida
queda identificada para una futura divulgación real.

## Verificación por un tercero

1. Abrir la URL anterior con una cuenta colaboradora: el aviso aparece como `draft`.
2. `gh api repos/alejandrorevillaEng/reportaudit-lab/security-advisories/GHSA-h9wj-g8cp-pwgx --jq '[.state,.published_at]|@tsv'`
   → `draft` y `null`.
3. Las personas sin acceso al aviso ven un 404: el detalle no se filtra públicamente.
