from typing import Dict, Any

class RequestRouter:
    def handle(self, req: Dict[str, Any]) -> Dict[str, Any]:
        msg_type = req.get("type")
        payload = req.get("payload", {})

        if msg_type == "PING":
            return {"status": "ok", "data": {"pong": True, "echo": payload}}

        return {"status": "error", "error": f"Unknown type: {msg_type}"}
