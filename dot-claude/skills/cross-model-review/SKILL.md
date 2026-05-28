# Skill: 跨模型代码审查

## 触发条件
用户说"让 GPT 审查这段代码"、"多模型审查"、"交叉审查"或类似表述。

## 前置条件
- `scripts/model-router.sh` 存在（已集成 Ai头号玩家 统一 API）
- GPT/Claude/Gemini 使用统一 API Key，DeepSeek 需设置 `DEEPSEEK_API_KEY`

## 执行步骤

### 1. 收集代码上下文
将要审查的代码差异或文件路径收集为临时文件。

### 2. 并行分发审查
使用后台 Bash 并行调用不同模型进行审查：

```bash
# 示例 - 并行发起到三个模型
echo "$CODE_DIFF" | ./scripts/model-router.sh gpt5 &
echo "$CODE_DIFF" | ./scripts/model-router.sh gemini3 &
echo "$CODE_DIFF" | ./scripts/model-router.sh deepseek &
wait
```

### 3. 汇总对比
收集各模型审查结果，按以下维度对比：
- 安全问题发现数量
- 性能建议
- 代码风格意见
- 误报/漏报分析

### 4. 生成综合报告
输出包含：
- 各模型独立审查结果
- 交叉验证发现：所有模型一致同意的风险（高置信度）
- 分歧点分析：哪个模型在哪些维度更准确
