#!/bin/bash
#
# 数据服务健康检查脚本（一次性本地测试）
# 用法: ./check_data_service.sh
#

set -e

# 配置
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"
API_PORT=8001
API_HOST=localhost

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查结果计数
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

print_header() {
    echo ""
    echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
}

print_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((CHECKS_PASSED++)) || true
}

print_fail() {
    echo -e "${RED}✗${NC} $1"
    ((CHECKS_FAILED++)) || true
}

print_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((CHECKS_WARNING++)) || true
}

print_info() {
    echo -e "  ${BLUE}ℹ${NC} $1"
}

# ==================== 检查 1: Docker 容器状态 ====================
check_containers() {
    print_header "1. Docker 容器状态检查"
    
    local containers=("data-service" "data-celery-worker" "data-celery-beat")
    local all_running=true
    
    for container in "${containers[@]}"; do
        local status
        status=$(docker-compose -f "$COMPOSE_FILE" ps -q "$container" 2>/dev/null | xargs docker inspect -f '{{.State.Status}}' 2>/dev/null || echo "not_found")
        
        if [ "$status" = "running" ]; then
            local health
            health=$(docker-compose -f "$COMPOSE_FILE" ps -q "$container" 2>/dev/null | xargs docker inspect -f '{{.State.Health.Status}}' 2>/dev/null || echo "none")
            if [ "$health" = "healthy" ] || [ "$health" = "none" ]; then
                print_pass "$container: 运行中 (状态: $status, 健康: $health)"
            else
                print_warn "$container: 运行中但健康检查未通过 (健康: $health)"
            fi
        elif [ "$status" = "not_found" ]; then
            print_fail "$container: 容器不存在"
            all_running=false
        else
            print_fail "$container: 未运行 (状态: $status)"
            all_running=false
        fi
    done
    
    $all_running && return 0 || return 1
}

# ==================== 检查 2: API 健康端点 ====================
check_api_health() {
    print_header "2. API 健康端点检查"
    
    local response
    local http_code
    
    # 尝试获取健康端点
    response=$(curl -s -w "\n%{http_code}" "http://${API_HOST}:${API_PORT}/health" 2>/dev/null || echo -e "\n000")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        print_pass "API 响应正常 (HTTP $http_code)"
        print_info "响应: $body"
        return 0
    elif [ "$http_code" = "000" ]; then
        print_fail "无法连接到 API (连接被拒绝)"
        print_info "请检查 data-service 是否运行，端口 $API_PORT 是否正确"
        return 1
    else
        print_fail "API 异常 (HTTP $http_code)"
        print_info "响应: $body"
        return 1
    fi
}

# ==================== 检查 3: Celery Worker 状态 ====================
check_celery_worker() {
    print_header "3. Celery Worker 状态检查"
    
    # 检查 Worker 是否响应
    local worker_status
    worker_status=$(docker-compose -f "$COMPOSE_FILE" exec -T data-celery-worker celery -A app.worker.celery_app inspect ping --timeout=5 2>&1) || true
    
    if echo "$worker_status" | grep -q "pong"; then
        print_pass "Celery Worker 响应正常"
        # 获取 Worker 统计
        local stats
        stats=$(docker-compose -f "$COMPOSE_FILE" exec -T data-celery-worker celery -A app.worker.celery_app inspect stats --timeout=5 2>&1) || true
        local processed
        processed=$(echo "$stats" | grep -o '"total": {[0-9]*' | head -1 | grep -o '[0-9]*' || echo "unknown")
        print_info "已处理任务数: $processed"
        return 0
    else
        print_fail "Celery Worker 无响应"
        print_info "错误信息: $worker_status"
        return 1
    fi
}

# ==================== 检查 4: 最近任务执行日志 ====================
check_recent_logs() {
    print_header "4. 数据同步任务执行检查"
    
    # 获取最近的同步完成日志
    local last_sync
    last_sync=$(docker-compose -f "$COMPOSE_FILE" logs --tail=200 data-celery-worker 2>/dev/null | grep "Comprehensive GitHub data synchronization task finished" | tail -1 || true)
    
    if [ -n "$last_sync" ]; then
        # 提取时间戳（假设日志格式为：YYYY-MM-DD HH:MM:SS）
        local sync_time
        sync_time=$(echo "$last_sync" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' || echo "unknown")
        
        if [ "$sync_time" != "unknown" ]; then
            # 计算时间差（简化处理，只比较小时和分钟）
            local current_epoch
            local sync_epoch
            current_epoch=$(date +%s)
            sync_epoch=$(date -d "$sync_time" +%s 2>/dev/null || echo "0")
            
            if [ "$sync_epoch" != "0" ]; then
                local diff_minutes=$(( (current_epoch - sync_epoch) / 60 ))
                
                if [ $diff_minutes -lt 10 ]; then
                    print_pass "最近同步: $sync_time (${diff_minutes}分钟前)"
                elif [ $diff_minutes -lt 30 ]; then
                    print_warn "最近同步: $sync_time (${diff_minutes}分钟前)"
                else
                    print_fail "最近同步: $sync_time (${diff_minutes}分钟前) - 超过30分钟未同步"
                fi
            else
                print_warn "最近同步: $sync_time (无法计算时间差)"
            fi
        else
            print_warn "发现同步日志但无法解析时间"
        fi
        
        # 检查是否有错误
        local recent_errors
        recent_errors=$(docker-compose -f "$COMPOSE_FILE" logs --tail=100 data-celery-worker 2>/dev/null | grep -i "error\|failed\|exception" | tail -5 || true)
        if [ -n "$recent_errors" ]; then
            print_warn "最近日志中发现错误信息:"
            echo "$recent_errors" | while read -r line; do
                print_info "$line"
            done
        fi
    else
        print_fail "未找到任何数据同步完成记录"
        print_info "可能原因: 1) 服务刚启动 2) 调度器未正常工作 3) 任务执行失败"
        return 1
    fi
}

# ==================== 检查 5: Celery Beat 调度器 ====================
check_celery_beat() {
    print_header "5. Celery Beat 调度器检查"
    
    # 检查最近是否有任务被发送
    local last_sent
    last_sent=$(docker-compose -f "$COMPOSE_FILE" logs --tail=100 data-celery-beat 2>/dev/null | grep "Sending due task" | tail -1 || true)
    
    if [ -n "$last_sent" ]; then
        local sent_time
        sent_time=$(echo "$last_sent" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' || echo "unknown")
        print_pass "调度器正常，最近触发: $sent_time"
        return 0
    else
        print_warn "未找到调度器触发记录"
        print_info "如果服务刚启动，这可能正常，等待最多5分钟后会首次触发"
        return 1
    fi
}

# ==================== 检查 6: 数据更新验证（可选） ====================
check_data_freshness() {
    print_header "6. 数据新鲜度检查（数据库）"
    
    # 检查数据库中是否有仓库数据
    local repo_count
    repo_count=$(docker-compose -f "$COMPOSE_FILE" exec -T db psql -U postgres -d github_store -t -c "SELECT COUNT(*) FROM repositories;" 2>/dev/null | xargs || true)
    
    if [ -n "$repo_count" ] && [ "$repo_count" -gt 0 ] 2>/dev/null; then
        print_pass "数据库中有 $repo_count 个仓库"
        
        # 检查最新同步时间
        local latest_sync
        latest_sync=$(docker-compose -f "$COMPOSE_FILE" exec -T db psql -U postgres -d github_store -t -c "SELECT MAX(last_synced_at) FROM repositories;" 2>/dev/null | xargs || true)
        
        if [ -n "$latest_sync" ] && [ "$latest_sync" != "NULL" ]; then
            print_info "最新同步时间: $latest_sync"
        else
            print_warn "仓库数据存在但未设置 last_synced_at"
        fi
    else
        print_warn "数据库中暂无仓库数据"
        print_info "如果是全新部署，这是正常的，首次同步可能需要几分钟"
    fi
}

# ==================== 主函数 ====================
main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║       GitHub 数据服务健康检查                              ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # 检查 docker-compose 是否可用
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}错误: 未找到 docker-compose 命令${NC}"
        exit 1
    fi
    
    # 检查配置文件是否存在
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}错误: 未找到 $COMPOSE_FILE${NC}"
        exit 1
    fi
    
    # 执行各项检查
    check_containers
    check_api_health
    check_celery_worker
    check_recent_logs
    check_celery_beat
    check_data_freshness
    
    # 总结
    print_header "检查结果汇总"
    echo -e "${GREEN}通过: $CHECKS_PASSED${NC}  |  ${YELLOW}警告: $CHECKS_WARNING${NC}  |  ${RED}失败: $CHECKS_FAILED${NC}"
    echo ""
    
    if [ $CHECKS_FAILED -eq 0 ]; then
        if [ $CHECKS_WARNING -eq 0 ]; then
            echo -e "${GREEN}🎉 所有检查通过！数据服务运行正常。${NC}"
            exit 0
        else
            echo -e "${YELLOW}⚠ 服务基本正常，但存在警告项，建议查看详情。${NC}"
            exit 0
        fi
    else
        echo -e "${RED}❌ 检测到问题，请根据上述信息排查。${NC}"
        echo ""
        echo "常用排查命令:"
        echo "  查看日志: docker-compose -f $COMPOSE_FILE logs -f"
        echo "  重启服务: docker-compose -f $COMPOSE_FILE restart"
        echo "  查看状态: docker-compose -f $COMPOSE_FILE ps"
        exit 1
    fi
}

# 执行主函数
main "$@"
