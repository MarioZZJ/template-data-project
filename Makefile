.PHONY: init init-python init-tex manuscript manuscript-diff clean-manuscript check-tex-style prepare-elsevier-submission dashboard

init: init-python init-tex

init-python:
	@if command -v uv >/dev/null 2>&1; then \
		echo "Initializing Python environment with uv"; \
		uv sync || uv venv; \
	else \
		echo "uv not found. Install uv or use the existing project environment."; \
	fi

init-tex:
	@bash scripts/init-tex-env.sh

manuscript:
	@cd docs/writing/manuscript && latexmk -pdf -r ../../../.latexmkrc main.tex

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

dashboard:
	@sed -n '1,220p' DASHBOARD.md
