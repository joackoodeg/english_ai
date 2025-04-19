import language_tool_python

tool = language_tool_python.LanguageTool('en-US')

def correct_text(text: str) -> tuple[str, list[str]]:
    matches = tool.check(text)
    corrected = language_tool_python.utils.correct(text, matches)
    issues = [f"{m.ruleIssueType.upper()}: {m.message}" for m in matches]
    return corrected, issues

