# Codex 的 GPT Image 2 插件

这是一个可安装的 Codex 插件，用于调用 GPT Image 2 生成和修图。插件包含 `gpt-image-2` Skill，以及一个安全的本地包装脚本：它从当前 Codex provider 配置中读取 API key 和可选的 `base_url`，不会打印或保存密钥。

[English README](README.md)

## 功能

- 使用 GPT Image 2 文生图。
- 使用一张或多张参考图进行修图和合成。
- 使用带 alpha 通道的 PNG mask 做局部修改，也支持为方形图片生成圆环 mask。
- 支持用途、风格、构图和约束等提示词辅助参数。
- 通过 `--dry-run` 在真正请求接口前检查命令和 payload。
- 不内置密钥，也不会把 Codex 会话 bearer token 当作图片 API key 使用。

## 从 GitHub 安装

```bash
codex plugin marketplace add zlsbksdxl/gpt-image-2-skill-codex-gpt --ref main
codex plugin add gpt-image-2-codex@gpt-image-2-skill-codex-gpt
```

安装后重启 Codex 或新建任务。可以显式输入 `$gpt-image-2`，也可以直接描述画图或修图需求。

## 本地开发目录

本仓库的本地副本位于：

```text
/Users/starfall/Project/gpt-image-2-skill-codex-gpt
```

直接从本地源码做无网络 dry-run：

```bash
cd /Users/starfall/Project/gpt-image-2-skill-codex-gpt
python3 plugins/gpt-image-2-codex/skills/gpt-image-2/scripts/image.py generate \
  --prompt "一张干净的建筑方案可视化图" \
  --out outputs/architecture.png \
  --dry-run
```

## 配置

包装脚本会读取 `~/.codex/config.toml` 中的当前 provider：

```toml
model_provider = "OpenAI"

[model_providers.OpenAI]
OPENAI_API_KEY = "your-image-api-key"
base_url = "https://api.openai.com/v1"
```

也可以使用环境变量 `OPENAI_API_KEY` 和 `OPENAI_BASE_URL`。`base_url` 可以是 OpenAI 兼容的中转地址。脚本不会读取或复用 `experimental_bearer_token`。

本机需要存在 Codex 的 ImageGen runtime：`~/.codex/skills/.system/imagegen/scripts/image_gen.py`。如果路径不同，可以通过 `--image-gen` 指定。

## 生成图片

```bash
python3 plugins/gpt-image-2-codex/skills/gpt-image-2/scripts/image.py generate \
  --prompt "白色工作室背景中的陶瓷杯产品摄影" \
  --out outputs/mug.png \
  --quality high \
  --size 1024x1024 \
  --force
```

可选参数包括 `--use-case`、`--style`、`--composition`、`--constraints` 和 `--dry-run`。

## 修图

```bash
python3 plugins/gpt-image-2-codex/skills/gpt-image-2/scripts/image.py edit \
  --image work/input.png \
  --prompt "只修改背景。严格保留主体的形状、姿态、比例、颜色、光照和细节。" \
  --out outputs/edited.png \
  --quality high \
  --size 1024x1024 \
  --force
```

多张参考图可以重复使用 `--image`。局部修改使用带 alpha 的 PNG mask：透明区域允许修改，不透明区域保留。方形图片可以用 `--mask-ring` 自动生成圆环 mask。

## 限制

- 通过此工作流调用 GPT Image 2 时不能直接承诺原生透明背景。需要透明背景时，先生成纯色或色键背景，再在本地抠图。
- 修图模型可能重新解释需要保护的内容；涉及严格保持时，应使用明确的保留要求和 mask。
- 画图和修图会产生配置 provider 对应的 API 费用。新环境建议先执行 `--dry-run`。

## 许可证

MIT，详见 [LICENSE](LICENSE)。
