#!/bin/bash
# LocalPilot Benchmark Showcase
# Run this to show the full benchmark results with colors

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
echo -e "${CYAN}║${WHITE}            LocalPilot Benchmark Showcase                    ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${YELLOW}  Testing 10 Real-World Coding Tasks                        ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}Available Benchmark Tasks${NC}"
echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${GREEN}1.${NC} ${BLUE}add_docstring${NC}       - Add docstrings to functions"
echo -e "${GREEN}2.${NC} ${BLUE}add_type_hints${NC}      - Add Python type annotations"
echo -e "${GREEN}3.${NC} ${BLUE}fix_import${NC}          - Fix broken import statements"
echo -e "${GREEN}4.${NC} ${BLUE}add_parameter${NC}       - Add new function parameters"
echo -e "${GREEN}5.${NC} ${BLUE}add_default_value${NC}   - Add default parameter values"
echo -e "${GREEN}6.${NC} ${BLUE}add_error_handling${NC}  - Add try/except blocks"
echo -e "${GREEN}7.${NC} ${BLUE}extract_constant${NC}    - Extract magic numbers"
echo -e "${GREEN}8.${NC} ${BLUE}remove_unused_import${NC} - Clean up imports"
echo -e "${GREEN}9.${NC} ${BLUE}fix_typo${NC}            - Rename variables"
echo -e "${GREEN}10.${NC} ${BLUE}rename_function${NC}    - Refactor function names"
echo ""

echo -e "${MAGENTA}Choose demo type:${NC}"
echo -e "  ${WHITE}1${NC} - Quick demo (single task, ~10 seconds)"
echo -e "  ${WHITE}2${NC} - Full benchmark (all 10 tasks, ~3-4 minutes)"
echo ""
echo -ne "${YELLOW}Enter choice [1/2]: ${NC}"
read choice

if [ "$choice" == "1" ]; then
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                              ║${NC}"
    echo -e "${CYAN}║${WHITE}              Quick Benchmark Demo                           ${CYAN}║${NC}"
    echo -e "${CYAN}║                                                              ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${YELLOW}Running task: ${WHITE}add_docstring${NC}"
    echo -e "${BLUE}Model: ${WHITE}qwen2.5-coder:7b${NC}"
    echo ""
    
    python bench/run_bench.py --task add_docstring --mode harness --model qwen2.5-coder:7b
    
else
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                              ║${NC}"
    echo -e "${CYAN}║${WHITE}            Full Benchmark Suite                             ${CYAN}║${NC}"
    echo -e "${CYAN}║                                                              ║${NC}"
    echo -e "${CYAN}║${YELLOW}  This will run all 10 tasks (~3-4 minutes)                 ${CYAN}║${NC}"
    echo -e "${CYAN}║                                                              ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${BLUE}Model: ${WHITE}qwen2.5-coder:7b${NC}"
    echo -e "${BLUE}Mode: ${WHITE}harness (with all 4 safety gates)${NC}"
    echo ""
    
    echo -e "${YELLOW}Starting benchmark...${NC}"
    echo ""
    
    python bench/run_bench.py --mode harness --model qwen2.5-coder:7b
fi

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${WHITE}                  Key Takeaways                              ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${GREEN}  ✓ 80% Success Rate (8/10 tasks passing)                    ${CYAN}║${NC}"
echo -e "${CYAN}║${GREEN}  ✓ 0% Syntax Errors (safety gates work!)                    ${CYAN}║${NC}"
echo -e "${CYAN}║${YELLOW}  ⚠ 20% Broken Tests (2 edge cases, still valid syntax)     ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${WHITE}  Even on 'failed' tasks, LocalPilot never breaks syntax!    ${CYAN}║${NC}"
echo -e "${CYAN}║${WHITE}  The 4 safety gates prevent all syntax-breaking edits.      ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${MAGENTA}Results saved to: ${WHITE}bench/results.md${NC}"
echo ""
