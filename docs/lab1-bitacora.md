# Laboratorio 1 — Bitácora de auditoría de la cadena de suministro

- **Autor/a:** Alejandro Revilla Blanco
- **Repositorio:** https://github.com/alejandrorevillaEng/reportaudit-lab
- **Sistema operativo y versión de Python usados:** Ubuntu 24.04 (WSL2), Python 3.12.3
- **Compañero revisor:** `isramrtnz` (Israel Gallego), colaborador con permiso de escritura
- **SonarQube Cloud — Organization Key:** `alejandrorevillaeng`
- **SonarQube Cloud — Project Key:** `alejandrorevillaEng_reportaudit-lab`

> Las secciones se han ido completando a medida que avanzaba el laboratorio. Las
> evidencias de terminal están en `docs/evidencias/` y las capturas de pantalla
> en el documento Word de la asignatura (fuera del repositorio).

---

## Parte B — Auditoría manual (antes de usar ninguna herramienta)

| # | Función | Línea | Qué sospechas | Dato de entrada (*source*) | Destino peligroso (*sink*) |
|---|---------|-------|---------------|---------------------------|---------------------------|
| 1 | Constantes (`NOTIFICATION_API_KEY`, `SMTP_PASSWORD`) | 21-22 | Credenciales expuestas en el código | N/A | N/A |
| 2 | `cargar_configuracion` | 27-34 (sink: 33) | YAML inseguro (`Loader=yaml.Loader`) | Contenido de `config.yaml` | `yaml.load(f, Loader=yaml.Loader)` |
| 3 | `buscar_reportes_cliente` | 37-45 (sink: 41-42) | Inyección SQL por concatenación | `nombre_cliente` (`/reportes?cliente=...`) | `cursor.execute(query)` |
| 4 | `convertir_a_pdf` | 48-52 (sink: 50-51) | Inyección de comandos con `os.system` | `nombre_archivo` (`/convertir?archivo=...`) | `os.system(comando)` |
| 5 | `hash_password_legacy` | 55-57 (sink: 57) | Hash MD5 inseguro sin sal | `password` | `hashlib.md5(...)` |

**Impacto en el negocio:**

1. **Credenciales expuestas:** cualquiera que vea el código tiene acceso a la API de notificaciones y al servidor SMTP, y puede enviar correos fraudulentos en nombre de ReportAudit.
2. **YAML inseguro:** un atacante que pueda modificar `config.yaml` puede instanciar objetos Python arbitrarios y ejecutar código en el servidor.
3. **Inyección SQL:** permite leer, modificar o borrar los reportes de todos los clientes y, según el motor, escalar a operaciones administrativas.
4. **Inyección de comandos:** permite ejecutar comandos del sistema en el servidor (robo de datos, malware, borrado de archivos).
5. **Hash MD5:** las contraseñas del sistema legado pueden crackearse en poco tiempo y dar acceso no autorizado a las cuentas de los clientes.

**Síntoma observado (Parte C):** al pedir `http://127.0.0.1:8087/reportes?cliente=o'brien_ltd` el servicio devolvió `Internal Server Error` y la terminal mostró `sqlite3.OperationalError: near "brien_ltd": syntax error`. El apóstrofo rompió la consulta concatenada: prueba directa de que la entrada del usuario se estaba interpretando como SQL.

---

## Matriz de detección (completada)

| Hallazgo | Manual (B) | SonarQube for IDE sin conexión (D) | IDE Connected Mode (E) | SonarQube Cloud (F) | CodeQL (F) | Semgrep (H) | Trivy (L) |
|---|---|---|---|---|---|---|---|
| H1 Inyección SQL en `buscar_reportes_cliente` | ✓ | ✗ | ✓ (S3649) | ✓ | ✓ `py/sql-injection` | ✗ | n/a |
| H2 Inyección de comandos en `convertir_a_pdf` | ✓ | ✗ | ✓ (S2076) | ✓ | ✓ `py/command-line-injection` | ✗ | n/a |
| H3 YAML inseguro en `cargar_configuracion` | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ `avoid-pyyaml-load` | n/a |
| H4 Hash MD5 en `hash_password_legacy` | ✓ | ✓ (S4790) | ✓ (S4790) | ✓ | ✓ `py/weak-sensitive-data-hashing` | ✓ `insecure-hash-algorithm-md5` + `md5-used-as-password` | n/a |
| H5 Clave de API escrita en el código | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| H6 Contraseña SMTP escrita en el código | ✓ | ✓ (S2068) | ✓ (S2068, S7552) | ✓ | ✓ `py/clear-text-logging-sensitive-data` (por imprimirla) | ✗ | ✗ |

**Conclusión de la matriz:** ninguna herramienta lo detectó todo. CodeQL y SonarQube Cloud son buenos en flujos de datos (H1, H2, H4), Semgrep encontró el YAML (H3) que ningún SAST de grafo vio, y los secretos (H5, H6) solo aparecieron de forma fiable en la revisión manual y parcialmente en el IDE. Trivy, centrado en dependencias y formatos de secretos de proveedor, no encontró las credenciales de ReportAudit. Depender de un único motor dejaría huecos: hacen falta revisión humana + SAST + SCA + escáner de secretos.

**Parte F — Connected Mode:** con la conexión a SonarQube Cloud el editor aplica las reglas del proyecto y descarga el *taint analysis* calculado en el servidor: aparecieron `pythonsecurity:S3649` (línea 42) y `pythonsecurity:S2076` (línea 51), además de `secrets:S7552` para la contraseña SMTP. Sin conexión solo se veían `S4790` y `S2068`.

---

## Backlog del laboratorio (Issues)

Milestone: **Lab 1 - Secure supply chain** (13 Issues).

| Issue | Título | PR o evidencia de cierre |
|---|---|---|
| #1 | Adopt an international pull request template | PR #14 (fusionado) |
| #2 | Run SAST (SonarQube Cloud and CodeQL) on every pull request | PR #15 (fusionado) |
| #3 | Block insecure commits with a Semgrep pre-commit hook | PR #16 (fusionado) |
| #4 | Enable Dependabot alerts and security updates | PR #17 + ajustes de Security (cerrado) |
| #5 | Remediate the findings of the security audit | PR #20 (fusionado) |
| #6 | Upgrade the vulnerable dependencies | PR #21 (fusionado) |
| #7 | Publish the audit log and the before/after evidence | PR #22 (documentación) |
| #8 | Detect ReportAudit credentials in the whole Git history | PR de Gitleaks (Parte O) |
| #9 | Make SCA and secret scanning required checks on main | PR de puertas + ajustes (Parte P) |
| #10 | Publish a security policy and a private vulnerability reporting channel | PR de SECURITY.md (Parte Q) |
| #11 | Release v1.0.0 with an SBOM and signed provenance | Release v1.0.0 (Parte R) |
| #12 | Measure supply-chain maturity with OpenSSF Scorecard | PR de Scorecard (Parte S) |
| #13 | Build the CRA evidence index | PR del expediente (Parte T) |

---

## Parte J — SBOM: el iceberg medido

Ejecutado con Syft 1.52.0 (instalado verificando SHA-256 con el `checksums.txt` oficial):

```bash
./tools/syft scan dir:. --exclude './venv/**' --exclude './tools/**' \
  -o cyclonedx-json=docs/evidencias/sbom.cyclonedx.json -o table
```

| Dato | Valor |
|---|---|
| Dependencias directas (`requirements.in`) | 2 (`flask`, `pyyaml`) |
| Componentes Python en el SBOM | 9 |
| Otros componentes que aparecen en el SBOM | 4 GitHub Actions (`actions/checkout`, `SonarSource/sonarqube-scan-action`, `github/codeql-action/init`, `github/codeql-action/analyze`). También aparecen 2 entradas de tipo `file` (el workflow y `requirements.txt`). |
| Formato y versión de especificación del SBOM | `bomFormat: CycloneDX`, `specVersion: 1.7` |

El "iceberg": pedimos dos librerías y el escáner ve nueve componentes Python más cuatro acciones. Las dependencias transitivas (`blinker`, `click`, `itsdangerous`, `jinja2`, `markupsafe`, `werkzeug`, `colorama`) están bajo el agua y son precisamente donde aparecieron las vulnerabilidades.

---

## Parte J/K — Triage de vulnerabilidades de dependencias (Grype)

```bash
./tools/grype sbom:docs/evidencias/sbom.cyclonedx.json | tee docs/evidencias/grype-antes.txt
```

| Paquete | Versión | ¿Directa o transitiva? | CVE / GHSA | Severidad | Corregida en | ¿Explotable en ReportAudit? | Decisión |
|---|---|---|---|---|---|---|---|
| werkzeug | 3.0.1 | Transitiva (`# via flask`) | GHSA-2g68-c3qc-8985 | High | 3.0.3 | No: afecta a la consola del depurador; `app/servicio.py:64` fija `debug=False` | Actualizar + VEX |
| werkzeug | 3.0.1 | Transitiva | GHSA-q34m-jh98-gwm2 | Medium | 3.0.6 | No: requiere cabeceras multipart concretas que el servicio no procesa | Actualizar |
| werkzeug | 3.0.1 | Transitiva | GHSA-f9vj-2wh5-fj8j | Medium | 3.0.6 | No: ruta de multipart no usada | Actualizar |
| jinja2 | 3.1.2 | Transitiva (`# via flask`) | GHSA-h5c8-rqwp-cp95 | Medium | 3.1.3 | No: ReportAudit responde con `jsonify`, no renderiza plantillas | Actualizar |
| jinja2 | 3.1.2 | Transitiva | GHSA-h75v-3vvj-5mfj | Medium | 3.1.4 | No: evasión de sandbox de plantillas, sin plantillas controladas por el usuario | Actualizar |
| werkzeug | 3.0.1 | Transitiva | GHSA-hgf8-39gv-g3f2 | Medium | 3.1.4 | No: parsado de multipart no usado | Actualizar |
| werkzeug | 3.0.1 | Transitiva | GHSA-29vq-49wr-vm6x | Medium | 3.1.6 | No: no se sirven archivos estáticos | Actualizar |
| jinja2 | 3.1.2 | Transitiva | GHSA-q2x7-8rv6-6q7h | Medium | 3.1.5 | No: sandbox de plantillas no usado | Actualizar |
| werkzeug | 3.0.1 | Transitiva | GHSA-87hc-h4r5-73f7 | Medium | 3.1.5 | No: no se usa esa utilidad de cabeceras | Actualizar |
| jinja2 | 3.1.2 | Transitiva | GHSA-cpwx-vrp4-4pq7 | Medium | 3.1.6 | No: compilación de plantillas no usada | Actualizar |
| werkzeug | 3.0.1 | Transitiva | GHSA-g6x2-hccm-hh4m | Medium | 3.1.9 | No: routing/cabeceras concretas no usadas | Actualizar |
| jinja2 | 3.1.2 | Transitiva | GHSA-gmj6-6f8f-6699 | Medium | 3.1.5 | No: sandbox no usado | Actualizar |
| flask | 3.0.0 | Directa (`# via -r requirements.in`) | GHSA-68rp-wp8r-4726 | Low | 3.1.3 | No: no se usa la funcionalidad afectada | Actualizar |

**Comparación con Dependabot:** las alertas de Dependabot aparecen en Security → Dependabot y llegan en PRs agrupados; Grype las ve directamente sobre el SBOM, sin esperar a GitHub. En este laboratorio los PRs automáticos que aparecieron fueron de actualización de acciones (`checkout` v7 y `sonarqube-scan-action` v8); las correcciones de pip se hicieron en el PR #21 porque las alertas de seguridad de Dependabot aún no se habían publicado en el repositorio. Las versiones coinciden en espíritu: ambas señalan Werkzeug/Jinja2/Flask como paquetes a actualizar.

**Documento VEX:** [docs/evidencias/reportaudit.openvex.json](evidencias/reportaudit.openvex.json). Justificación en una frase: *el aviso GHSA-2g68-c3qc-8985 afecta al depurador de Werkzeug, que ReportAudit nunca activa (`debug=False` en `app/servicio.py:64`), por lo que la ruta vulnerable no se ejecuta; aun así la dependencia se actualiza porque el parche es barato.*

---

## Parte L — Trivy: dependencias y secretos

```bash
./tools/trivy fs --scanners vuln,secret --skip-dirs venv --skip-dirs tools . \
  | tee docs/evidencias/trivy-antes.txt
```

Trivy 0.74.0 informó de **13 vulnerabilidades** en `requirements.txt` (tipo `pip`) y **0 secretos**, coincidiendo con Grype en los paquetes afectados. No detectó las dos credenciales escritas en `app/reporte_auditoria.py`: no siguen el formato de ningún proveedor conocido. SonarQube for IDE sí las marcó por el nombre de variable (`S2068`, `S7552`). Un escaneo de secretos limpio no demuestra que no haya secretos: demuestra solo que no encajan con una firma conocida.

---

## Parte L y M — Antes y después

| Medida | Antes | Después |
|---|---|---|
| Hallazgos de Semgrep en `app/` | 3 findings bloqueantes (YAML + 2 reglas MD5) | `pre-commit run --all-files` → Passed |
| Alertas abiertas de CodeQL (Security → Code scanning) | 4 (`py/sql-injection`, `py/command-line-injection`, `py/weak-sensitive-data-hashing`, `py/clear-text-logging-sensitive-data`) | 4 en estado **Fixed** |
| Vulnerabilidades en SonarQube Cloud (rama main) | Presentes en el análisis inicial | 0 tras el PR de corrección |
| Security Hotspots por revisar en SonarQube Cloud | 1 (uso de `subprocess.run`) | Revisado como Safe: lista de argumentos, `shell=False` y lista blanca de nombre |
| Vulnerabilidades de Grype sobre el SBOM | 13 | `No vulnerabilities found` |
| Alertas abiertas de Dependabot | Dependencias desactualizadas | Sin alertas abiertas tras el PR #21 |
| Secretos en el código actual (Gitleaks) | 2 en el historial, 0 en el árbol de trabajo | 2 localizados, rotados y basados en `.gitleaksignore` |

**Correcciones aplicadas en el PR #20 (`app/reporte_auditoria.py`):**

- Consulta parametrizada: `cursor.execute("SELECT * FROM reportes WHERE cliente = ?", (nombre_cliente,))`.
- `subprocess.run(["wkhtmltopdf", nombre_archivo, salida], check=False)` con validación previa `^[A-Za-z0-9_][A-Za-z0-9_.-]*\.html$`.
- `yaml.safe_load(f)` en lugar de `yaml.Loader`.
- PBKDF2-HMAC-SHA256 con sal aleatoria de 16 bytes y 600.000 iteraciones.
- Credenciales leídas de `REPORTAUDIT_NOTIFICATION_API_KEY` y `REPORTAUDIT_SMTP_PASSWORD`; la clave ya no se imprime ni parcialmente.

**Verificación funcional tras el cambio:**

| Dirección | Resultado |
|---|---|
| `/reportes?cliente=acme_corp` | 2 reportes (igual que antes) |
| `/reportes?cliente=o'brien_ltd` | 1 reporte (antes: HTTP 500) |
| `/convertir?archivo=informe.html` | 200 |
| `/convertir?archivo=informe final.html` | 400 |

---

## Preguntas de comprobación (Sección 7 de la guía)

1. **¿Qué vive en Windows, en Ubuntu y en GitHub?** En Windows están VS Code, el navegador y el documento Word de capturas. En Ubuntu (WSL2) viven el proyecto en `~/reportaudit-lab`, el entorno virtual, Git y las herramientas (Semgrep, Syft, Grype, Trivy, Gitleaks). En GitHub viven el repo, los PRs, Actions, los secretos, la protección de `main`, Dependabot y los resultados de CodeQL. Se trabaja en Ubuntu porque las herramientas y los runners del pipeline son Linux: así la máquina se comporta igual que la nube.

2. **Directa vs. transitiva.** Directa es la que el equipo declara (`flask`, `pyyaml` en `requirements.in`). Transitiva es la que llega por otra: `werkzeug==3.0.1` aparece en el SBOM y en el lockfile con `# via flask`. El SBOM tenía 9 componentes Python para solo 2 directas: ahí está el iceberg.

3. **Source y sink.** El *source* es el dato de entrada controlado por el atacante (`request.args.get("cliente")` en `app/servicio.py:41`); el *sink* es el punto peligroso (`cursor.execute` en `app/reporte_auditoria.py:42`). El dato atraviesa los dos archivos sin validación.

4. **¿Por qué fallaba `o'brien_ltd`?** La consulta se construía concatenando el nombre entre comillas: el apóstrofo cerraba la cadena SQL y `brien_ltd` se interpretaba como código, produciendo `sqlite3.OperationalError`. Eso demuestra inyección SQL, no un simple error de formato.

5. **¿Qué aporta Semgrep que no aportan SonarQube/CodeQL?** Detecta patrones de código concretos con reglas locales rápidas, como `yaml.load` con `Loader` inseguro (H3), que los motores de análisis de flujo no señalaron. Pero el hook solo mira `app/` en la máquina del desarrollador: no protege el servidor, no cubre dependencias y se puede saltar con `--no-verify`. Por eso se complementa con SAST en la nube, SCA y puertas obligatorias.

6. **¿Es un error que no detecten lo mismo?** No. Cada herramienta tiene reglas y granularidad distintas: CodeQL y SonarQube hacen análisis de flujo, Semgrep busca patrones sintácticos, Trivy mira dependencias y secretos con formatos conocidos. La matriz muestra huecos complementarios, no fallos.

7. **¿Por qué el PR de código no cerró las alertas de Dependabot ni el PR de Dependabot las de CodeQL?** Porque miden cosas distintas: CodeQL analiza el código fuente y sus alertas se cierran cuando el patrón vulnerable desaparece; Dependabot vigila versiones de paquetes y solo se cierran cuando el manifiesto/lockfile usa una versión corregida. Cambiar `app/` no cambia `requirements.txt`, y viceversa.

8. **¿Borrar un secreto es corregirlo?** No. El secreto ya quedó en el historial de Git: cualquiera con acceso al repo puede recuperarlo. Corregir significa sacarlo del código, **rotarlo en el proveedor**, impedir que vuelva a entrar (regla de Gitleaks + push protection) y documentar la rotación.

9. **¿Qué resuelve un VEX?** Convierte una decisión informal ("lo ignoro") en una afirmación verificable: qué vulnerabilidad, en qué producto y versión, con qué justificación (`vulnerable_code_not_in_execute_path`) y con evidencia en el código. Nuestro VEX documenta GHSA-2g68-c3qc-8985 en `werkzeug@3.0.1` y explica que `debug=False` deja la ruta fuera del camino de ejecución; aun así se actualizó la dependencia.

10. **¿Qué comprueba el instalador?** Fija versiones concretas (Syft 1.52.0, Grype 0.119.0, Trivy 0.74.0), descarga el `checksums.txt` oficial de la misma release, calcula el SHA-256 local y compara antes de ejecutar; si no coincide, se detiene. No puede garantizar que la release oficial no haya sido comprometida ni que el binario sea seguro en sí mismo (caso TeamPCP, marzo de 2026): por eso también se fija la versión y se vigilan las acciones con Dependabot.

11. **¿Código limpio, historial sucio?** El PR de corrección sustituyó las constantes por variables de entorno, así que `gitleaks dir app` no encuentra nada. `gitleaks git .` recorre los commits y encuentra las credenciales en el commit de importación. El riesgo solo se cierra con la **rotación**; el `.gitleaksignore` evita ruido, no elimina el secreto.

12. **¿Por qué no exigir pip-audit desde la Parte G?** La idea del *ratchet*: se empieza con las comprobaciones que el código puede pasar y se añaden puertas nuevas cuando el equipo ha corregido lo que detectan. Exigir SCA desde el primer PR habría bloqueado el pipeline por las 13 vulnerabilidades sembradas; se añadió en la Parte P, tras la corrección y la actualización de dependencias.

13. **¿Alerta de Dependabot vs. check `SCA - pip-audit`?** La alerta es informativa y vive en Security → Dependabot; el check es una puerta obligatoria en cada PR que falla el merge si `requirements.txt` contiene una versión vulnerable, incluso si nadie ha mirado la alerta.

14. **¿Qué demuestra `gh attestation verify`?** Que el artefacto fue producido por el workflow `publicar-version.yml` de este repositorio a partir del tag `v1.0.0` y que no ha sido modificado desde entonces; con `--predicate-type https://cyclonedx.org/bom` demuestra además que ese SBOM está atestado. No demuestra que el código sea seguro ni que quien firmó sea una persona concreta. `SHA256SUMS` solo comprueba integridad del archivo: alguien con acceso a la release podría regenerar ambos; la atestación está firmada por Sigstore y ligada a la identidad del workflow.

15. **¿Canal privado y `SECURITY.md`?** Un Issue público filtra la vulnerabilidad antes de que exista parche y puede avisar a atacantes. `SECURITY.md` dice cómo reportar en privado, qué plazos de respuesta se ofrecen y qué versión sigue recibiendo soporte.

16. **¿Scorecard 0 en Maintained?** No es una vulnerabilidad: significa que el proyecto lleva menos de 90 días con actividad pública (o que la métrica no tiene datos). Es una señal de mantenimiento, no de explotabilidad. Las métricas hay que leerlas con contexto: un 0 puede ser simplemente "proyecto nuevo".

17. **¿Comparación con la Práctica 2?** En la respuesta B5 imaginábamos un SBOM, una política de divulgación y una firma de releases. Ahora existen de verdad: `sbom.cyclonedx.json` atestado en la release, `SECURITY.md`, `SHA256SUMS` y los `.sigstore.json` verificables. Sigue sin existir la declaración UE de conformidad, el marcado CE ni la documentación técnica del Anexo VII: están fuera del alcance del laboratorio.

---

## Checklist de entrega (sección 8)

- [x] Repositorio público con el commit de importación, el de la plantilla y los PRs de configuración/corrección fusionados.
- [x] `main` protegida: PR, una aprobación requerida, resolución de conversaciones y checks SAST obligatorios (los dos SCA/secretos se añaden en la Parte P).
- [x] Colaborador revisor `isramrtnz` añadido y aceptado.
- [x] Proyecto de SonarQube Cloud con `SONAR_TOKEN` en Actions y claves reales en `sonar-project.properties`.
- [x] Captura del commit bloqueado por Semgrep (`docs/evidencias/pre-commit-bloqueo.txt` + captura en el Word).
- [x] Alertas de CodeQL en estado Fixed tras la corrección.
- [x] `docs/evidencias/` con SBOM antes/después, salidas de Grype y Trivy antes/después y VEX.
- [x] PR de auditoría con la plantilla internacional, tabla de hallazgos, VEX enlazado y credenciales a rotar declaradas.
- [ ] Secciones O–T y documentación final (se completan al cierre del laboratorio).
- [x] `.github/PULL_REQUEST_TEMPLATE.md` en `main`; commits y PRs con Conventional Commits y comentarios etiquetados.
- [ ] Regla propia de Gitleaks y puertas SCA/secretos (Partes O y P).
- [ ] `SECURITY.md`, simulacro, release v1.0.0, Scorecard y expediente CRA (Partes Q–T).

> Nota de transparencia: GitHub no permite que el autor apruebe su propio PR. Los PRs se han fusionado con privilegios de administrador y se ha dejado constancia en cada review; la aprobación formal de `isramrtnz` debe registrarse en su cuenta.

---

## Bloque final — Publicar y demostrar (Partes O–T)

### O. Secretos en el historial (Gitleaks)

| Escaneo | Comando | N.º de hallazgos | Commit(s) donde aparecen |
|---|---|---|---|
| Código actual, reglas por defecto | `gitleaks dir app` | 0 | Ninguno |
| Historial, reglas por defecto | `gitleaks git .` | 2 | `390d7cc` (importación) |
| Historial, con regla propia | `gitleaks git . -c .gitleaks.toml` | 2 | `390d7cc` (importación) |
| Historial, tras .gitleaksignore | `gitleaks git . -c .gitleaks.toml` | 0 | Ninguno (baseline de 2 huellas rotadas) |

¿Por qué el código actual está limpio y el historial no? ¿Qué medida de la Parte M cierra el riesgo
y cuál no lo cierra? *(Se completa en el PR final.)*

### P. Puertas obligatorias en main

| Check | ¿Exigido en main? | Resultado en el PR de prueba (test/puerta-sca) |
|---|---|---|
| SAST - SonarQube Cloud | Sí | Pass (el código no cambió) |
| SAST - CodeQL | Sí | Pass (el código no cambió) |
| SCA - pip-audit | Sí | **Fail** (werkzeug 3.0.1 vulnerable) |
| Secretos - Gitleaks | Sí | Pass |

### Q. Divulgación coordinada (simulacro)

- Informe recibido de (usuario de GitHub): *(por completar)*
- Identificador del borrador de aviso (GHSA-...): *(por completar)*
- Severidad y vector CVSS: *(por completar)*
- CWE: CWE-89 (SQL Injection)
- Versiones afectadas / versión corregida: < 1.0.0 / 1.0.0

### R. Versión 1.0.0 verificable

| Comprobación | Comando | Resultado |
|---|---|---|
| Huellas SHA-256 | `sha256sum -c SHA256SUMS` | *(por completar)* |
| Procedencia (SLSA) | `gh attestation verify reportaudit-1.0.0.tar.gz --repo alejandrorevillaEng/reportaudit-lab` | *(por completar)* |
| SBOM atestado | `gh attestation verify ... --predicate-type https://cyclonedx.org/bom` | *(por completar)* |
| Archivo alterado | `gh attestation verify alterado.tar.gz --repo ...` | *(por completar)* |

### S. Madurez (OpenSSF Scorecard)

| Check | Puntuación (0–10) | Qué la explica |
|---|---|---|
| Puntuación global | *(por completar)* | |
| *(por completar)* | | |

### T. Expediente de evidencias

Ver `docs/cra/expediente-evidencias.md`.

Compara el expediente con tu respuesta B5 de la Práctica 2: ¿qué evidencia imaginaste que ahora
existe de verdad, y cuál sigue sin existir? *(Se completa en el PR final.)*
