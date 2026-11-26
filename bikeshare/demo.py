"""Run the integration contract against a three-station example."""

import json
from datetime import date
from pathlib import Path

from bikeshare.pipeline import PlanningInput, run_pipeline


def fixture_planner(request: PlanningInput) -> dict[str, int]:
    """Stand-in for the resource planning module in the demo only."""
    return {"A": request.bike_budget, "B": 0, "C": 0}


def main() -> None:
    path = Path(__file__).resolve().parent.parent / "fixtures" / "three_stations.json"
    example = json.loads(path.read_text(encoding="utf-8"))
    request = PlanningInput(
        service_date=date.fromisoformat(example["service_date"]),
        bike_budget=example["bike_budget"],
        risks=example["risks"],
        limits=example["limits"],
    )
    allocation = run_pipeline(request, fixture_planner)
    if allocation != example["expected_allocation"]:
        raise ValueError("The demo allocation differs from the fixture's expected result.")
    print(json.dumps({
        "mode": "mock integration demo",
        "service_date": request.service_date.isoformat(),
        "bike_budget": request.bike_budget,
        "allocation": allocation,
    }, indent=2))


if __name__ == "__main__":
    main()
