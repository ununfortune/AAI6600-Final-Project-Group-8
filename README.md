# Group 8 · Bike-share restocking

Before the 7–10 a.m. rush, decide how many spare bikes to deliver to each station.
The forecast estimates shortage risk, station rules set delivery limits, and the planner allocates the available bikes.

## Run the integration example

From the repository root with Python 3.10 or later:

```sh
python -m bikeshare.demo
```

The example uses three fictional stations and a two-bike budget. It checks that the preset plan delivers two bikes to station A, zero to B, and zero to closed station C. The inputs and expected output are in `fixtures/three_stations.json`.

## Shared inputs and outputs

Use the same string station IDs across all modules. Create one set of inputs per service date in local New Jersey time.

| Owner | Hands off | Format |
|---|---|---|
| Forecast | Shortage probabilities after each delivery quantity | `dict[str, list[float]]`. Index 0 means no delivery, index 1 means one bike, and so on. Each list must cover every allowed quantity for that station. |
| Station rules | Delivery limit and explanation | `dict[str, dict]`. Each station has an integer `max_delivery` and a text `reason`. A closed station has a limit of zero. |
| Planner | Proposed allocation | Accepts a `PlanningInput` with `service_date`, `bike_budget`, `risks`, and `limits`. Returns `dict[str, int]` with a quantity for each station. |
| Evaluation | Compares planner allocations with the baseline | Receive the allocation and its service date. Use the held-out trip replay to count simulated shortages. |

The integration function `bikeshare.pipeline.run_pipeline` accepts the forecast and rule outputs plus a planner function. It validates station IDs, required probabilities, station limits, and the total budget.

## Dataset

Use the July, August, and September 2024 Jersey City and Hoboken trip archives. Use July–August to select 20 stations and fit the model. Use September for the held-out replay. Keep local raw files under `data/raw/`.

From the repository root, download the three archives and extract their CSVs:

```sh
python -m bikeshare.download_data
```

The script verifies each official ZIP against its SHA-256 hash and extracts the matching trip CSV. The three CSVs and their ZIPs are available under `data/raw/`. Rerunning the script reuses verified files. Git ignores that directory.

| Archive | Use |
|---|---|
| [July 2024](https://s3.amazonaws.com/tripdata/JC-202407-citibike-tripdata.csv.zip) | Training |
| [August 2024](https://s3.amazonaws.com/tripdata/JC-202408-citibike-tripdata.csv.zip) | Training |
| [September 2024](https://s3.amazonaws.com/tripdata/JC-202409-citibike-tripdata.csv.zip) | Held-out evaluation |

## Start in parallel

Each module owner can develop against the three-station fixture immediately. Add the real forecast, rule engine, and planner on separate branches. The integration owner can connect each module as it becomes available.

## Pull requests

When opening a pull request for your module, include both of the following in the description:

- One command a teammate can run from the repository root to reproduce your result.
- One example of the output that command produces. Use the three-station fixture when it fits your module.

The integration owner uses these to verify the module's output before connecting it to the pipeline.
