import json
import re
from collections import defaultdict

def detect_json_format_errors(filepath):
    """
    Detects JSON issues including:
    - Syntax errors (invalid JSON)
    - Root not being a dictionary
    - Top-level values not dictionaries
    - Inner keys not numeric strings
    - Inner values not strings
    - Improper use of single quotes around values
    - Commas before closing braces

    Args:
        filepath (str): Path to the JSON file.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        content = ''.join(lines)

    # Fallback to raw line scanning for syntax issues
    single_quote_issues = defaultdict(list)
    comma_brace_issues = defaultdict(list)
    syntax_errors = []

    current_top_key = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Track current top-level block
        if stripped.startswith('"') and stripped.endswith('{') and ':' in stripped:
            current_top_key = stripped.split(':', 1)[0].strip().strip('"')

        if re.search(r':\s*\'(.*?)\'\s*(,|})', line):
            single_quote_issues[current_top_key].append((i + 1, line.strip(), "Single-quoted string found instead of double quotes", _extract_context(lines, i + 1)))

        if i < len(lines) - 1 and lines[i].rstrip().endswith(',') and lines[i + 1].lstrip().startswith('}'):
            comma_brace_issues[current_top_key].append((i + 1, lines[i].strip(), "Trailing comma before closing brace", _extract_context(lines, i + 1)))

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        context = _extract_context(lines, e.lineno)
        syntax_errors.append((e.lineno, e.msg, context))
        data = {}  # allow fallback structure analysis

    structure_issues = defaultdict(list)
    if isinstance(data, dict):
        for block, values in data.items():
            if not isinstance(values, dict):
                structure_issues[block].append("Top-level value is not a dictionary")
                continue
            for k, v in values.items():
                if not isinstance(k, str):
                    structure_issues[block].append(f"Key {k} is not a string")
                elif not k.isdigit():
                    structure_issues[block].append(f"Key '{k}' is not numeric (expected numeric string key)")
                if not isinstance(v, str):
                    structure_issues[block].append(f"Value for key '{k}' is not a string (found {type(v).__name__})")

    if not structure_issues and not any(single_quote_issues.values()) and not any(comma_brace_issues.values()) and not syntax_errors:
        print("\n No structural or format errors found. JSON is valid.")
        return

    if structure_issues:
        print("\n Structural issues detected:")
        for block, issues in structure_issues.items():
            print(f"- In block '{block}': ({len(issues)} issues)")
            for issue in issues:
                print(f"  - {issue}")

    if single_quote_issues:
        print("\n Single-quoted string values detected:")
        for block, issues in single_quote_issues.items():
            print(f"- In block '{block}': ({len(issues)} issues)")
            for lineno, line, explanation, context in issues:
                print(f"  Line {lineno}: {line}\n    → {explanation}\n    Context:")
                for ctx_line in context:
                    print(f"    {ctx_line}")

    if comma_brace_issues:
        print("\n Commas before closing braces detected:")
        for block, issues in comma_brace_issues.items():
            print(f"- In block '{block}': ({len(issues)} issues)")
            for lineno, line, explanation, context in issues:
                print(f"  Line {lineno}: {line}\n    → {explanation}\n    Context:")
                for ctx_line in context:
                    print(f"    {ctx_line}")

def _extract_context(lines, lineno, radius=2):
    start = max(0, lineno - radius - 1)
    end = min(len(lines), lineno + radius)
    return [f"  {i + 1}: {lines[i].rstrip()}" for i in range(start, end)]


def fix_commas_before_closing_brace(filepath, output_path):
    """
    Removes commas from the last key-value pair in objects
    before a closing brace like } or }, inside dictionaries.
    Returns the number of fixes made.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixed_lines = []
    fix_count = 0
    for i in range(len(lines)):
        current_line = lines[i].rstrip()
        next_line = lines[i + 1].lstrip() if i + 1 < len(lines) else ""

        if current_line.endswith(',') and next_line.startswith('}'):
            fixed_line = current_line.rstrip(',') + '\n'
            fixed_lines.append(fixed_line)
            fix_count += 1
        else:
            fixed_lines.append(lines[i])

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)

    print(f"Fixed {fix_count} comma(s) before closing braces saved to: {output_path}")
  


def fix_all_single_quoted_values(filepath, output_path):
    """
    Fixes all single-quoted string values in the entire file, regardless of top-level key.
    Returns the number of fixes made.
    """
    fix_count = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(output_path, 'w', encoding='utf-8') as f:
        for line in lines:
            match = re.match(r'^(\s*"\d+"\s*:\s*)\'(.*)\'(\s*[},]?)$', line)
            if match:
                key_part, value_part, suffix = match.groups()
                value_fixed = value_part.replace('"', '\\"')
                fixed_line = f'{key_part}"{value_fixed}"{suffix}\n'
                f.write(fixed_line)
                fix_count += 1
            else:
                f.write(line)

    print(f"Fixed {fix_count} single-quoted value(s) saved to: {output_path}")

