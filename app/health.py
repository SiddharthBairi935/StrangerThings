from datetime import date, datetime
from typing import Any


def summarize_health_entries(
    entries: list[dict[str, Any]], days: int, today: date | None = None
) -> dict[str, object]:
    """Summarize only logged numeric nutrition, workouts, weights and measurements."""
    safe_days = max(1, min(int(days), 365))
    end = today or date.today()
    start = date.fromordinal(end.toordinal() - safe_days + 1)
    daily: dict[str, dict[str, float | int]] = {}
    weight_series: list[dict[str, object]] = []
    measurements: list[dict[str, object]] = []
    workout_sessions = 0

    for entry in entries:
        logged = str(entry.get("logged_at") or "")
        try:
            logged_day = datetime.fromisoformat(logged.replace("Z", "+00:00")).date()
        except ValueError:
            continue
        if logged_day < start or logged_day > end:
            continue
        day_key = logged_day.isoformat()
        bucket = daily.setdefault(day_key, {
            "food_entries": 0, "calories": 0.0, "protein_g": 0.0,
            "carbs_g": 0.0, "fat_g": 0.0, "workouts": 0,
        })
        data = entry.get("data") if isinstance(entry.get("data"), dict) else {}
        kind = entry.get("entry_type")
        if kind == "food":
            bucket["food_entries"] += 1
            nutrition = data.get("nutrition") if isinstance(data.get("nutrition"), dict) else data
            for output, keys in {
                "calories": ("calories", "kcal"),
                "protein_g": ("protein_g", "protein"),
                "carbs_g": ("carbs_g", "carbs"),
                "fat_g": ("fat_g", "fat"),
            }.items():
                for key in keys:
                    value = nutrition.get(key)
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        bucket[output] += float(value)
                        break
        elif kind == "workout":
            bucket["workouts"] += 1
            workout_sessions += 1
        elif kind == "weight":
            value = data.get("kg", data.get("weight_kg"))
            unit = "kg"
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                value = data.get("value", data.get("weight"))
                unit = str(data.get("unit") or "")
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                weight_series.append({"date": day_key, "value": float(value), "unit": unit})
        elif kind == "measurement":
            measurements.append({"date": day_key, **data})

    ordered_days = sorted(daily)
    totals = {
        key: round(sum(float(daily[day][key]) for day in ordered_days), 2)
        for key in ("calories", "protein_g", "carbs_g", "fat_g")
    }
    weight_series.sort(key=lambda item: str(item["date"]))
    return {
        "period_days": safe_days,
        "from": start.isoformat(),
        "to": end.isoformat(),
        "totals": totals,
        "daily": [{"date": day, **daily[day]} for day in ordered_days],
        "weight_series": weight_series,
        "latest_weight": weight_series[-1] if weight_series else None,
        "measurements": measurements[:50],
        "workout_sessions": workout_sessions,
        "note": "Nutrition totals include only numeric values stored in food logs. Values marked AI estimate are approximate, not measurements; missing values are not estimated or treated as zero intake.",
    }
