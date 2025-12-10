import asyncio
from app.graph_engine import Engine
from app.workflows import nodes_map, edges_map

def test_run_graph_sync():
    engine = Engine()
    gid = engine.create_graph(nodes_map, edges_map)
    # run the graph synchronously in event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    run = loop.run_until_complete(engine.run_graph(gid, {'code': 'def foo():\n    print("hi")\n', 'threshold': 8}))
    assert run.finished
    assert 'quality_score' in run.state

def test_loop_safety():
    # small artificial graph that loops forever unless capped
    async def n1(state, g): return {'state': {'x': state.get('x',0)+1}, 'next': 'n1'}
    nodes = {'n1': n1}
    edges = {'n1': ['n1']}
    engine = Engine()
    gid = engine.create_graph(nodes, edges)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    run = loop.run_until_complete(engine.run_graph(gid, {}))
    assert run.finished
    # should have a finite number of log entries
    assert len(run.log) < 20000
