.PHONY: init init-python init-tex manuscript manuscript-diff clean-manuscript check-tex-style prepare-elsevier-submission dashboard research-setup research-run research-status research-deliver research-export test-runtime

init: init-python init-tex

init-python:
	@command -v uv >/dev/null 2>&1 || { echo "uv not found; install uv and retry." >&2; exit 1; }
	@uv sync

init-tex:
	@bash scripts/init-tex-env.sh

manuscript:
	@cd docs/writing/manuscript && latexmk -pdf -r ../../../.latexmkrc main.tex
	@test -s docs/writing/manuscript/build/main.pdf

manuscript-diff:
	@base="$${BASE_SHA:-$${BASE_REF:-}}"; \
	if [ -z "$$base" ]; then \
		base="$$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"; \
	fi; \
	if [ -z "$$base" ] && git rev-parse --verify origin/master >/dev/null 2>&1; then \
		base="origin/master"; \
	fi; \
	if [ -z "$$base" ] && git rev-parse --verify origin/main >/dev/null 2>&1; then \
		base="origin/main"; \
	fi; \
	BASE_SHA="$${base:-HEAD~1}" \
	HEAD_SHA="$${HEAD_SHA:-$${HEAD_REF:-HEAD}}" \
	scripts/build-manuscript-diff.sh docs/writing/manuscript/build/manuscript-diff.pdf

clean-manuscript:
	@cd docs/writing/manuscript && latexmk -C -r ../../../.latexmkrc main.tex || true
	@rm -rf docs/writing/manuscript/build

check-tex-style:
	@if command -v python >/dev/null 2>&1; then \
		python scripts/check-tex-sentence-lines.py; \
	else \
		python3 scripts/check-tex-sentence-lines.py; \
	fi

prepare-elsevier-submission:
	@bash scripts/prepare-elsevier-submission.sh

# ARGS are forwarded explicitly; Python is the portable entrypoint.
PYTHON ?= python3
research-setup:
	@$(PYTHON) scripts/research.py setup $(ARGS)
research-run:
	@$(PYTHON) scripts/research.py run $(ARGS)
research-status:
	@$(PYTHON) scripts/research.py status $(ARGS)
research-deliver:
	@$(PYTHON) scripts/research.py deliver $(ARGS)
research-export:
	@$(PYTHON) scripts/research.py export $(ARGS)
dashboard:
	@$(PYTHON) scripts/research.py status --dashboard-from "$(SNAPSHOT)" --dashboard DASHBOARD.md
test-runtime:
	@$(PYTHON) -m unittest discover -s tests -p 'test_research*.py' -v
