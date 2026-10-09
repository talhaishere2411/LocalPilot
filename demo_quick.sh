#!/bin/bash
# LocalPilot Quick Demo (No Pauses)
# Run this for a fast, automated demo

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

clear

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${WHITE}               LocalPilot Live Demo                          ${CYAN}║${NC}"
echo -e "${CYAN}║${YELLOW}  🎯 80% Success | 🔒 100% Local | ✅ 0% Syntax Errors ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Cleanup old demo
rm -rf demo_quick
mkdir -p demo_quick
cd demo_quick

# Create test file - simpler example
cat > calculator.py << 'EOF'
def add(x, y):
    return x + y

def multiply(x, y):
    return x * y
EOF

cat > test_calculator.py << 'EOF'
from calculator import add, multiply

def test_add():
    assert add(2, 3) == 5

def test_add_has_docstring():
    assert add.__doc__ is not None, "add function should have a docstring"
    assert "add" in add.__doc__.lower() or "sum" in add.__doc__.lower()
EOF

cd ..

echo -e "${BLUE}📁 Created demo_quick/calculator.py${NC}"
echo ""

echo -e "${YELLOW}📄 BEFORE (no docstrings):${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
cat demo_quick/calculator.py
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
echo ""

echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}Running LocalPilot with 4 Safety Gates${NC}"
echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Run LocalPilot
python -m agent run "Add a docstring to the add function that says 'Add two numbers and return the sum'" --dir demo_quick

echo ""
echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}Results${NC}"
echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}📄 AFTER (with docstring):${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
cat demo_quick/calculator.py
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
echo ""

echo -e "${YELLOW}🧪 Running tests:${NC}"
cd demo_quick && python -m pytest test_calculator.py -v
cd ..

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${WHITE}                   ✨ Demo Complete! ✨                      ${CYAN}║${NC}"
echo -e "${CYAN}║${GREEN}  ✓ All 4 gates passed                                       ${CYAN}║${NC}"
echo -e "${CYAN}║${GREEN}  ✓ Docstring added successfully                                ${CYAN}║${NC}"
echo -e "${CYAN}║${GREEN}  ✓ All tests passing                                        ${CYAN}║${NC}"
echo -e "${CYAN}║${YELLOW}  🔒 100% local - no cloud APIs!                            ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
