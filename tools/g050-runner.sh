#!/usr/bin/env bash
# g050-runner.sh —— g050 fail-before 红复现运行器（quality/contract.yaml g050.runner-cmd 指向本文件）
# 用法：g050-runner.sh --root <测试 commit worktree> <NEW_TESTS...>
# 语义：在测试 commit 的 worktree 上只复跑“该提交时已存在”的 TS 驱动测试
#   （tests/card/**/*.test.ts）；.py 测试不参与机器红复现——质量关卡 job 无
#   python 包环境，红复现由 TS 驱动经 child_process 驱动真实 Python 实现完成，
#   红必须是断言失败（g050 签名判定不改）。
# 调用 cwd 固定为仓根（g050 壳以 (cd ROOT && bash tools/g050-runner.sh --root WT ...) 执行），
# 故本文件在实现 commit 之后才入库也不影响对早期测试 commit 的红复现。
set -u

root=""
args=()
while (($#)); do
  case "$1" in
    --root)
      root="$2"
      shift 2
      ;;
    *)
      args+=("$1")
      shift
      ;;
  esac
done

if [[ -z "$root" || ! -d "$root" ]]; then
  echo "g050-runner: 无效 --root '$root'" >&2
  exit 2
fi
cd "$root" || exit 2

ts=()
for f in "${args[@]}"; do
  if [[ "$f" == *.test.ts && -f "$f" ]]; then
    ts+=("$f")
  fi
done

if ((${#ts[@]})); then
  npx vitest run "${ts[@]}"
  exit $?
fi

echo "g050-runner: worktree 中无本次新增的 TS 驱动测试——无红可复现（.py 测试不参与机器红复现）"
exit 0