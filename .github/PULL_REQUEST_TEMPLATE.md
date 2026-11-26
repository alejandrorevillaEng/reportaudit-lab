## 🔗 Linked issue
<!-- First the context. "Closes #12" closes the Issue when merged into main.
     If the PR does not finish it, use "Refs #12". Without an Issue: "N/A" and why. -->
Closes #

## 📝 Summary
<!-- What problem does it solve and why, in 2-3 sentences, in English:
     the working language of international engineering teams. -->

## 🔄 Type of change
<!-- Must match the Conventional Commits prefix of the PR title. -->
- [ ] `fix` — bug fix
- [ ] `feat` — new feature
- [ ] `refactor` — internal change, same behaviour
- [ ] `perf` — performance improvement
- [ ] `test` — tests added or changed
- [ ] `docs` — documentation only
- [ ] `build` / `ci` — dependencies, pipeline or configuration
- [ ] ⚠️ `BREAKING CHANGE` — breaks compatibility (explain the migration)

## 📋 What changed
<!-- The important technical changes, one per line. -->
-

## 🛡️ Security & supply-chain impact
<!-- Mandatory. If a box does not apply, tick it and write "N/A". -->
- [ ] No new dependencies, or each one is justified below (name, exact version, licence, why).
- [ ] All required checks are green (SAST, SCA, secrets) and no new code-scanning alerts.
- [ ] No secrets, tokens or personal data in the code, the commits or the logs.
- [ ] If dependencies changed, the SBOM will be regenerated in the next release.

**Findings addressed** <!-- One row per finding. Delete the table if none is fixed. -->

| ID | Detected by | Rule / CVE | File:line | Category (SAST/SCA/Secret) | Severity | Resolution |
|----|-------------|------------|-----------|----------------------------|----------|------------|
|    |             |            |           |                            |          |            |

**Accepted risks** <!-- Link to the VEX for what is NOT fixed and who accepts the risk. -->

**Credentials to rotate** <!-- Any credential ever in history is compromised. -->

## 🏗️ Design decisions
<!-- What the reviewer cannot deduce from the diff. -->
- **Approach and why:**
- **Alternatives discarded:**

## 👀 How to review
<!-- Recommended reading order and what to pay attention to. -->
1.

## 🧪 Testing & evidence
- [ ] Tested locally: the service starts and the affected endpoints behave as expected.
- [ ] `pre-commit run --all-files` passes.
- [ ] Evidence attached (terminal output, screenshots or reports in `docs/evidencias/`).

## ⚠️ Risks & rollback
<!-- What could go wrong and how to undo it. -->

## ✅ Author checklist
- [ ] I self-reviewed the diff on GitHub before requesting review.
- [ ] Small PR (ideally < 400 changed lines) about a single topic.
- [ ] The PR title follows Conventional Commits.
- [ ] Comments explain *why*, not *what*.
- [ ] If an AI assistant was used, I reviewed and understand every line I submit.
