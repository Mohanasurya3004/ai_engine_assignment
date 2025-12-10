from pydantic import BaseModel
from typing import Dict, Any, Optional

class RunGraphRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any] = {}
