from datetime import datetime
from pathlib import Path
import json


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALERT_FILE = OUTPUT_DIR / "alerts.json"


class AlertManager:

    def __init__(
        self,
        persistence_frames=5,
        disappearance_frames=30
    ):

        self.active_alerts = {}
        self.alert_history = []

        self.persistence_frames = persistence_frames
        self.disappearance_frames = disappearance_frames

        # Track how long an object remains a threat
        self.threat_frames = {}

        # Track how long an object has disappeared
        self.missing_frames = {}

        self.next_alert_id = 1

    # --------------------------------------------------
    # Observe object
    # --------------------------------------------------

    def observe(
        self,
        track_id,
        object_type,
        direction,
        speed,
        risk_level,
        inside_danger_zone
    ):

        # Object is currently visible
        self.missing_frames[track_id] = 0

        # ----------------------------------------------
        # Object outside danger zone
        # ----------------------------------------------

        if not inside_danger_zone:

            self.threat_frames[track_id] = 0

            if track_id in self.active_alerts:

                return self.resolve_alert(track_id)

            return None

        # ----------------------------------------------
        # Object inside danger zone
        # ----------------------------------------------

        if risk_level not in ["HIGH", "CRITICAL"]:

            return None

        self.threat_frames[track_id] = (
            self.threat_frames.get(track_id, 0) + 1
        )

        # ----------------------------------------------
        # Create alert only after persistence
        # ----------------------------------------------

        if (
            track_id not in self.active_alerts
            and
            self.threat_frames[track_id]
            >= self.persistence_frames
        ):

            return self.create_alert(
                track_id,
                object_type,
                direction,
                speed,
                risk_level
            )

        # ----------------------------------------------
        # Escalate existing alert
        # ----------------------------------------------

        if track_id in self.active_alerts:

            return self.update_alert(
                track_id,
                direction,
                speed,
                risk_level
            )

        return None

    # --------------------------------------------------
    # Handle missing tracks
    # --------------------------------------------------

    def handle_missing_tracks(self, visible_track_ids):

        resolved_alerts = []

        for track_id in list(
            self.active_alerts.keys()
        ):

            if track_id not in visible_track_ids:

                self.missing_frames[track_id] = (
                    self.missing_frames.get(track_id, 0) + 1
                )

                if (
                    self.missing_frames[track_id]
                    >= self.disappearance_frames
                ):

                    alert = self.resolve_alert(
                        track_id
                    )

                    if alert:
                        resolved_alerts.append(
                            alert
                        )

        return resolved_alerts

    # --------------------------------------------------
    # Create alert
    # --------------------------------------------------

    def create_alert(
        self,
        track_id,
        object_type,
        direction,
        speed,
        risk_level
    ):

        if track_id in self.active_alerts:
            return None

        alert = {

            "alert_id": self.next_alert_id,

            "track_id": track_id,

            "object_type": object_type,

            "direction": direction,

            "speed_pixels_per_second": round(
                speed,
                2
            ),

            "risk_level": risk_level,

            "location": "Railway Danger Zone",

            "status": "ACTIVE",

            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            )
        }

        self.next_alert_id += 1

        self.active_alerts[track_id] = alert

        self.alert_history.append(
            alert
        )

        self.save_alerts()

        return alert

    # --------------------------------------------------
    # Update alert
    # --------------------------------------------------

    def update_alert(
        self,
        track_id,
        direction,
        speed,
        risk_level
    ):

        if track_id not in self.active_alerts:
            return None

        alert = self.active_alerts[
            track_id
        ]

        old_risk = alert[
            "risk_level"
        ]

        alert["direction"] = direction

        alert[
            "speed_pixels_per_second"
        ] = round(speed, 2)

        # HIGH → CRITICAL escalation
        if (
            old_risk == "HIGH"
            and
            risk_level == "CRITICAL"
        ):

            alert["risk_level"] = "CRITICAL"

            alert["escalated_at"] = (
                datetime.now().isoformat(
                    timespec="seconds"
                )
            )

            self.save_alerts()

            return alert

        return None

    # --------------------------------------------------
    # Resolve alert
    # --------------------------------------------------

    def resolve_alert(self, track_id):

        if track_id not in self.active_alerts:
            return None

        alert = self.active_alerts.pop(
            track_id
        )

        alert["status"] = "RESOLVED"

        alert["resolved_at"] = (
            datetime.now().isoformat(
                timespec="seconds"
            )
        )

        self.save_alerts()

        return alert

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    def save_alerts(self):

        data = {

            "active_alerts":
                list(
                    self.active_alerts.values()
                ),

            "alert_history":
                self.alert_history
        }

        with open(
            ALERT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    # --------------------------------------------------
    # Get active alerts
    # --------------------------------------------------

    def get_active_alerts(self):

        return list(
            self.active_alerts.values()
        )

    # --------------------------------------------------
    # Get history
    # --------------------------------------------------

    def get_alert_history(self):

        return self.alert_history