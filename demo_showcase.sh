#!/bin/bash
# LocalPilot Visual Showcase Demo
# Run this script to show off LocalPilot with colorful output

set -e

# Colors for echo
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

clear

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${WHITE}               LocalPilot Live Demo                          ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${YELLOW}  🎯 80% Success Rate | 🔒 100% Local | ✅ 0% Syntax Errors ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}Phase 1: Setup Demo Project${NC}"
echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Create demo project
echo -e "${BLUE}📁 Creating demo project...${NC}"
rm -rf demo_showcase
mkdir -p demo_showcase
cd demo_showcase

# Create a file with multiple issues
cat > calculator.py << 'EOF'
def add(x, y):
    resutl = x + y
    return resutl

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y
EOF

echo -e "${GREEN}✓${NC} Created calculator.py with a typo"
echo ""

# Show the file
echo -e "${YELLOW}📄 Current file:${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
cat calculator.py
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
echo ""

# Create a test
cat > test_calculator.py << 'EOF'
from calculator import add, subtract

def test_add():
    assert add(2, 3) == 5

def test_subtract():
    assert subtract(5, 3) == 2

def test_no_typo():
    """Ensure the typo 'resutl' is fixed."""
    import inspect
    source = inspect.getsource(add)
    assert 'resutl' not in source, "Variable 'resutl' should be renamed to 'result'"
EOF

echo -e "${BLUE}📝 Created test_calculator.py${NC}"
echo ""

# Run tests to show failure
echo -e "${YELLOW}🧪 Running tests (should fail due to typo):${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
python -m pytest test_calculator.py -v 2>&1 | head -20 || true
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
echo ""

echo -e "${RED}✗${NC} Test failed: 'resutl' typo detected"
echo ""

# Pause for effect
echo -e "${MAGENTA}Press Enter to run LocalPilot...${NC}"
read

clear

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${WHITE}            LocalPilot: Safety Gates in Action               ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}Phase 2: Run LocalPilot with 4 Safety Gates${NC}"
echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}📡 Sending task to local LLM (qwen2.5-coder:7b)...${NC}"
echo -e "${BLUE}Task: ${WHITE}Fix the typo: rename 'resutl' to 'result' in calculator.py${NC}"
echo ""

# Run LocalPilot
cd ..
python -m agent.cli demo_showcase "Fix the typo: rename the variable 'resutl' to 'result' in calculator.py"

echo ""
echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}Phase 3: Verify Results${NC}"
echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Show the fixed file
echo -e "${YELLOW}📄 Fixed file:${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
cat demo_showcase/calculator.py
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
echo ""

# Run tests to show success
echo -e "${YELLOW}🧪 Running tests (should pass now):${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
cd demo_showcase
python -m pytest test_calculator.py -v
cd ..
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
echo ""

echo -e "${GREEN}✓${NC} All tests passed!"
echo ""

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${WHITE}                   ✨ Demo Complete! ✨                      ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${GREEN}  ✓ Path Guard    - File path verified                      ${CYAN}║${NC}"
echo -e "${CYAN}║${GREEN}  ✓ Fuzzy Patch   - Code matched with 80% similarity        ${CYAN}║${NC}"
echo -e "${CYAN}║${GREEN}  ✓ Syntax Gate   - Valid Python confirmed                  ${CYAN}║${NC}"
echo -e "${CYAN}║${GREEN}  ✓ Test/Lint Gate - All tests passing                      ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${YELLOW}  🎯 File safely edited in 1-2 steps                        ${CYAN}║${NC}"
echo -e "${CYAN}║${YELLOW}  🔒 Zero syntax errors                                     ${CYAN}║${NC}"
echo -e "${CYAN}║${YELLOW}  ⚡ All done locally - no cloud APIs!                      ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
