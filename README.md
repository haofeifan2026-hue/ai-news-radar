# Codex 与 Obsidian 使用技巧

本目录同时包含一个面向 AI 自学与内容创作的资讯雷达：定时收集 GitHub、Reddit、RSS，以及可选的 X/Twitter RSS 桥接内容，并以 Obsidian Markdown 写入 `inbox/ai-radar`。

## 内容方向

- 使用 Codex 辅助整理和维护 Obsidian 笔记
- 为笔记库设计清晰的目录与标签体系
- 利用模板提升日常记录效率
- 通过自动化完成归档、链接检查和内容整理
- Codex 与 Obsidian 协作时的安全和版本管理建议

## 快速启用

1. 将本目录放进你的 GitHub 仓库，并启用 Actions 的读写权限。
2. 编辑 `config.yaml`，补充你关心的仓库、Reddit 社区和 RSS。
3. 在仓库 `Settings → Secrets and variables → Actions` 中按需添加 `OPENAI_API_KEY` 或 `GITHUB_TOKEN`。不要把密钥写入文件。
4. 在 Actions 中手动运行“AI资讯雷达”，确认生成 `inbox/ai-radar/YYYY-MM-DD.md`。

## 关于 X/Twitter

X/Twitter 没有稳定、免费的公开 RSS 接口。推荐先使用 RSSHub/Nitter 等你信任的 RSS 桥接服务，把地址填入 `config.yaml` 的 `x.rss_urls` 并设置 `enabled: true`；如果你有官方 X API Bearer Token，再单独接入 API 采集。

## 内容工作流

每天生成的 Markdown 可以直接被 Obsidian 打开。建议在发布前用 Codex 做二次筛选：事实核验、去重、提炼成“发生了什么 / 为什么重要 / 我能怎么用 / 可变现方向”四段式笔记。
