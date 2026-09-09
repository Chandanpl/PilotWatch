from datetime import datetime
from pathlib import Path
import json


BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALERT_FILE = OUTPUT_DIR / "alerts.json"


class AlertManager:

    def __init__(self):
        self.active_alerts = {}
        self.alert_history = []

    # ---------------------------------------------------------
    # CREATE NEW ALERT
    # ---------------------------------------------------------
    def create_alert(
        self,
        track_id,
        object_type,
        direction,
        speed,
        risk_level
    ):

        # Do not create duplicate alerts
        if track_id in self.active_alerts:
            return None

        alert = {
            "alert_id": len(self.alert_history) + 1,
            "track_id": track_id,
            "object_type": object_type,
            "direction": direction,
            "speed_pixels_per_second": round(speed, 2),
            "risk_level": risk_level,
            "location": "Railway Danger Zone",
            "status": "ACTIVE",
            "timestamp": datetime.now().isoformat(timespec="seconds")
        }

        self.active_alerts[track_id] = alert
        self.alert_history.append(alert)

        self.save_alerts()

        return alert

    # ---------------------------------------------------------
    # UPDATE EXISTING ALERT
    # ---------------------------------------------------------
    def update_alert(
        self,
        track_id,
        direction,
        speed,
        risk_level
    ):

        if track_id not in self.active_alerts:
            return None

        alert = self.active_alerts[track_id]

        old_risk = alert["risk_level"]

        alert["direction"] = direction
        alert["speed_pixels_per_second"] = round(speed, 2)

        # Allow HIGH → CRITICAL escalation
        if old_risk == "HIGH" and risk_level == "CRITICAL":

            alert["risk_level"] = "CRITICAL"
            alert["escalated_at"] = datetime.now().isoformat(
                timespec="seconds"
            )

            self.save_alerts()

            return alert

        return None

    # ---------------------------------------------------------
    # RESOLVE ALERT
    # ---------------------------------------------------------
    def resolve_alert(self, track_id):

        if track_id not in self.active_alerts:
            return None

        alert = self.active_alerts.pop(track_id)

        alert["status"] = "RESOLVED"
        alert["resolved_at"] = datetime.now().isoformat(
            timespec="seconds"
        )

        self.save_alerts()

        return alert

    # ---------------------------------------------------------
    # SAVE ALERTS
    # ---------------------------------------------------------
    def save_alerts(self):

        data = {
            "active_alerts": list(self.active_alerts.values()),
            "alert_history": self.alert_history
        }

        with open(ALERT_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    # ---------------------------------------------------------
    # GET ACTIVE ALERTS
    # ---------------------------------------------------------
    def get_active_alerts(self):

        return list(self.active_alerts.values())

    # ---------------------------------------------------------
    # GET ALERT HISTORY
    # ---------------------------------------------------------
    def get_alert_history(self):

        return self.alert_history


# -------------------------------------------------------------
# TEST
# -------------------------------------------------------------
if __name__ == "__main__":

    print("Starting PilotWatch Alert Manager...")

    manager = AlertManager()

    # First alert
    alert = manager.create_alert(
        track_id=27,
        object_type="person",
        direction="LEFT",
        speed=18.4,
        risk_level="HIGH"
    )

    if alert:
        print("\nNew alert created:")
        print(json.dumps(alert, indent=4))

    # Duplicate test
    duplicate = manager.create_alert(
        track_id=27,
        object_type="person",
        direction="LEFT",
        speed=20.1,
        risk_level="HIGH"
    )

    if duplicate is None:
        print("\nDuplicate alert blocked successfully!")

    # Escalation test
    escalation = manager.update_alert(
        track_id=27,
        direction="LEFT",
        speed=45.2,
        risk_level="CRITICAL"
    )

    if escalation:
        print("\nAlert escalated:")
        print(json.dumps(escalation, indent=4))

    # Active alerts
    print("\nActive alerts:")
    print(
        json.dumps(
            manager.get_active_alerts(),
            indent=4
        )
    )

    print(f"\nAlert file: {ALERT_FILE}")