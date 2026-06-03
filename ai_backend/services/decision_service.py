class DecisionService:
    """Rule-based Gemma4 decision adapter for the dashboard demo."""

    def analyze(self, state: dict) -> dict:
        vision = state.get("vision", {})
        speech = state.get("speech", {})
        context = state.get("context", {})

        fall_detected = bool(vision.get("fall_detected"))
        confidence = max(0.0, min(1.0, float(vision.get("confidence") or 0)))
        confidence_pct = round(confidence * 100)
        detections = vision.get("detections") or []
        posture_fall = any(item.get("posture_fall") for item in detections if isinstance(item, dict))
        transcript = str(speech.get("transcript") or "")
        intent = str(speech.get("intent") or "none")
        no_response_seconds = int(context.get("no_response_seconds") or 0)

        if intent == "help":
            score = 96 if fall_detected else 82
            return {
                "risk_level": "high",
                "risk_score": score,
                "emergency_alert": fall_detected,
                "action": "Escalate rescue response",
                "reason": (
                    "The user verbally asked for help"
                    + (f" while vision confidence is {confidence_pct}%." if fall_detected else ".")
                ),
                "reply_analysis": f"User replied: {transcript}",
                "model": "gemma4-demo-rule-engine",
            }

        if intent == "safe" and not fall_detected:
            score = max(5, min(18, round(6 + confidence * 8)))
            return {
                "risk_level": "low",
                "risk_score": score,
                "emergency_alert": False,
                "action": "User confirmed safe",
                "reason": "The user gave a safe voice reply and vision does not detect a fall.",
                "reply_analysis": f"User replied: {transcript}",
                "model": "gemma4-demo-rule-engine",
            }

        if fall_detected and confidence >= 0.85 and no_response_seconds >= 60:
            return {
                "risk_level": "high",
                "risk_score": 100,
                "emergency_alert": True,
                "action": "Trigger emergency alert",
                "reason": (
                    f"Fall risk is very high ({confidence_pct}% visual confidence) "
                    f"and there has been no response for {no_response_seconds} seconds."
                ),
                "reply_analysis": "No response after repeated voice checks.",
                "model": "gemma4-demo-rule-engine",
            }

        if fall_detected and intent == "safe":
            score = max(18, min(38, round(18 + confidence * 18)))
            return {
                "risk_level": "low",
                "risk_score": score,
                "emergency_alert": False,
                "action": "Record safe reply and keep monitoring",
                "reason": (
                    f"The user replied that they are safe. Visual confidence is {confidence_pct}%, "
                    "so monitoring continues without emergency escalation."
                ),
                "reply_analysis": f"User replied: {transcript}",
                "model": "gemma4-demo-rule-engine",
            }

        if fall_detected and no_response_seconds >= 30:
            score = max(82, min(96, round(70 + confidence * 20 + no_response_seconds / 6)))
            return {
                "risk_level": "high",
                "risk_score": score,
                "emergency_alert": False,
                "action": "Escalate voice prompt and prepare alert",
                "reason": (
                    f"Fall risk remains active ({confidence_pct}% visual confidence) "
                    f"and no response has been received for {no_response_seconds} seconds."
                ),
                "reply_analysis": "No response yet.",
                "model": "gemma4-demo-rule-engine",
            }

        if fall_detected:
            if posture_fall:
                score = max(36, min(58, round(28 + confidence * 42)))
                reason = (
                    f"Posture looks like a possible fall ({confidence_pct}% posture confidence), "
                    "but it needs voice confirmation before escalation."
                )
            else:
                score = max(52, min(82, round(42 + confidence * 38)))
                reason = (
                    f"Vision detected a suspected fall with {confidence_pct}% confidence. "
                    "Ask the user to confirm whether they are safe."
                )
            return {
                "risk_level": "medium",
                "risk_score": score,
                "emergency_alert": False,
                "action": "Start voice check",
                "reason": reason,
                "reply_analysis": "Voice check required.",
                "model": "gemma4-demo-rule-engine",
            }

        score = max(6, min(28, round(8 + confidence * 14)))
        return {
            "risk_level": "low",
            "risk_score": score,
            "emergency_alert": False,
            "action": "Continue monitoring",
            "reason": (
                f"No fall is currently detected. Person confidence is {confidence_pct}%."
                if confidence
                else "No fall is currently detected."
            ),
            "reply_analysis": "No active voice check.",
            "model": "gemma4-demo-rule-engine",
        }
