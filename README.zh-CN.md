# Codex Image Plugin

这是一个公开的 Codex 插件，通过任意兼容 OpenAI Image API 的接口进行画图和修图。你可以输入接口 URL、API key 和模型 ID，插件会原样调用指定模型，不绑定某一家服务商或某一个固定模型。

[English README](README.md)

## 功能

- 使用任意兼容接口提供的模型生成图片。
- 使用一张或多张参考图修图，并支持 alpha PNG mask。
- 查询接口暴露的模型列表。
- 在接口暴露的画图模型中查询并选择一个模型。
- 支持命令行参数、环境变量和 Codex 当前 provider 配置。
- 不打印或保存 API key，也不会使用 Codex 会话 bearer token。

## 从 GitHub 安装

```bash
codex plugin marketplace add zlsbksdxl/codex-image-plugin --ref main
codex plugin add codex-image-plugin@codex-image-plugin
```

安装后重启 Codex 或新建任务，并使用 `$codex-image-plugin` 调用 Skill。

## 本地开发目录

```bash
cd /Users/starfall/Project/codex-image-plugin
python3 plugins/codex-image-plugin/skills/codex-image-plugin/scripts/image.py \
  models \
  --base-url "https://api.example.com/v1" \
  --api-key "$OPENAI_API_KEY" \
  --image-only
```

建议通过环境变量传入 key，避免出现在 shell 历史记录中。脚本也会读取 `OPENAI_BASE_URL`、`OPENAI_API_KEY` 和 `~/.codex/config.toml` 中的当前 provider。

## 使用指定模型画图

```bash
python3 plugins/codex-image-plugin/skills/codex-image-plugin/scripts/image.py \
  generate \
  --base-url "https://api.example.com/v1" \
  --api-key "$OPENAI_API_KEY" \
  --model "gpt-image-2" \
  --prompt "白色工作室背景中的陶瓷杯产品摄影" \
  --out outputs/mug.png \
  --quality high \
  --size 1024x1024 \
  --force
```

`gpt-image-2` 只是示例。请使用 `models` 返回的 ID 或接口文档中的模型名，包装脚本不会把模型写死。

## 修图

```bash
python3 plugins/codex-image-plugin/skills/codex-image-plugin/scripts/image.py \
  edit \
  --base-url "https://api.example.com/v1" \
  --api-key "$OPENAI_API_KEY" \
  --model "gpt-image-2" \
  --image work/input.png \
  --prompt "只修改背景，严格保留主体的形状、姿态、比例、颜色、光照和细节。" \
  --out outputs/edited.png \
  --force
```

多张参考图可以重复使用 `--image`。局部编辑使用 `--mask mask.png`；方形图片可以用 `--mask-ring` 生成外圈 mask。

## Dry-run 和配置

给 `models`、`generate` 或 `edit` 添加 `--dry-run`，可以只检查 endpoint 和 payload，不发起 API 请求。尺寸、质量、mask、格式和透明背景等限制由具体接口决定，接口错误会直接返回。

## 许可证

MIT，详见 [LICENSE](LICENSE)。
