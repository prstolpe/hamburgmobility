"""Interpreter for the cascade `classification` in config/rules.yaml (guide 3.4, prompts/08_classify.md).

Order = priority: the first top-level rule whose condition is surely true decides. A rule whose `then`
names a group (GOW) continues with the rules `applies_to: <group>`: all trigger rules are checked
(for the trace), the first one that passes wins, the rule `no C-…-* passed` is the fallback.
Missing values and confidence follow classification_policy (C-MISS-01, C-CONF-01).
"""

import re
from dataclasses import dataclass
from typing import Any

from config.schema.rules_model import CATEGORY_GROUPS, RuleSet
from pipeline.lib import expr
from pipeline.lib.expr import HIGH, LOW, Context, Result

_NONE_PASSED = re.compile(r"^no\s+(C-[A-Z0-9]+-)\*\s+passed$")
_TERNARY = re.compile(r"^(\w+)\s+if\s+(.+?)\s+else\s+(\w+)$")


@dataclass
class CompiledRule:
    id: str
    kind: str              # default | none_passed | condition
    condition: Any         # AST (condition) or rule-id prefix (none_passed)
    then_kind: str         # category | group | ternary
    then: Any              # category, group or (category_true, AST, category_false)
    applies_to: str | None


@dataclass
class Policy:
    defaults: dict[str, Any]
    fallback: dict[str, Any]       # feature -> AST of `when` or None (always)
    near_threshold: float


def _compile_then(text: str, groups: set[str]) -> tuple[str, Any]:
    text = re.sub(r"\([^)]*\)", " ", text).strip()  # text in parentheses is a comment
    m = _TERNARY.match(text)
    if m:
        return "ternary", (m.group(1), expr.parse(m.group(2)), m.group(3))
    return ("group" if text in groups else "category"), text


def compile_rules(rules: RuleSet) -> tuple[list[CompiledRule], Policy]:
    """Parse all conditions once; raises expr.ExprError for an unreadable condition."""
    compiled = []
    for r in rules.classification:
        cond_text = r.if_.strip()
        m = _NONE_PASSED.match(cond_text)
        if cond_text == "default":
            kind, cond = "default", None
        elif m:
            kind, cond = "none_passed", m.group(1)
        else:
            kind, cond = "condition", expr.parse(cond_text)
        then_kind, then = _compile_then(r.then, set(CATEGORY_GROUPS))
        compiled.append(CompiledRule(r.id, kind, cond, then_kind, then, r.applies_to))

    defaults, fallback, near = {}, {}, None
    for p in rules.classification_policy:
        defaults.update({k: d.value for k, d in p.defaults.items()})
        fallback.update({k: (expr.parse(f.when) if f.when else None) for k, f in p.fallback_inputs.items()})
        if "near_threshold" in p.thresholds:
            near = p.thresholds["near_threshold"].value
    return compiled, Policy(defaults, fallback, near)


def _ref_resolver(rules: RuleSet):
    thresholds = {n: t.value for r in rules.classification for n, t in r.thresholds.items()}

    def resolve(ref: str) -> float:
        section, name = ref.split(".", 1)
        if section == "thresholds":
            return thresholds[name]
        width = rules.required_width[name]
        if width.value is None:
            raise expr.ExprError(f"{ref} is a range; the cascade needs a single value")
        return width.value
    return resolve


_CACHE: dict[int, tuple] = {}


def clear_cache() -> None:
    """Forget compiled rule sets (many short-lived variants in the sensitivity analysis)."""
    _CACHE.clear()


def classification_inputs(rules: RuleSet) -> list[str]:
    """Columns the cascade and the confidence policy read."""
    from pipeline.lib.rules import referenced_features

    cols = set(referenced_features(rules))
    for p in rules.classification_policy:
        cols |= set(p.defaults) | set(p.fallback_inputs)
        cols |= {f for fi in p.fallback_inputs.values() if fi.when for f in expr.features_in(expr.parse(fi.when))}
    return sorted(cols)


def _compiled(rules: RuleSet):
    cached = _CACHE.get(id(rules))
    if cached is None or cached[0] is not rules:
        cached = _CACHE[id(rules)] = (rules, compile_rules(rules), _ref_resolver(rules))
    return cached[1], cached[2]


def _evaluate(node, ctx: Context) -> Result:
    """Evaluate a condition; a known value counts by its truth (a bare feature may be 0/1)."""
    r = expr.evaluate(node, ctx)
    return r if r.value is None else Result(bool(r.value), r.confidence, r.reasons)


def _prepare(features: dict, policy: Policy, resolve) -> tuple[dict, set[str], list[str]]:
    """Apply C-MISS-01 defaults and find the fallback inputs (C-CONF-01)."""
    values = {k: expr.clean_value(v) for k, v in features.items()}
    defaulted = []
    for name, default in policy.defaults.items():
        if values.get(name) is None:
            values[name] = default
            defaulted.append(name)
    fallback = set(defaulted)
    for name, when in policy.fallback.items():
        if when is None:
            fallback.add(name)
            continue
        r = expr.evaluate(when, Context(values, resolve, policy.near_threshold))
        if r.value is None or bool(r.value):
            fallback.add(name)
    return values, fallback, defaulted


def _step(rule_id: str, result: Result, ctx: Context, part: str | None = None) -> dict:
    step = {"id": rule_id, "passed": result.value is True, "result": result.value,
            "inputs": dict(ctx.used), "confidence": expr.label(result.confidence)}
    if part:
        step["part"] = part
    if result.reasons:
        step["reasons"] = result.reasons
    ctx.used.clear()
    return step


def classify_segment(features: dict, rules: RuleSet) -> dict:
    """Target category for one segment.

    Returns cat_proposed, confidence (hoch|mittel|niedrig), confidence_reasons, defaults_used and
    rule_trace (list of {id, passed, result, inputs, confidence, reasons?}).
    """
    (compiled, policy), resolve = _compiled(rules)
    values, fallback, defaulted = _prepare(features, policy, resolve)
    ctx = Context(values, resolve, policy.near_threshold, fallback)
    trace: list[dict] = []
    path: list[Result] = []  # rule outcomes on the decision path

    def finish(category: str) -> dict:
        conf = min((r.confidence for r in path), default=HIGH)
        reasons = list(dict.fromkeys(x for r in path for x in r.reasons))
        return {"cat_proposed": category, "confidence": expr.label(conf), "confidence_reasons": reasons,
                "defaults_used": defaulted, "rule_trace": trace}

    for rule in compiled:
        if rule.applies_to is not None:
            continue  # evaluated inside its group
        if rule.kind == "default":
            result = Result(True)
        else:
            result = _evaluate(rule.condition, ctx)
        trace.append(_step(rule.id, result, ctx))
        path.append(result)
        if result.value is not True:
            continue

        if rule.then_kind == "category":
            return finish(rule.then)
        if rule.then_kind == "ternary":
            cat_true, cond, cat_false = rule.then
            r = _evaluate(cond, ctx)
            trace.append(_step(rule.id, r, ctx, part="then"))
            if r.value is None:  # C-MISS-01: not surely true -> else branch, confidence low
                r = Result(False, LOW, r.reasons)
            path.append(r)
            return finish(cat_true if r.value else cat_false)
        return finish(_classify_group(rule.then, compiled, ctx, trace, path))

    raise expr.ExprError("cascade ended without a decision (missing default rule)")


def _classify_group(group: str, compiled: list[CompiledRule], ctx: Context, trace: list, path: list) -> str:
    members = [r for r in compiled if r.applies_to == group]
    triggers = [r for r in members if r.kind == "condition"]
    results = {}
    for rule in triggers:
        results[rule.id] = _evaluate(rule.condition, ctx)
        trace.append(_step(rule.id, results[rule.id], ctx))
    # The decision between the trigger rules and the fallback is an "or" over the triggers.
    path.append(expr.combine("or", list(results.values())) if results else Result(False))
    for rule in triggers:
        if results[rule.id].value is True:
            return rule.then
    for rule in members:
        if rule.kind == "none_passed":
            prefix = rule.condition
            any_passed = any(results[r.id].value is True for r in triggers if r.id.startswith(prefix))
            trace.append({"id": rule.id, "passed": not any_passed, "result": not any_passed,
                          "inputs": {"checked": [r.id for r in triggers if r.id.startswith(prefix)]},
                          "confidence": expr.label(path[-1].confidence)})
            if not any_passed:
                return rule.then
    raise expr.ExprError(f"group {group}: no rule decided")
