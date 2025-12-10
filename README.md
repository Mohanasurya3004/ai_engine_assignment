<h1 align="center">AI Engine Assignment</h1>
<p align="center"><strong>Graph-based workflow engine (FastAPI)</strong></p>

<hr>

<h2>What to Submit</h2>
<ul>
  <li><strong>The FastAPI project</strong> (include the <code>/app</code> folder)</li>
  <li><strong>Code for the graph engine</strong> (<code>app/graph_engine.py</code>)</li>
  <li><strong>Code for example agent workflow</strong> (<code>app/workflows.py</code> + <code>app/tools.py</code>)</li>
  <li><strong>This README</strong> explaining how to run, supported features, and improvements</li>
</ul>

<hr>

<h2>Folder structure (clean, minimal)</h2>
<pre>
ai_engine_assignment/
├─ app/
│  ├─ main.py            # FastAPI entrypoint (endpoints)
│  ├─ graph_engine.py    # Core graph engine (nodes, runner, logs)
│  ├─ workflows.py       # Example workflow nodes & edges
│  ├─ tools.py           # Helper functions used by workflow
│  └─ models.py          # Pydantic request/response models
├─ tests/
│  └─ test_engine.py     # Unit tests (pytest)
├─ requirements.txt
└─ README.md
</pre>

<hr>

<h2>How to run</h2>
<ol>
  <li>Clone the repo and enter the project folder:
    <pre>git clone &lt;repo-url&gt; && cd ai_engine_assignment</pre>
  </li>
  <li>Create and activate a virtual environment:
    <pre>
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
    </pre>
  </li>
  <li>Install dependencies:
    <pre>pip install -r requirements.txt</pre>
  </li>
  <li>Start the FastAPI server:
    <pre>uvicorn app.main:app --reload --port 8000</pre>
  </li>
  <li>Open the root endpoint to get the sample graph id:
    <pre>http://127.0.0.1:8000/</pre>
  </li>
  <li>Start a run (example):
    <pre>
curl -X POST "http://127.0.0.1:8000/graph/run" -H "Content-Type: application/json" -d '{
  "graph_id":"&lt;graph_id&gt;",
  "initial_state":{"code":"def foo():\\n  print(\"hello\")\\n","threshold":7}
}'
    </pre>
  </li>
  <li>Check run state & logs:
    <pre>http://127.0.0.1:8000/graph/state/&lt;run_id&gt;</pre>
  </li>
  <li>Optional: stream live logs via WebSocket:
    <pre>ws://127.0.0.1:8000/ws/run/&lt;run_id&gt;</pre>
  </li>
</ol>

<hr>

<h2>What the workflow engine supports</h2>
<ul>
  <li><strong>Nodes:</strong> functions (sync or async) that read and update a shared state dict.</li>
  <li><strong>Edges:</strong> configurable edges define default control flow between nodes.</li>
  <li><strong>Branching:</strong> nodes can return <code>{"next": "node_name"}</code> to choose the next node dynamically.</li>
  <li><strong>Looping:</strong> nodes/edges can form loops; runner enforces a safe loop iteration cap.</li>
  <li><strong>State propagation:</strong> all nodes read/write a shared state object which is merged after each node.</li>
  <li><strong>Logs:</strong> timestamped execution logs per node; available via API and WebSocket stream.</li>
  <li><strong>Sample workflow:</strong> a Code Review agent that extracts functions, measures complexity, detects smells, and suggests improvements.</li>
</ul>

<hr>

<h2>What I would improve with more time</h2>
<ul>
  <li><strong>Persistence:</strong> store graphs and runs in SQLite so runs survive server restarts.</li>
  <li><strong>Secure dynamic graphs:</strong> safe API to upload workflow specs mapped only to pre-approved node functions.</li>
  <li><strong>Front-end UI:</strong> simple web UI to create graphs, start runs and view logs visually.</li>
  <li><strong>Configurable loop/timeout policies:</strong> per-graph settings for iteration caps and timeouts.</li>
  <li><strong>Tests & CI:</strong> more unit/integration tests and GitHub Actions to run tests on push.</li>
</ul>

<hr>
