from app.services.reporting import get_severity


def aggregate_events(seconds_by_type):
    """Merge consecutive occupied seconds by class (not person tracking)."""
    events = []
    for name, seconds in seconds_by_type.items():
        ordered = sorted(seconds)
        if not ordered:
            continue
        start = previous = ordered[0]
        for current in ordered[1:] + [None]:
            if current is not None and current == previous + 1:
                previous = current
                continue
            events.append({
                "type": name,
                "severity": get_severity(name),
                "start_time": f"{start // 60:02d}:{start % 60:02d}",
                "end_time": f"{previous // 60:02d}:{previous % 60:02d}",
            })
            start = previous = current
    return events
