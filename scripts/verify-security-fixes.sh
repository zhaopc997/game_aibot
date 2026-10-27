#!/usr/bin/env bash
# 渗透测试问题修复验证脚本
# 用法：BASE=https://helozero.com ./verify-security-fixes.sh
set -uo pipefail
BASE="${BASE:-https://helozero.com}"
TS=$(date +%s)
U="sectestfix${TS}"
P="SecTest!2026Aa"
J=/tmp/_vf.json

pass() { printf "  \033[32m✓\033[0m %s\n" "$1"; }
fail() { printf "  \033[31m✗\033[0m %s\n" "$1"; FAILED=1; }
FAILED=0
title() { printf "\n\033[1m%s\033[0m\n" "$1"; }
code() { curl -s -o "${J}" -w "%{http_code}" --max-time 25 "$@"; }
body() { head -c 200 "${J}" 2>/dev/null; }
msg()  { python3 -c "import json;print((json.load(open('${J}')).get('message') or '')[:60])" 2>/dev/null; }

# ─────────────────────────────────────────────
title "F-06 弱密码策略（12345678 应被拒绝）"
C=$(code -X POST "${BASE}/api/v1/auth/register" -H 'Content-Type: application/json' \
  -d "{\"username\":\"weak${TS}\",\"email\":\"weak${TS}@t.com\",\"password\":\"12345678\"}")
M=$(msg)
if [ "${C}" = "400" ] && echo "${M}" | grep -q "密码"; then
  pass "弱密码被拒 HTTP ${C} → ${M}"
else
  fail "弱密码未被拒：HTTP ${C} → ${M}"
fi

# ─────────────────────────────────────────────
title "F-06b 强密码应可注册（对照组）"
C=$(code -X POST "${BASE}/api/v1/auth/register" -H 'Content-Type: application/json' \
  -d "{\"username\":\"${U}\",\"email\":\"${U}@t.com\",\"password\":\"${P}\"}")
AT=$(python3 -c "import json;d=json.load(open('${J}'));print((d.get('data') or {}).get('accessToken',''))" 2>/dev/null)
RT=$(python3 -c "import json;d=json.load(open('${J}'));print((d.get('data') or {}).get('refreshToken',''))" 2>/dev/null)
if [ "${C}" = "200" ] && [ -n "${AT}" ]; then
  pass "强密码注册成功（${U}）"
else
  fail "强密码注册失败：HTTP ${C} → $(body)"
fi

# ─────────────────────────────────────────────
title "F-05 用户枚举（重复注册文案应统一）"
C1=$(code -X POST "${BASE}/api/v1/auth/register" -H 'Content-Type: application/json' \
  -d "{\"username\":\"${U}\",\"email\":\"other${TS}@t.com\",\"password\":\"${P}\"}")
M1=$(msg)
C2=$(code -X POST "${BASE}/api/v1/auth/register" -H 'Content-Type: application/json' \
  -d "{\"username\":\"othername${TS}\",\"email\":\"${U}@t.com\",\"password\":\"${P}\"}")
M2=$(msg)
if [ "${M1}" = "${M2}" ] && [ -n "${M1}" ]; then
  pass "用户名冲突与邮箱冲突文案一致：${M1}"
else
  fail "文案不一致：[${M1}] vs [${M2}]"
fi

# ─────────────────────────────────────────────
title "F-09 参数类型错误应返回 400（原为 500）"
C=$(code "${BASE}/api/v1/guides/abc")
if [ "${C}" = "400" ]; then pass "路径参数非法 → HTTP 400"; else fail "路径参数非法 → HTTP ${C}"; fi
C=$(code "${BASE}/api/v1/guides?size=abc")
if [ "${C}" = "400" ]; then pass "查询参数非法 → HTTP 400"; else fail "查询参数非法 → HTTP ${C}"; fi

# ─────────────────────────────────────────────
title "F-08 未实现端点应返回 404（原为 500）"
C=$(code "${BASE}/api/v1/qa" -H "Authorization: Bearer ${AT}")
if [ "${C}" = "404" ]; then pass "/api/v1/qa → HTTP 404"; else fail "/api/v1/qa → HTTP ${C}"; fi

# ─────────────────────────────────────────────
title "F-10 服务端拒绝 HTML 输入"
C=$(code -X POST "${BASE}/api/v1/questions" -H "Authorization: Bearer ${AT}" \
  -H 'Content-Type: application/json' \
  -d "{\"gameId\":1,\"title\":\"<img src=x onerror=alert(1)>\",\"description\":\"<script>alert(1)</script>\"}")
if [ "${C}" = "400" ]; then pass "含 HTML 标签的问题被拒 → HTTP 400"; else fail "含 HTML 标签仍被接收 → HTTP ${C}"; fi

# ─────────────────────────────────────────────
title "F-02 Refresh Token 轮换与复用检测"
C=$(code -X POST "${BASE}/api/v1/auth/refresh" -H 'Content-Type: application/json' \
  -d "{\"refreshToken\":\"${RT}\"}")
RT2=$(python3 -c "import json;d=json.load(open('${J}'));print((d.get('data') or {}).get('refreshToken',''))" 2>/dev/null)
if [ "${C}" = "200" ] && [ -n "${RT2}" ] && [ "${RT2}" != "${RT}" ]; then
  pass "首次刷新成功，且签发了新 Refresh Token（已轮换）"
else
  fail "刷新异常：HTTP ${C}"
fi
C=$(code -X POST "${BASE}/api/v1/auth/refresh" -H 'Content-Type: application/json' \
  -d "{\"refreshToken\":\"${RT}\"}")
if [ "${C}" = "401" ]; then
  pass "旧 Refresh Token 被复用 → 拒绝（HTTP 401，复用检测生效）"
else
  fail "旧 Refresh Token 仍可用 → HTTP ${C}（复用检测未生效）"
fi

# ─────────────────────────────────────────────
title "F-08b 登出接口应可用（原为 500）"
C=$(code -X POST "${BASE}/api/v1/auth/login" -H 'Content-Type: application/json' \
  -d "{\"username\":\"${U}\",\"password\":\"${P}\"}")
AT2=$(python3 -c "import json;d=json.load(open('${J}'));print((d.get('data') or {}).get('accessToken',''))" 2>/dev/null)
RT3=$(python3 -c "import json;d=json.load(open('${J}'));print((d.get('data') or {}).get('refreshToken',''))" 2>/dev/null)
C=$(code -X POST "${BASE}/api/v1/auth/logout" -H "Authorization: Bearer ${AT2}")
if [ "${C}" = "200" ]; then pass "POST /auth/logout → HTTP 200"; else fail "登出 → HTTP ${C}"; fi
C=$(code -X POST "${BASE}/api/v1/auth/refresh" -H 'Content-Type: application/json' \
  -d "{\"refreshToken\":\"${RT3}\"}")
if [ "${C}" = "401" ]; then pass "登出后旧 Refresh Token 立即失效 → HTTP 401"; else fail "登出后令牌仍可用 → HTTP ${C}"; fi

# ─────────────────────────────────────────────
title "F-01 登录限流与失败锁定（放最后，会消耗 IP 配额）"
LOCKED=0
for i in $(seq 1 12); do
  C=$(curl -s -o "${J}" -w "%{http_code}" --max-time 20 -X POST "${BASE}/api/v1/auth/login" \
    -H 'Content-Type: application/json' \
    -d "{\"username\":\"nosuchuser${TS}\",\"password\":\"wrong${i}\"}")
  if [ "${C}" = "429" ]; then
    M=$(msg); RA=$(curl -sI --max-time 10 -X POST "${BASE}/api/v1/auth/login" \
      -H 'Content-Type: application/json' -d '{"username":"x","password":"y"}' 2>/dev/null | grep -i retry-after | head -1)
    pass "第 ${i} 次失败登录被限流 → HTTP 429「${M}」"
    [ -n "${RA}" ] && pass "响应含 Retry-After 头"
    LOCKED=1
    break
  fi
done
[ "${LOCKED}" = "0" ] && fail "连续 12 次失败登录均未被拦截"

echo ""
if [ "${FAILED}" = "0" ]; then
  printf "\033[32m══ 全部通过 ══\033[0m\n"
else
  printf "\033[31m══ 存在未通过项 ══\033[0m\n"
fi
echo "测试账号：${U} （需清理）"
exit 0
