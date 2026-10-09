#!/bin/bash
# LocalPilot Two-Phase Demo
# Phase 1: Show the problem (messy code)
# Phase 2: Watch LocalPilot fix it (LLM + gates + tree-sitter)

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
echo -e "${CYAN}║${WHITE}          LocalPilot: Two-Phase Live Demo                    ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${YELLOW}  Phase 1: Show the messy code                               ${CYAN}║${NC}"
echo -e "${CYAN}║${YELLOW}  Phase 2: Watch LocalPilot fix it with 4 safety gates       ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Cleanup
rm -rf demo_twophase
mkdir -p demo_twophase
cd demo_twophase

echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}PHASE 1: The Problem - Messy Python Code${NC}"
echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Create a realistic Python file with multiple issues
cat > data_processor.py << 'EOF'
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count

def filter_values(items, threshold):
    filtered = []
    for item in items:
        if item >= threshold:
            filtered.append(item)
    return filtered

def transform_data(data):
    transformed = []
    for d in data:
        transformed.append(d ** 2)
    return transformed

class DataAnalyzer:
    def __init__(self, data):
        self.data = data
    
    def analyze(self):
        return {
            'mean': calculate_average(self.data),
            'processed': process_data(self.data)
        }
EOF

echo -e "${RED}❌ Issues with this code:${NC}"
echo -e "   ${YELLOW}1.${NC} No docstrings - unclear what functions do"
echo -e "   ${YELLOW}2.${NC} No type hints - unclear parameter/return types"
echo -e "   ${YELLOW}3.${NC} No error handling - calculate_average fails on empty list"
echo -e "   ${YELLOW}4.${NC} Poor documentation for DataAnalyzer class"
echo ""

echo -e "${BLUE}📄 Current file (${WHITE}data_processor.py${BLUE}):${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
cat data_processor.py | head -20
echo -e "${YELLOW}... (showing first 20 lines, full file has ~35 lines)${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
echo ""

# Create tests
cat > test_data_processor.py << 'EOF'
import pytest
from data_processor import process_data, calculate_average, filter_values

def test_process_data():
    assert process_data([1, 2, 3]) == [2, 4, 6]

def test_calculate_average():
    assert calculate_average([1, 2, 3, 4, 5]) == 3.0

def test_filter_values():
    assert filter_values([1, 5, 10, 15], 10) == [10, 15]

def test_functions_have_docstrings():
    """Check that key functions have docstrings."""
    assert process_data.__doc__ is not None, "process_data needs docstring"
    assert calculate_average.__doc__ is not None, "calculate_average needs docstring"
    assert filter_values.__doc__ is not None, "filter_values needs docstring"
EOF

echo -e "${YELLOW}🧪 Current test status:${NC}"
cd ..
python -m pytest demo_twophase/test_data_processor.py -v 2>&1 | tail -15 || true
echo ""

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${MAGENTA}Press Enter to start Phase 2 (LocalPilot AI fixing)...${NC}"
read

clear

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${WHITE}          PHASE 2: LocalPilot Safety Pipeline                ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${WHITE}What you'll see:${NC}"
echo -e "  ${GREEN}1.${NC} ${BLUE}Building Repo Map${NC} - Tree-sitter parses Python AST"
echo -e "  ${GREEN}2.${NC} ${BLUE}LLM Inference${NC} - Qwen 2.5 Coder generates SEARCH/REPLACE blocks"
echo -e "  ${GREEN}3.${NC} ${BLUE}Gate 1: Path Guard${NC} - Ensures file path is safe"
echo -e "  ${GREEN}4.${NC} ${BLUE}Gate 2: Fuzzy Patch${NC} - Finds code with 80% similarity"
echo -e "  ${GREEN}5.${NC} ${BLUE}Gate 3: Syntax Gate${NC} - Tree-sitter validates Python syntax"
echo -e "  ${GREEN}6.${NC} ${BLUE}Gate 4: Test/Lint Gate${NC} - Runs pytest + ruff checks"
echo ""

echo -e "${YELLOW}📡 Sending task to qwen2.5-coder:7b...${NC}"
echo -e "${WHITE}Task: Add docstrings to all functions in data_processor.py${NC}"
echo ""

echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
echo ""

# Run LocalPilot with the task
python -m agent run "Add docstrings to the functions process_data, calculate_average, and filter_values. Each docstring should describe what the function does, its parameters, and return value." --dir demo_twophase

echo ""
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
echo ""

echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}RESULTS: Before vs After${NC}"
echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}📄 Updated file (first 30 lines):${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
cat demo_twophase/data_processor.py | head -30
echo -e "${YELLOW}... (file continues)${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
echo ""

echo -e "${YELLOW}🧪 Final test results:${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
cd demo_twophase
python -m pytest test_data_processor.py -v
cd ..
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
echo ""

# Count changes
FUNCS_WITH_DOCS=$(grep -c '"""' demo_twophase/data_processor.py || echo "0")

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${WHITE}                   Demo Complete! ✨                         ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${GREEN}  What LocalPilot Did:                                       ${CYAN}║${NC}"
echo -e "${CYAN}║${GREEN}    ✓ Parsed Python AST with tree-sitter                    ${CYAN}║${NC}"
echo -e "${CYAN}║${GREEN}    ✓ Generated repo map (token-budget aware)               ${CYAN}║${NC}"
echo -e "${CYAN}║${GREEN}    ✓ LLM created ${FUNCS_WITH_DOCS} docstrings with SEARCH/REPLACE blocks    ${CYAN}║${NC}"
echo -e "${CYAN}║${GREEN}    ✓ All 4 safety gates passed                             ${CYAN}║${NC}"
echo -e "${CYAN}║${GREEN}    ✓ Code validated with pytest + ruff                     ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${YELLOW}  Key Metrics:                                               ${CYAN}║${NC}"
echo -e "${CYAN}║${YELLOW}    • 0% syntax errors (gates work!)                        ${CYAN}║${NC}"
echo -e "${CYAN}║${YELLOW}    • 100% local (no cloud APIs)                            ${CYAN}║${NC}"
echo -e "${CYAN}║${YELLOW}    • Real tree-sitter AST parsing                          ${CYAN}║${NC}"
echo -e "${CYAN}║${YELLOW}    • Real LLM inference with qwen2.5-coder:7b              ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}💡 Pro Tip:${NC} Check ${WHITE}demo_twophase/data_processor.py${NC} to see the actual changes!"
echo ""
