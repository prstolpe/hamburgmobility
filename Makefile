# Hamburger Straßenfunktionsplan – Pipeline
#
# Intended run order (crosssection runs before classify, because rule C-G30-02 needs the
# street space width):
#   fetch -> network -> conflate -> features -> crosssection -> classify (+harmonise) -> coherence
#   -> cycle-demand -> cycle-network -> ist-facility -> discrepancy -> validate -> export -> web
# discrepancy reads the Ist cycle facility (rules.yaml S-FEAT-13) and the parallel route of the Soll cycle network
# (S-FEAT-11) from ist-facility (c03b); both need the cycle graph and the Soll cycle network, so discrepancy runs after
# the first cycling stages (rules.yaml 0.20.0, Review 2026-11 F21/F26). The classification does not need them.
# validate runs before export because the website shows its robustness mark ("unsicher").
# coherence checks N1–N5 (N7 is part of N2); the junction part (formerly N6: junctions without a Soll type, N5 transitions per junction) needs the Soll
# junction type and runs in the junctions stage (c07) of the cycling chain (rules.yaml 0.19.0, Review 2026-11 F09).
#
# For now all targets are independent and phony. Later prompts replace them with file-based
# dependencies on data/interim/*.parquet so that only outdated stages are rebuilt.

SHELL := /bin/bash
.DEFAULT_GOAL := help

PIPELINE_TARGETS := fetch network conflate features crosssection classify coherence discrepancy export validate
# Cycle network extension (prompts 14–21, docs/guide_radnetz.md); runs after classify (needs cat_final).
#   cycle-demand -> cycle-network -> ist-facility -> cycle-principles -> cycle-facility -> cross-section-soll
#   -> junctions -> export-cycling
# ist-facility (c03b) computes the Ist facility once per segment for c04, c05 and s08 (V-INV-08).
# junctions (c07) reads the Soll lanes of cross-section-soll (J-14/J-15) and the N5 nodes of coherence and writes the section "Übergänge (N5)".
CYCLING_TARGETS := cycle-demand cycle-network ist-facility cycle-principles cycle-facility cross-section-soll junctions export-cycling
.PHONY: help install dirs test web web-test a11y basemap site-data override-template rerun $(PIPELINE_TARGETS) $(CYCLING_TARGETS)

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

classify: dirs ## Rule-based target category, then harmonisation along streets and carriageways (H-STR-01, H-PAIR-01)
	$(call run_step,classify,s05_classify)
	$(call run_step,classify,s05b_harmonise)

coherence: dirs ## Network coherence flags N1-N5 and overrides (junction part runs in junctions)
	$(call run_step,coherence,s06_coherence)
	$(call run_step,coherence,s06b_overrides)

override-template: ## Template rows for new overrides (IDS="seg_... seg_...")
	@uv run python -m pipeline.override_template $(IDS)

discrepancy: dirs ## Discrepancy types and priority (needs ist-facility)
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

cycle-demand: dirs ## Cycle graph and cycle demand model (prompt 15)
	$(call run_step,cycle-demand,c01_cycle_graph)
	$(call run_step,cycle-demand,c02_cycle_demand)

cycle-network: dirs ## Target cycle network: hierarchy and gap closing (prompt 16)
	$(call run_step,cycle-network,c03_cycle_network)

ist-facility: dirs ## Ist cycle facility per segment (S-FEAT-13) and parallel route of the Soll network (S-FEAT-11)
	$(call run_step,ist-facility,c03b_ist_facility)

cycle-principles: dirs ## Five principles per route and network, Ist and Soll (prompt 17)
	$(call run_step,cycle-principles,c04_principles)

cycle-facility: dirs ## Cycle facility type and width per segment (prompt 18)
	$(call run_step,cycle-facility,c05_facility)

cross-section-soll: dirs ## Target cross section: lanes, placement, space allocation (prompt 19)
	$(call run_step,cross-section-soll,c06_cross_section_soll)

junctions: dirs ## Target junction type, cyclist treatment per node (prompt 20) and junction coherence report
	$(call run_step,junctions,c07_junctions)

export-cycling: dirs ## Cycling validation (c08) and export incl. cycling layers (prompt 21) -> reports/validation_cycling.md
	$(call run_step,export-cycling,c08_validate_cycling)
	$(call run_step,export-cycling,s09_export)

# rerun FROM=<stage>: CHAIN from FROM (street stages, the first cycling stages, ist-facility and discrepancy), then
# validate alongside the rest of the cycling chain (they share no outputs; the junction coherence part belongs to junctions), then
# export-cycling. FROM may also name a stage of the cycling tail (validate is then skipped).
# Workers per stage: SFP_WORKERS (default all cores, 1 = serial).
CHAIN := network conflate features crosssection classify coherence cycle-demand cycle-network ist-facility discrepancy
TAIL := cycle-principles cycle-facility cross-section-soll junctions
FROM ?= classify
rerun: dirs ## Full rerun from FROM (default classify) to export; validate runs alongside the cycling chain
	@run=0; for s in $(CHAIN); do \
		if [ "$$s" = "$(FROM)" ]; then run=1; fi; \
		if [ $$run = 1 ]; then $(MAKE) --no-print-directory $$s || exit 1; fi; \
	done; \
	if [ $$run = 1 ]; then \
		$(MAKE) --no-print-directory validate > data/interim/validate.log 2>&1 & v=$$!; \
		$(MAKE) --no-print-directory $(TAIL); c=$$?; \
		wait $$v; vs=$$?; cat data/interim/validate.log; \
		if [ $$c -ne 0 ] || [ $$vs -ne 0 ]; then echo "rerun: Abbruch (Radnetz $$c, validate $$vs)"; exit 1; fi; \
	else \
		for s in $(TAIL); do \
			if [ "$$s" = "$(FROM)" ]; then run=1; fi; \
			if [ $$run = 1 ]; then $(MAKE) --no-print-directory $$s || exit 1; fi; \
		done; \
		if [ $$run = 0 ]; then echo "rerun: FROM=$(FROM) ist keine Stufe ($(CHAIN) $(TAIL))"; exit 1; fi; \
	fi
	@$(MAKE) --no-print-directory export-cycling

test: ## Run tests (Python and website unit tests)
	uv run pytest
	@if [ -d web/node_modules ]; then npm --prefix web test; fi
