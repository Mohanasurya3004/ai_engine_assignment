# Sample code-review workflow using tools
from app.tools import extract_functions, check_complexity, detect_smells, suggest_improvements

async def node_extract(state, graph_or_tools):
    code = state.get('code', '')
    out = extract_functions(code)
    return {'state': {'functions': out['functions']}, 'next': 'check_complexity'}

async def node_check_complexity(state, graph_or_tools):
    funcs = state.get('functions', [])
    out = check_complexity(funcs)
    return {'state': {'complexities': out['complexities']}, 'next': 'detect_issues'}

async def node_detect_issues(state, graph_or_tools):
    code = state.get('code', '')
    out = detect_smells(code)
    state_update = {'issues': out['issues']}
    # compute a simple quality score
    score = 10 - (len(out['issues']) * 2) - sum(c.get('complexity',0)-1 for c in state.get('complexities', []))
    state_update['quality_score'] = max(0, score)
    # branch to suggestions if low score
    threshold = state.get('threshold', 7)
    if state_update['quality_score'] < threshold:
        return {'state': state_update, 'next': 'suggest_improvements'}
    else:
        return {'state': state_update, 'next': None}

async def node_suggest_improvements(state, graph_or_tools):
    out = suggest_improvements(state)
    # pretend we 'apply' suggestions by increasing quality score slightly
    new_score = state.get('quality_score', 0) + 1
    state_update = {'suggestions': out['suggestions'], 'quality_score': new_score}
    # loop back to detect_issues to re-evaluate (in real system you'd re-run analysis after fixes)
    return {'state': state_update, 'next': 'detect_issues'}

nodes_map = {
    'extract': node_extract,
    'check_complexity': node_check_complexity,
    'detect_issues': node_detect_issues,
    'suggest_improvements': node_suggest_improvements
}

edges_map = {
    'extract': ['check_complexity'],
    'check_complexity': ['detect_issues'],
    'detect_issues': ['suggest_improvements'],
    'suggest_improvements': ['detect_issues']
}
