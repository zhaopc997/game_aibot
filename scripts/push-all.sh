#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# 双远程推送（Gitee + GitHub）
#
#   ./scripts/push-all.sh                 # 推送当前分支到两个远程
#   ./scripts/push-all.sh -m "提交信息"    # 先提交全部变更再推送
#   ./scripts/push-all.sh --verify        # 只核验两个远程的提交状态
#
# 背景：
#   本项目由两端协作开发，变更需同时同步到 Gitee 与 GitHub。
#   GitHub 在国内网络下经常出现：
#     · RPC failed; curl 18 Transferred a partial file
#     · curl 16 Error in the HTTP2 framing layer
#   这类错误多为网络抖动，重试通常即可成功。
#   本脚本对两个远程分别推送并带重试，避免"推了一个漏一个"。
#
# 注意：
#   origin 同时配置了两个 pushurl（Gitee + GitHub），
#   `git push origin main` 会依次推送，但**任一失败即整体报错**，
#   且不易判断到底哪个成功。故本脚本拆开单独推、单独校验。
# ═══════════════════════════════════════════════════════════════
set -uo pipefail

export LC_ALL=C
export LANG=C

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

REMOTES=(gitee github)
BRANCH="${BRANCH:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null)}"
MAX_RETRY="${MAX_RETRY:-3}"

log()  { printf "[push] %s\n" "$*"; }
ok()   { printf "[  ok  ] %s\n" "$*"; }
warn() { printf "[ warn ] %s\n" "$*"; }
die()  { printf "[ fail ] %s\n" "$*" >&2; exit 1; }

git rev-parse --git-dir >/dev/null 2>&1 || die "当前目录不是 git 仓库"
[[ -n "$BRANCH" ]] || die "无法确定当前分支"

# ───── 可选：提交 ─────
if [[ "${1:-}" == "--verify" ]]; then
  VERIFY_ONLY=1
else
  VERIFY_ONLY=0
fi

if [[ "${1:-}" == "-m" ]]; then
  MSG="${2:-}"
  [[ -n "$MSG" ]] || die "-m 后需要提交信息"
  git add -A || die "git add 失败"
  if git diff --cached --quiet; then
    warn "没有需要提交的变更"
  else
    git commit -q -m "$MSG" || die "git commit 失败"
    ok "已提交：$(git log -1 --format='%h %s')"
  fi
fi

# ───── 推送（带重试）─────
push_one() {
  local remote="$1" attempt=1
  while (( attempt <= MAX_RETRY )); do
    log "推送到 $remote（第 $attempt/$MAX_RETRY 次）…"
    if out=$(git push "$remote" "$BRANCH" 2>&1); then
      if grep -q "Everything up-to-date" <<<"$out"; then
        ok "$remote 已是最新"
      else
        ok "$remote 推送成功"
      fi
      return 0
    fi
    # 网络类错误才重试；其它错误（权限、冲突）直接失败
    if grep -qiE "RPC failed|curl 1[68]|HTTP2 framing|remote end hung up|Could not resolve|timed out" <<<"$out"; then
      warn "$remote 网络异常，$((attempt < MAX_RETRY ? 5 : 0)) 秒后重试"
      sleep 5
      attempt=$((attempt + 1))
      continue
    fi
    printf "%s\n" "$out" | tail -5 | sed 's/^/      /'
    return 1
  done
  warn "$remote 重试 $MAX_RETRY 次仍失败"
  return 1
}

FAILED=()
if [[ "$VERIFY_ONLY" -eq 0 ]]; then
  for r in "${REMOTES[@]}"; do
    push_one "$r" || FAILED+=("$r")
  done
fi

# ───── 校验：以远程实际 ref 为准 ─────
echo ""
log "校验各远程实际状态…"
LOCAL_SHA=$(git rev-parse HEAD)
ALL_OK=1
for r in "${REMOTES[@]}"; do
  sha=$(git ls-remote --heads "$r" "$BRANCH" 2>/dev/null | awk '{print $1}' | head -1)
  if [[ "$sha" == "$LOCAL_SHA" ]]; then
    ok "$r  = ${LOCAL_SHA:0:7}"
  elif [[ -z "$sha" ]]; then
    warn "$r  读取失败（网络问题，稍后用 --verify 复核）"
    ALL_OK=0
  else
    warn "$r  = ${sha:0:7}（落后于本地 ${LOCAL_SHA:0:7}）"
    ALL_OK=0
  fi
done

echo ""
if [[ "$ALL_OK" -eq 1 && ${#FAILED[@]} -eq 0 ]]; then
  ok "两个远程均已同步到 ${LOCAL_SHA:0:7}"
  exit 0
fi
die "存在未同步的远程：${FAILED[*]:-见上方提示}"
