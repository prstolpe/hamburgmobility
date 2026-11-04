# Hamburger Straßenfunktionsplan – Pipeline
#
# Intended run order (crosssection runs before classify, because rule C-G30-02 needs the
# street space width):
#   fetch -> network -> conflate -> features -> crosssection -> classify -> coherence
#   -> discrepancy -> validate -> export -> web
# validate runs before export because the website shows its robustness mark ("unsicher").
#
# For now all targets are independent and phony. Later prompts replace them with file-based
# dependencies on data/interim/*.parquet so that only outdated stages are rebuilt.

SHELL := /bin/bash
.DEFAULT_GOAL := help

PIPELINE_TARGETS := fetch network conflate features crosssection classify coherence discrepancy export validate
.PHONY: help install dirs test web web-test a11y basemap site-data override-template $(PIPELINE_TARGETS)

# run_step(target, script): run pipeline/<script>.py if it exists, otherwise report that it is missing.
define run_step
	@if [ -f pipeline/$(2).py ]; then \
		uv run python -m pipeline.$(2); \
	else \
		echo "$(1): noch nicht implementiert (pipeline/$(2).py fehlt)"; \
	fi
endef

help: ## Show available targets
	@echo "Ziele:"
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-18s %s\n", $$1, $$2}'

install: ## Install dependencies (uv sync)
	uv sync

dirs: ## Create local data folders (not in git)
	@mkdir -p data/raw data/interim data/out

fetch: dirs ## Download sources from config/sources.yaml
	$(call run_step,fetch,s01_fetch)

network: dirs ## Build OSM network and segments
	$(call run_step,network,s02_network)

conflate: dirs ## Match official data to OSM segments
	$(call run_step,conflate,s03_conflate)

features: dirs ## Compute features per segment
	$(call run_step,features,s04_features)

crosssection: dirs ## Cross sections and feasibility
	$(call run_step,crosssection,s07_crosssection)

classify: dirs ## Rule-based target category
	$(call run_step,classify,s05_classify)

coherence: dirs ## Network coherence flags and overrides
	$(call run_step,coherence,s06_coherence)
	$(call run_step,coherence,s06b_overrides)

override-template: ## Template rows for new overrides (IDS="seg_... seg_...")
	@uv run python -m pipeline.override_template $(IDS)

discrepancy: dirs ## Discrepancy types and priority
	$(call run_step,discrepancy,s08_discrepancy)

export: dirs ## Export downloads, profiles, search index and PMTiles (data/out)
	$(call run_step,export,s09_export)

basemap: dirs ## Background map extract, fonts and sprites for the website (data/out/basemap)
	uv run python -m pipeline.s09b_basemap

web: ## Build the static website (needs make export and make basemap)
	npm --prefix web ci --no-fund --no-audit
	npm --prefix web run build

web-test: ## Unit tests of the website
	npm --prefix web test

a11y: ## Smoke and accessibility tests (axe-core) of the built site -> reports/web_accessibility.md
	npm --prefix web run a11y

site-data: ## Pack data/out for the GitHub release "data-latest" (deployment workflow)
	tar -czf data/site-data.tar.gz -C data/out .
	@echo "data/site-data.tar.gz: als Asset an das Release data-latest hängen (README, Abschnitt Veröffentlichen)"

validate: dirs ## Validation and sensitivity (before export) -> reports/validation.md
	$(call run_step,validate,validate)

test: ## Run tests (Python and website unit tests)
	uv run pytest
	@if [ -d web/node_modules ]; then npm --prefix web test; fi
