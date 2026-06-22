.PHONY: init init-python init-tex manuscript clean-manuscript check-tex-style prepare-elsevier-submission dashboard

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
