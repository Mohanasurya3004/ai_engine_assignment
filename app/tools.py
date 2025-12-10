# Simple tool functions used by sample workflow
from typing import List, Dict

def extract_functions(code: str) -> Dict:
    # naive extractor: split by 'def ' occurrences
    funcs = []
    parts = code.split('\n')
    current = None
    buf = []
    for line in parts:
        if line.strip().startswith('def '):
            if current:
                funcs.append({'name': current, 'body': '\n'.join(buf)})
            # parse function name
            header = line.strip()
            name = header.split('def ')[1].split('(')[0]
            current = name
            buf = [line]
        else:
            if current:
                buf.append(line)
    if current:
        funcs.append({'name': current, 'body': '\n'.join(buf)})
    return {'functions': funcs}

def check_complexity(functions: List[Dict]) -> Dict:
    results = []
    for f in functions:
        lines = f['body'].count('\n') + 1
        # very naive 'complexity' proxy
        complexity = 1 + (lines // 40)
        results.append({'name': f['name'], 'complexity': complexity, 'lines': lines})
    return {'complexities': results}

def detect_smells(code: str) -> Dict:
    issues = []
    if 'TODO' in code:
        issues.append('contains TODO')
    if 'print(' in code:
        issues.append('contains print statements')
    if len(code) > 500:
        issues.append('file is large')
    return {'issues': issues}

def suggest_improvements(state: Dict) -> Dict:
    suggestions = []
    issues = state.get('issues', [])
    complexities = state.get('complexities', [])
    if issues:
        suggestions.append('Address TODOs and remove debug prints.')
    for c in complexities:
        if c.get('complexity', 0) > 2:
            suggestions.append(f"Refactor function {c['name']} (lines={c['lines']}) into smaller parts.")
    if not suggestions:
        suggestions.append('No changes required.')
    return {'suggestions': suggestions}
