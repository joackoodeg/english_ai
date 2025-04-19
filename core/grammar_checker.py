import language_tool_python
import re
from typing import Dict, List, Tuple, Any

# Initialize the tool
tool = language_tool_python.LanguageTool('en-US')

# Categorize issues by type for better feedback
VERB_TENSE_RULES = [
    'TENSE_SEQUENCE',
    'TENSE_SIMPLE_PAST',
    'PAST_TENSE',
    'CONDITIONAL_PERFECT',
    'VERB_FORM',
    'VERB_TENSE',
]

EXPRESSION_IMPROVEMENT_RULES = [
    'COLLOCATION',
    'REDUNDANCY',
    'WORDINESS',
    'INFORMAL_EXPRESSIONS',
]

def categorize_issue(rule_id: str, message: str) -> str:
    """Categorize the type of grammatical issue"""
    rule_id = rule_id.upper()
    
    # Verb tense issues
    if any(tense_rule in rule_id for tense_rule in VERB_TENSE_RULES) or 'TENSE' in rule_id:
        return 'VERB_TENSE'
    
    # Expression improvements
    if any(expr_rule in rule_id for expr_rule in EXPRESSION_IMPROVEMENT_RULES):
        return 'EXPRESSION'
        
    # Common categories
    if 'GRAMMAR' in rule_id:
        return 'GRAMMAR'
    elif 'SPELL' in rule_id:
        return 'SPELLING'
    elif 'PUNCT' in rule_id:
        return 'PUNCTUATION'
    elif 'STYLE' in rule_id:
        return 'STYLE'
    elif 'AGREEMENT' in rule_id:
        return 'AGREEMENT'
    else:
        return 'OTHER'

def suggest_better_expression(match: Any) -> str:
    """Generate a suggestion for better expression based on match"""
    replacement = match.replacements[0] if match.replacements else None
    
    if replacement:
        return f"Consider using '{replacement}' instead of '{match.context}'"
    else:
        return f"This expression could be improved: '{match.context}'"

def correct_text(text: str) -> Tuple[str, List[str], Dict[str, List[str]]]:
    """
    Correct text and provide detailed feedback by category.
    
    Args:
        text: The input text to check
        
    Returns:
        Tuple containing:
        - corrected text
        - list of issues
        - dictionary of categorized suggestions
    """
    matches = tool.check(text)
    corrected = language_tool_python.utils.correct(text, matches)
    
    # Basic issues list
    issues = [f"{m.ruleIssueType.upper()}: {m.message}" for m in matches]
    
    # Categorized suggestions with explanations
    categorized = {
        'VERB_TENSE': [],
        'EXPRESSION': [],
        'GRAMMAR': [],
        'SPELLING': [],
        'PUNCTUATION': [],
        'STYLE': [],
        'AGREEMENT': [],
        'OTHER': []
    }
    
    for match in matches:
        category = categorize_issue(match.ruleId, match.message)
        
        # Basic message
        message = f"{match.message}"
        
        # Add replacements if available
        if match.replacements:
            message += f" Suggestion: '{match.replacements[0]}'"
            
        # For expression improvements, add additional context
        if category == 'EXPRESSION':
            message += "\n" + suggest_better_expression(match)
            
        # For verb tense issues, explain the problem
        if category == 'VERB_TENSE':
            message += "\nConsistency in verb tense is important for clear communication."
            
        categorized[category].append(message)
    
    return corrected, issues, categorized

def get_alternative_expressions(text: str) -> List[Tuple[str, str]]:
    """
    Find natural-sounding alternatives to common expressions.
    
    Args:
        text: The input text
        
    Returns:
        List of tuples with (original phrase, better alternative)
    """
    # Common expressions and their better alternatives
    expression_map = {
        r'\b(?:very|really|extremely) (\w+)\b': {
            'pattern': r'very|really|extremely',
            'examples': {
                'happy': ['delighted', 'thrilled', 'overjoyed'],
                'sad': ['devastated', 'heartbroken', 'miserable'],
                'tired': ['exhausted', 'drained', 'fatigued'],
                'big': ['enormous', 'massive', 'gigantic'],
                'small': ['tiny', 'miniature', 'minuscule'],
                'good': ['excellent', 'outstanding', 'superb'],
                'bad': ['terrible', 'awful', 'dreadful'],
                'hungry': ['famished', 'starving', 'ravenous'],
                'interesting': ['fascinating', 'captivating', 'intriguing'],
                'scared': ['terrified', 'petrified', 'horrified'],
            },
            'default': ['notably', 'particularly', 'remarkably']
        },
        r'\bI think\b': {
            'alternatives': ['I believe', 'In my opinion', 'I consider', 'From my perspective']
        },
        r'\ba lot of\b': {
            'alternatives': ['many', 'numerous', 'plenty of', 'a great deal of']
        },
        r'\bnice\b': {
            'alternatives': ['pleasant', 'enjoyable', 'delightful', 'charming']
        },
        r'\bgood\b': {
            'alternatives': ['excellent', 'superb', 'outstanding', 'wonderful']
        },
        r'\bbad\b': {
            'alternatives': ['poor', 'terrible', 'unpleasant', 'disappointing']
        },
        r'\bsaid\b': {
            'alternatives': ['mentioned', 'stated', 'explained', 'described']
        },
        r'\blike\b': {
            'alternatives': ['enjoy', 'appreciate', 'favor', 'prefer']
        },
    }
    
    suggestions = []
    
    for pattern, info in expression_map.items():
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            original = match.group(0)
            
            # For the intensity modifiers (very, really, etc.)
            if 'pattern' in info:
                intensity_word = re.search(info['pattern'], original, re.IGNORECASE).group(0)
                adjective = match.group(1).lower()
                
                if adjective in info['examples']:
                    alternatives = info['examples'][adjective]
                else:
                    alternatives = info['default']
                    
                for alt in alternatives:
                    suggestions.append((original, alt))
                    
            # For simple replacements
            elif 'alternatives' in info:
                for alt in info['alternatives']:
                    suggestions.append((original, alt))
    
    return suggestions if suggestions else []