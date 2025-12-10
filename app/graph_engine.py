import asyncio
import uuid
import time
from typing import Dict, Callable, Any, List, Optional
from pydantic import BaseModel

MAX_LOOP_ITERS = 1000

class Graph(BaseModel):
    nodes: Dict[str, Callable]
    edges: Dict[str, List[str]]

class RunResult:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.state = {}
        self.log = []
        self.current_node = None
        self.finished = False
        self.started_at = time.time()
        self.ended_at = None

    def add_log(self, entry):
        ts = time.time()
        rec = {"ts": ts, "entry": entry}
        self.log.append(rec)
        return rec

class Engine:
    def __init__(self):
        self.graphs: Dict[str, Graph] = {}
        self.runs: Dict[str, RunResult] = {}
        # per-run asyncio.Queue for streaming logs
        self.log_queues: Dict[str, asyncio.Queue] = {}

    def create_graph(self, nodes: Dict[str, Callable], edges: Dict[str, List[str]]) -> str:
        graph_id = str(uuid.uuid4())
        self.graphs[graph_id] = Graph(nodes=nodes, edges=edges)
        return graph_id

    async def run_graph(self, graph_id: str, initial_state: Dict[str, Any], run_id: Optional[str]=None, log_queue: Optional[asyncio.Queue]=None) -> RunResult:
        if graph_id not in self.graphs:
            raise ValueError("graph not found")
        if run_id is None:
            run_id = str(uuid.uuid4())
        run = RunResult(run_id)
        run.state = dict(initial_state or {})
        self.runs[run_id] = run
        if log_queue is None:
            # create queue for this run if not provided
            log_queue = asyncio.Queue()
        self.log_queues[run_id] = log_queue

        graph = self.graphs[graph_id]
        # choose start node
        start_node = "start" if "start" in graph.nodes else list(graph.nodes.keys())[0]
        current = start_node
        iters = 0

        while current:
            run.current_node = current
            rec = run.add_log(f"running node {current}")
            # put to queue without blocking
            try:
                log_queue.put_nowait(rec)
            except Exception:
                pass
            node_fn = graph.nodes[current]
            # execute node (sync or async)
            try:
                if asyncio.iscoroutinefunction(node_fn):
                    out = await node_fn(run.state, graph)
                else:
                    out = node_fn(run.state, graph)
            except Exception as e:
                rec = run.add_log({"node": current, "error": str(e)})
                try: log_queue.put_nowait(rec)
                except: pass
                break

            # normalize output
            next_node = None
            if out is None:
                out_state = {}
            elif isinstance(out, dict):
                out_state = out.get("state", {k:v for k,v in out.items() if k != "next"})
                next_node = out.get("next")
            else:
                out_state = {}
            # merge state
            run.state.update(out_state)

            # if node didn't set next, follow edges
            if not next_node:
                next_list = graph.edges.get(current, [])
                next_node = next_list[0] if next_list else None

            rec = run.add_log({"node": current, "state_snapshot": dict(run.state), "next": next_node})
            try: log_queue.put_nowait(rec)
            except: pass

            iters += 1
            if iters > MAX_LOOP_ITERS:
                rec = run.add_log("max iterations reached, stopping")
                try: log_queue.put_nowait(rec)
                except: pass
                break

            current = next_node

        run.finished = True
        run.ended_at = time.time()
        # final log
        rec = run.add_log("run finished")
        try: log_queue.put_nowait(rec)
        except: pass
        return run

    def get_run(self, run_id: str):
        return self.runs.get(run_id)

    def get_log_queue(self, run_id: str) -> Optional[asyncio.Queue]:
        return self.log_queues.get(run_id)
