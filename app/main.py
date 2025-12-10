from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from app.graph_engine import Engine
from app.models import RunGraphRequest
import asyncio

app = FastAPI(title="Agent Workflow Engine - Full")
engine = Engine()

@app.on_event("startup")
async def startup_create_sample_graph():
    # create a sample graph (code-review workflow)
    from app.workflows import nodes_map, edges_map
    graph_id = engine.create_graph(nodes_map, edges_map)
    engine.sample_graph_id = graph_id
    print(f"Sample graph created with graph_id: {graph_id}")

@app.get("/")
async def root():
    return {"message": "Agent Workflow Engine - running", "sample_graph_id": getattr(engine, 'sample_graph_id', None)}

@app.post("/graph/run")
async def run_graph(payload: RunGraphRequest, background_tasks: BackgroundTasks):
    graph_id = payload.graph_id
    if graph_id not in engine.graphs:
        raise HTTPException(status_code=404, detail="graph not found")
    # if user wants background execution they can still call; we'll run in background and return run_id immediately
    run_id = str(asyncio.uuid4()) if hasattr(asyncio, 'uuid4') else __import__('uuid').uuid4().hex
    # create a dedicated queue for logs
    log_queue = asyncio.Queue()
    # schedule background task
    background_tasks.add_task(engine.run_graph, graph_id, payload.initial_state, run_id, log_queue)
    # return run id for polling or websocket streaming
    return {"run_id": run_id}

@app.get("/graph/state/{run_id}")
async def get_state(run_id: str):
    run = engine.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    return {"run_id": run_id, "finished": run.finished, "state": run.state, "log": run.log}

@app.websocket("/ws/run/{run_id}")
async def websocket_run(ws: WebSocket, run_id: str):
    await ws.accept()
    # subscribe to engine log queue for this run
    q = engine.get_log_queue(run_id)
    if q is None:
        # if no queue yet (run not started), wait a bit for it to be created
        for _ in range(10):
            await asyncio.sleep(0.1)
            q = engine.get_log_queue(run_id)
            if q is not None:
                break
    if q is None:
        await ws.send_json({"error": "no such run or no logs available"})
        await ws.close()
        return
    try:
        while True:
            # wait for next log entry; timeout if run finished and queue empty
            try:
                entry = await asyncio.wait_for(q.get(), timeout=30.0)
            except asyncio.TimeoutError:
                # check if run finished and queue empty
                run = engine.get_run(run_id)
                if run and run.finished:
                    break
                else:
                    continue
            # send entry to client
            try:
                await ws.send_json(entry)
            except Exception:
                break
    except WebSocketDisconnect:
        pass
    finally:
        await ws.close()
