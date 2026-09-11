import json
import csv
import os


def collect_violations(result):
    violations = []
    for box in result.boxes:
        name = result.names[int(box.cls[0])]
        if is_violation(name):
            violations.append({"type": name, "confidence": round(float(box.conf[0]), 4),
                               "severity": get_severity(name), "timestamp": None})
    return violations


def write_reports(report, destination):
    (destination / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    fields = (["type", "severity", "start_time", "end_time"] if report["media_type"] == "video"
              else ["type", "confidence", "severity", "timestamp"])
    with (destination / "report.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(report["violations"])


VIOLATION_SEVERITY = {
    "NO-Hardhat": "high",
    "NO-Safety Vest": "medium",
    "NO-Mask": "low"
}


def is_violation(class_name):
    return class_name in VIOLATION_SEVERITY


def get_severity(class_name):
    return VIOLATION_SEVERITY.get(
        class_name,
        "unknown"
    )


def save_json_report(data, filename):

    os.makedirs(
        "outputs/reports/json",
        exist_ok=True
    )

    path = os.path.join(
        "outputs/reports/json",
        filename
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )

    return path


def save_csv_report(rows, filename):

    os.makedirs(
        "outputs/reports/csv",
        exist_ok=True
    )

    path = os.path.join(
        "outputs/reports/csv",
        filename
    )

    if not rows:

        with open(
            path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "type",
                "confidence",
                "severity",
                "timestamp"
            ])

        return path


    fieldnames = rows[0].keys()


    with open(
        path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(rows)


    return path
