#!/usr/bin/env bash
# 批量生成 AI 图文攻略（按主题轮换，避免雷同）
# 用法: bash scripts/batch_gen_guides.sh "游戏id:数量 游戏id:数量 ..."
# 参数格式: "2:8 4:8 6:8 8:8 9:8"（每游戏 8 个不同主题）
set -e
B=http://localhost:8081/api/v1
TOKEN=$(curl -s -X POST $B/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['accessToken'])")

# 获取主题列表（8 个）
TOPICS=$(curl -s -H "Authorization: Bearer $TOKEN" "$B/ai/guide-topics" | python3 -c "import sys,json;print('|'.join(json.load(sys.stdin)['data']))")

for spec in ${1}; do
  game_id="${spec%%:*}"
  count="${spec##*:}"
  echo "==> gameId=$game_id 生成 $count 篇（轮换主题）"
  i=0
  while [ "$i" -lt "$count" ]; do
    idx=$((i % 8))
    # 用 : 分隔主题（主题内不含分号）
    topic=$(echo "$TOPICS" | cut -d'|' -f$((idx+1)))
    # topic 转 URL 编码
    topic_enc=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$topic")
    echo -n "  [$((i+1))/$count] "
    resp=$(curl -s --max-time 180 -X POST -H "Authorization: Bearer $TOKEN" "$B/ai/generate-guides?gameId=$game_id&count=1&topic=$topic_enc")
    echo "$resp" | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    if d.get('code')!=0: print('❌ '+str(d.get('message')), flush=True)
    else: print('✅ '+d['data'][0]['title'][:45], flush=True)
except: print('⚠️ 响应解析失败', flush=True)"
    sleep 3
    i=$((i+1))
  done
done
echo "批量生成完成"