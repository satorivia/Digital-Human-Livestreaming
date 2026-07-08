from dataclasses import dataclass, field
from typing import Protocol

from app.services.entities import AnswerCandidate, CandidateStatus, Product, Risk


@dataclass(slots=True)
class RuleHit:
    rule_name: str
    risk: Risk
    reason: str


@dataclass(slots=True)
class ComplianceDecision:
    risk: Risk
    need_human_review: bool
    blocked: bool
    hits: list[RuleHit] = field(default_factory=list)


class ComplianceChecker(Protocol):
    def check(self, text: str, product: Product | None = None) -> list[RuleHit]:
        """Return rule hits for text."""


class SensitiveWordChecker:
    blocked_terms = ("私下转账", "治好湿疹")
    medium_terms = ("敏感肌",)

    def check(self, text: str, product: Product | None = None) -> list[RuleHit]:
        hits: list[RuleHit] = []
        for term in self.blocked_terms:
            if term in text:
                hits.append(RuleHit("sensitive_word", Risk.BLOCKED, f"命中禁用词：{term}"))
        for term in self.medium_terms:
            if term in text:
                hits.append(RuleHit("sensitive_word", Risk.MEDIUM, f"命中需人工确认词：{term}"))
        return hits


class AbsoluteClaimChecker:
    high_terms = ("100%", "保证不过敏", "绝对", "第一", "最有效")

    def check(self, text: str, product: Product | None = None) -> list[RuleHit]:
        return [
            RuleHit("absolute_claim", Risk.HIGH, f"命中绝对化/保证性表达：{term}")
            for term in self.high_terms
            if term in text
        ]


class ProductForbiddenClaimChecker:
    def check(self, text: str, product: Product | None = None) -> list[RuleHit]:
        if product is None:
            return []
        return [
            RuleHit("product_forbidden_claim", Risk.BLOCKED, f"命中商品禁用表达：{claim}")
            for claim in product.forbidden
            if claim and claim in text
        ]


class PriceConsistencyChecker:
    def check(self, text: str, product: Product | None = None) -> list[RuleHit]:
        if product is None or not product.skus:
            return []
        if "元" not in text:
            return []
        allowed_prices = {f"{sku.price_cents / 100:.2f}元" for sku in product.skus}
        allowed_prices.update(f"{sku.price_cents // 100}元" for sku in product.skus)
        if any(price in text for price in allowed_prices) or "以页面为准" in text:
            return []
        return [RuleHit("price_consistency", Risk.HIGH, "回答中出现未登记价格")]


class ComplianceService:
    risk_order = {Risk.LOW: 0, Risk.MEDIUM: 1, Risk.HIGH: 2, Risk.BLOCKED: 3}

    def __init__(self, checkers: list[ComplianceChecker] | None = None) -> None:
        self.checkers = checkers or [
            SensitiveWordChecker(),
            AbsoluteClaimChecker(),
            ProductForbiddenClaimChecker(),
            PriceConsistencyChecker(),
        ]

    def check(self, candidate: AnswerCandidate, product: Product | None = None) -> AnswerCandidate:
        decision = self.review_text(candidate.text, product)
        candidate.risk = decision.risk
        candidate.need_human_review = decision.need_human_review
        candidate.matched_rules = [hit.reason for hit in decision.hits]
        candidate.status = (
            CandidateStatus.BLOCKED if decision.blocked else CandidateStatus.NEEDS_HUMAN_REVIEW
        )
        return candidate

    def review_text(self, text: str, product: Product | None = None) -> ComplianceDecision:
        hits = [hit for checker in self.checkers for hit in checker.check(text, product)]
        risk = max((hit.risk for hit in hits), key=lambda value: self.risk_order[value], default=Risk.LOW)
        return ComplianceDecision(
            risk=risk,
            need_human_review=risk in {Risk.MEDIUM, Risk.HIGH, Risk.BLOCKED},
            blocked=risk == Risk.BLOCKED,
            hits=hits,
        )
