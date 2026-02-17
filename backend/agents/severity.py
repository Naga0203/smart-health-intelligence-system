"""
Severity Scoring Agent

Calculates severity score based on:
- Symptoms
- Model probability
- Temperature
- Comorbidities
"""

from typing import Dict, List


class SeverityScoringAgent:

    CRITICAL_SYMPTOMS = [
        "chest pain",
        "shortness of breath",
        "loss of consciousness",
        "severe headache"
    ]

    def calculate(
        self,
        symptoms: List[str],
        probability: float,
        profile: Dict
    ) -> Dict:

        score = len(symptoms)

        text = " ".join(symptoms).lower()

        for red_flag in self.CRITICAL_SYMPTOMS:
            if red_flag in text:
                score += 4

        temp = profile.get("temperature")
        if isinstance(temp, (int, float)):
            if temp >= 40:
                score += 5
            elif temp >= 39:
                score += 3

        score += len(profile.get("past_health_conditions", [])) * 2

        if probability >= 0.75:
            score += 3

        if score >= 12:
            level = "CRITICAL"
        elif score >= 8:
            level = "HIGH"
        elif score >= 4:
            level = "MODERATE"
        else:
            level = "LOW"

        return {
            "severity_score": score,
            "severity_level": level
        }
