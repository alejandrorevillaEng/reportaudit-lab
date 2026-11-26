# OpenSSF Scorecard — ReportAudit

- Fecha del análisis: 2026-11-26T18:19:07Z (re-exportado manualmente tras publicar v1.0.0)
- Commit analizado: `f95eabfe39909dd24f19055d37126a025b1aebc6`
- Scorecard v5.5.0
- Puntuación global: **6.2 / 10**
- Visor: https://scorecard.dev/viewer/?uri=github.com/alejandrorevillaEng/reportaudit-lab
- Datos: https://api.scorecard.dev/projects/github.com/alejandrorevillaEng/reportaudit-lab
- Ejecución: https://github.com/alejandrorevillaEng/reportaudit-lab/actions/runs/45874919936

## Checks con peor nota

| Check | Nota | Motivo y lectura |
|---|---|---|
| Branch-Protection | -1 (sin datos) | El token de GitHub Actions no puede leer las reglas clásicas de protección. No indica que falten: `main` tiene 4 checks obligatorios y 1 aprobación. Es una limitación del token, documentada por Scorecard. |
| Pinned-Dependencies | 0 | 12 acciones de GitHub y 5 de terceros usan etiquetas (`@v6`, `@v4`) en lugar de hashes. Es el reto opcional S.3: se puede mejorar fijando por SHA de commit; Dependabot sigue funcionando con ese formato. |
| Code-Review | 0 | Solo 1 de 12 cambios aparece aprobado por otra persona. GitHub impide aprobar PRs ya fusionados, y parte de la historia se fusionó con privilegios de administrador. La revisión por escrito existe, pero Scorecard solo cuenta aprobaciones formales. |
| Maintained | 0 | El repositorio tiene menos de 90 días. No es un problema de seguridad, es un dato de antigüedad. |
| License / Fuzzing | 0 | No hay archivo `LICENSE` ni integración de fuzzing. Entran fuera del alcance de este laboratorio (el fuzzing se verá en cursos posteriores). |

## Checks destacados

| Check | Nota | Evidencia |
|---|---|---|
| Security-Policy | 10 | `SECURITY.md` en la raíz |
| Token-Permissions | 10 | Permisos de solo lectura por defecto en los tres workflows |
| Dependency-Update-Tool | 10 | `.github/dependabot.yml` |
| Vulnerabilities | 10 | 0 vulnerabilidades abiertas |
| Signed-Releases | 8 | 1 de 1 release tiene al menos un artefacto firmado; Scorecard no reconoce el `.tar.gz` como provenance, pero sí el bundle `.sigstore.json` |
| SAST | 9 | CodeQL en 28 de 30 commits |
| CI-Tests | 9 | 13 de 14 PRs fusionados con CI |

## Interpretación

6.2 no es una certificación: mide prácticas observables, no seguridad real. El check más útil para
elegir una dependencia es `Vulnerabilities` (10 aquí) combinado con `Maintained`; el más engañoso
sin contexto es `Maintained` (0 por repositorio joven) o `Branch-Protection` (-1 por permisos del
token), que parecen fallos y no lo son.
