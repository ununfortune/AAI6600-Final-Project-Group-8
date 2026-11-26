"""Validate the forecast, station rules, and planner handoff."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import TypedDict


class StationLimit(TypedDict):
    max_delivery: int
    reason: str


@dataclass(frozen=True)
class PlanningInput:
    service_date: date
    bike_budget: int
    risks: dict[str, list[float]]
    limits: dict[str, StationLimit]


def run_pipeline(
    request: PlanningInput,
    planner: Callable[[PlanningInput], dict[str, int]],
) -> dict[str, int]:
    """Return a validated allocation for one service date."""
    if type(request.bike_budget) is not int or request.bike_budget < 0:
        raise ValueError("Bike budget must be a nonnegative integer.")
    if not request.limits or request.risks.keys() != request.limits.keys():
        raise ValueError("Forecast and station rules must cover the same nonempty set of stations.")

    for station, limit in request.limits.items():
        maximum = limit["max_delivery"]
        if type(maximum) is not int or maximum < 0:
            raise ValueError(f"{station}: expected a nonnegative integer delivery limit.")

        risks = request.risks[station]
        if len(risks) <= maximum:
            raise ValueError(f"{station}: forecast is missing one or more allowed delivery quantities.")
        if any(type(risk) not in (int, float) or not isfinite(risk) or not 0 <= risk <= 1 for risk in risks):
            raise ValueError(f"{station}: shortage probabilities must be between 0 and 1.")

    allocation = planner(request)
    if allocation.keys() != request.limits.keys():
        raise ValueError("Planner must return one quantity per station.")
    for station, quantity in allocation.items():
        if type(quantity) is not int or not 0 <= quantity <= request.limits[station]["max_delivery"]:
            raise ValueError(f"{station}: planned quantity violates the station limit.")
    if sum(allocation.values()) > request.bike_budget:
        raise ValueError("Planned deliveries exceed the bike budget.")
    return allocation
