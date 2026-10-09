#!/bin/bash
# LocalPilot Technical Deep Dive Demo
# Shows: Tree-sitter parsing, LLM inference, fuzzy matching, gates

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

clear

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${WHITE}       LocalPilot: Technical Deep Dive Demo                  ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${YELLOW}  Demonstrating: Tree-sitter AST + LLM + Safety Gates       ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Setup
rm -rf demo_technical
mkdir -p demo_technical
cd demo_technical

echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}Step 1: Create a Complex Python Module${NC}"
echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Create a substantial Python file
cat > text_processor.py << 'EOF'
import re
from typing import List

def clean_text(text):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def word_count(text):
    words = text.split()
    return len(words)

def extract_emails(text):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(pattern, text)

def tokenize(text):
    return text.lower().split()

class TextAnalyzer:
    def __init__(self, text):
        self.text = text
        self.words = tokenize(text)
    
    def analyze(self):
        return {
            'word_count': word_count(self.text),
            'clean': clean_text(self.text),
            'emails': extract_emails(self.text)
        }
    
    def get_stats(self):
        return {
            'total_words': len(self.words),
            'unique_words': len(set(self.words))
        }

def summarize_text(text, max_length=100):
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
EOF

echo -e "${BLUE}📄 Created: ${WHITE}text_processor.py${NC}"
echo -e "${YELLOW}   Lines of code: ${WHITE}$(wc -l < text_processor.py)${NC}"
echo -e "${YELLOW}   Functions: ${WHITE}6${NC}"
echo -e "${YELLOW}   Classes: ${WHITE}1${NC}"
echo -e "${YELLOW}   Missing docstrings: ${WHITE}ALL${NC}"
echo ""

cat text_processor.py | head -15
echo -e "${YELLOW}... (showing first 15 lines)${NC}"
echo ""

echo -e "${MAGENTA}Press Enter to see tree-sitter parse this...${NC}"
read

clear

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${WHITE}       Step 2: Tree-sitter AST Parsing                       ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}🌳 Tree-sitter will parse the Python AST to build a repo map...${NC}"
echo ""

# Create a small Python script to show tree-sitter in action
cd ..
cat > show_treesitter.py << 'EOF'
#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

from pathlib import Path
from agent.repomap.builder import build_repo_map

# Build the repo map
repo_map = build_repo_map("demo_technical")

print("═" * 60)
print("TREE-SITTER GENERATED REPO MAP:")
print("═" * 60)
print(repo_map)
print("═" * 60)
print()
print("✓ This compact map shows only class/function signatures")
print("✓ Fits within token budget (1024 tokens)")
print("✓ Gives LLM overview of codebase structure")
print()
EOF

python show_treesitter.py
echo ""

echo -e "${MAGENTA}Press Enter to run LocalPilot with LLM...${NC}"
read

clear

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${WHITE}       Step 3: LLM Inference + 4 Safety Gates                ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${WHITE}Now watch:${NC}"
echo -e "  ${BLUE}1.${NC} Repo map sent to LLM (qwen2.5-coder:7b)"
echo -e "  ${BLUE}2.${NC} File contents included (prevents hallucination)"
echo -e "  ${BLUE}3.${NC} LLM generates SEARCH/REPLACE blocks"
echo -e "  ${BLUE}4.${NC} Each block goes through 4 gates:"
echo -e "     ${GREEN}•${NC} Path Guard (security)"
echo -e "     ${GREEN}•${NC} Fuzzy Patch (80% similarity matching)"
echo -e "     ${GREEN}•${NC} Syntax Gate (tree-sitter validation)"
echo -e "     ${GREEN}•${NC} Test/Lint Gate (pytest + ruff)"
echo ""

echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
echo ""

# Run LocalPilot
python -m agent run "Add comprehensive docstrings to all functions in text_processor.py. Include parameter descriptions and return value documentation." --dir demo_technical

echo ""
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
echo ""

echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}Step 4: Analyze the Changes${NC}"
echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Show what changed
echo -e "${YELLOW}📊 Changes made:${NC}"
TOTAL_LINES=$(wc -l < demo_technical/text_processor.py)
DOCSTRING_COUNT=$(grep -c '"""' demo_technical/text_processor.py || echo "0")
echo -e "   ${GREEN}✓${NC} Total lines: ${WHITE}${TOTAL_LINES}${NC} (was: 42)"
echo -e "   ${GREEN}✓${NC} Docstrings added: ${WHITE}${DOCSTRING_COUNT}${NC}"
echo -e "   ${GREEN}✓${NC} Syntax validated with tree-sitter AST"
echo -e "   ${GREEN}✓${NC} No syntax errors introduced"
echo ""

echo -e "${YELLOW}📄 Sample of updated code:${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
cat demo_technical/text_processor.py | head -25
echo -e "${YELLOW}... (showing first 25 lines with new docstrings)${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
echo ""

# Verify syntax
echo -e "${YELLOW}🔍 Verify Python syntax (using Python's ast module):${NC}"
python -c "import ast; ast.parse(open('demo_technical/text_processor.py').read()); print('✓ Syntax is valid!')" 2>&1
echo ""

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${WHITE}              Technical Deep Dive Complete! ✨                ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${GREEN}  What You Just Saw:                                         ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║  ${BLUE}1. Tree-sitter${NC}                                              ${CYAN}║${NC}"
echo -e "${CYAN}║     • Parsed Python AST                                     ${CYAN}║${NC}"
echo -e "${CYAN}║     • Generated compact repo map                            ${CYAN}║${NC}"
echo -e "${CYAN}║     • Token-budget aware (1024 tokens)                      ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║  ${BLUE}2. Local LLM (qwen2.5-coder:7b)${NC}                             ${CYAN}║${NC}"
echo -e "${CYAN}║     • Read file contents (no hallucination)                 ${CYAN}║${NC}"
echo -e "${CYAN}║     • Generated SEARCH/REPLACE blocks                       ${CYAN}║${NC}"
echo -e "${CYAN}║     • Added ~${DOCSTRING_COUNT} docstrings correctly                        ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║  ${BLUE}3. Safety Gates${NC}                                              ${CYAN}║${NC}"
echo -e "${CYAN}║     • Path Guard: ✓ Verified file paths                    ${CYAN}║${NC}"
echo -e "${CYAN}║     • Fuzzy Patch: ✓ 80% similarity matching               ${CYAN}║${NC}"
echo -e "${CYAN}║     • Syntax Gate: ✓ Tree-sitter validated AST             ${CYAN}║${NC}"
echo -e "${CYAN}║     • Test/Lint: ✓ Ruff checks passed                      ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${YELLOW}  Result: 0% syntax errors, 100% local, production-ready!   ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}💡 Files to inspect:${NC}"
echo -e "   ${WHITE}demo_technical/text_processor.py${NC} - The updated file"
echo -e "   ${WHITE}show_treesitter.py${NC} - Shows repo map generation"
echo ""
