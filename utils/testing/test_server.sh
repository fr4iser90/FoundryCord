#!/run/current-system/sw/bin/bash

# Colors for better readability
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Server information
SERVER_USER="docker"
SERVER_HOST="192.168.178.33"
SERVER_DIR="/home/docker/docker/companion-management/discord-server-bot"
DOCKER_DIR="${SERVER_DIR}/docker/bot"

echo -e "${YELLOW}=== HomeLab Discord Bot Server Test Script ===${NC}"
echo "Testing server: ${SERVER_HOST}"
echo "Testing directory: ${SERVER_DIR}"
echo ""

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
    fi
}

# Test 1: Check SSH connection
echo -e "${YELLOW}Test 1: SSH Connection${NC}"
ssh -q ${SERVER_USER}@${SERVER_HOST} exit
print_result $? "SSH connection to ${SERVER_USER}@${SERVER_HOST}"

# Test 2: Check if Docker is running
echo -e "\n${YELLOW}Test 2: Docker Service${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} "systemctl is-active docker" > /dev/null 2>&1
print_result $? "Docker service is running"

# Test 3: Check if Docker Compose is installed
echo -e "\n${YELLOW}Test 3: Docker Compose${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} "docker-compose --version" > /dev/null 2>&1
print_result $? "Docker Compose is installed"

# Test 4: Check if project directory exists
echo -e "\n${YELLOW}Test 4: Project Directory${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} "[ -d ${SERVER_DIR} ]"
print_result $? "Project directory exists"

# Test 5: Check if docker-compose.yml exists
echo -e "\n${YELLOW}Test 5: Docker Compose File${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} "[ -f ${SERVER_DIR}/docker-compose.yml ]"
print_result $? "docker-compose.yml exists"

# Test 6: Check if environment files exist
echo -e "\n${YELLOW}Test 6: Environment Files${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} "[ -f ${SERVER_DIR}/.env.discordbot ]"
print_result $? ".env.discordbot exists"
ssh ${SERVER_USER}@${SERVER_HOST} "[ -f ${SERVER_DIR}/.env.postgres ]"
print_result $? ".env.postgres exists"

# Test 7: Check if containers are running
echo -e "\n${YELLOW}Test 7: Container Status${NC}"
POSTGRES_RUNNING=$(ssh ${SERVER_USER}@${SERVER_HOST} "docker ps -q -f name=homelab-postgres")
BOT_RUNNING=$(ssh ${SERVER_USER}@${SERVER_HOST} "docker ps -q -f name=discord-server-bot")

if [ -n "$POSTGRES_RUNNING" ]; then
    print_result 0 "PostgreSQL container is running"
else
    print_result 1 "PostgreSQL container is not running"
fi

if [ -n "$BOT_RUNNING" ]; then
    print_result 0 "Discord bot container is running"
else
    print_result 1 "Discord bot container is not running"
fi

# Test 8: Check PostgreSQL connection
echo -e "\n${YELLOW}Test 8: PostgreSQL Connection${NC}"
PG_TEST=$(ssh ${SERVER_USER}@${SERVER_HOST} "docker exec homelab-postgres pg_isready -U postgres" 2>&1)
if [[ $PG_TEST == *"accepting connections"* ]]; then
    print_result 0 "PostgreSQL is accepting connections"
else
    print_result 1 "PostgreSQL connection failed: $PG_TEST"
fi

# Test 9: Check if bot user exists in PostgreSQL
echo -e "\n${YELLOW}Test 9: Database User${NC}"
USER_EXISTS=$(ssh ${SERVER_USER}@${SERVER_HOST} "docker exec homelab-postgres psql -U postgres -tAc \"SELECT 1 FROM pg_roles WHERE rolname='homelab_discord_bot'\"")
if [ "$USER_EXISTS" == "1" ]; then
    print_result 0 "Database user 'homelab_discord_bot' exists"
else
    print_result 1 "Database user 'homelab_discord_bot' does not exist"
fi

# Test 10: Check bot logs for errors
echo -e "\n${YELLOW}Test 10: Bot Logs${NC}"
ERROR_COUNT=$(ssh ${SERVER_USER}@${SERVER_HOST} "docker logs discord-server-bot 2>&1 | grep -c 'ERROR\|CRITICAL\|FATAL'")
if [ "$ERROR_COUNT" -eq 0 ]; then
    print_result 0 "No critical errors in bot logs"
else
    print_result 1 "Found $ERROR_COUNT critical errors in bot logs"
    echo -e "${YELLOW}Recent errors:${NC}"
    ssh ${SERVER_USER}@${SERVER_HOST} "docker logs discord-server-bot 2>&1 | grep 'ERROR\|CRITICAL\|FATAL' | tail -5"
fi

# Test 11: Check system resources
echo -e "\n${YELLOW}Test 11: System Resources${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} "echo 'CPU Usage:'; top -bn1 | grep 'Cpu(s)' | awk '{print \$2 \"%\"}'"
ssh ${SERVER_USER}@${SERVER_HOST} "echo 'Memory Usage:'; free -m | awk 'NR==2{printf \"%.2f%%\", \$3*100/\$2}'"
ssh ${SERVER_USER}@${SERVER_HOST} "echo 'Disk Usage:'; df -h | grep -v tmpfs | grep -v udev"

# Test 12: Network connectivity test
echo -e "\n${YELLOW}Test 12: Network Connectivity${NC}"
DISCORD_TEST=$(ssh ${SERVER_USER}@${SERVER_HOST} "curl -s -o /dev/null -w '%{http_code}' https://discord.com/api/v10/gateway")
if [ "$DISCORD_TEST" == "200" ]; then
    print_result 0 "Discord API is reachable"
else
    print_result 1 "Discord API is not reachable (HTTP $DISCORD_TEST)"
fi

echo -e "\n${YELLOW}=== Test Summary ===${NC}"
echo "All tests completed. Review the results above to ensure your server is properly configured."
echo "If any tests failed, address the issues before deploying your bot."