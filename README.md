# AGUI Registry

Agui 包的中央索引。`agui install <包名>[@版本]` 默认读取：

```text
https://api.github.com/repos/gumeng23/AGUI-registry/contents/index.json
```

## 目录

```text
index.json                     包索引
packages/<name>-<version>.zip  包归档
packages/src/<name>/           归档源文件（便于审阅）
```

## index.json

```json
{
  "version": 1,
  "packages": {
    "mathx": {
      "description": "数学辅助库",
      "latest": "0.1.0",
      "versions": {
        "0.1.0": {
          "url": "https://raw.githubusercontent.com/gumeng23/AGUI-registry/main/packages/mathx-0.1.0.zip",
          "sha256": "<zip 的 SHA-256>",
          "entry": "mathx.ag",
          "dependencies": {}
        }
      }
    }
  }
}
```

- `version` 目前固定为 `1`。
- `latest` 省略时，客户端选择语义版本最高的版本。
- `sha256` 必填，下载后会强制校验。
- `entry` 是包内入口文件，默认 `<name>.ag`。
- `dependencies` 是 `包名 -> 版本约束`，支持 `^`、`~`、`>=`、精确版本、`latest`/`*`。

## 包 zip 布局

```text
mathx-0.1.0.zip
├── agui-package.json
└── mathx.ag
```

`agui-package.json`：

```json
{
  "name": "mathx",
  "version": "0.1.0",
  "description": "数学辅助库",
  "entry": "mathx.ag",
  "dependencies": {},
  "agui": ">=0.9.2"
}
```

要求：

- 包名、版本必须与索引一致。
- 入口文件必须在 zip 内，路径不能越出包目录。
- 不支持 zip 顶层再套一层目录；请把文件放在 zip 根目录。
- 单个 zip 上限 64 MB。

## 发布新包

外部作者不需要仓库写权限，走 fork + Pull Request：

1. 在 GitHub fork `gumeng23/AGUI-registry`，克隆自己的 fork。
2. 新建分支，例如 `add-<name>`。
3. 在 `packages/src/<name>/` 准备 `agui-package.json` 和 `.ag` 文件。
2. 打包：

```powershell
Compress-Archive -Path packages/src/mathx/* -DestinationPath packages/mathx-0.1.0.zip -Force
```

3. 计算 SHA-256：

```powershell
(Get-FileHash packages/mathx-0.1.0.zip -Algorithm SHA256).Hash.ToLower()
```

4. 在 `index.json` 添加版本，提交并推送到自己的 fork。
5. 在 GitHub 向 `gumeng23/AGUI-registry` 的 `main` 分支发起 Pull Request。
6. 维护者合并后，用户即可安装：

```powershell
agui install mathx
agui install mathx@0.1.0
```

也可以指定索引：

```powershell
agui install mathx --registry https://example.com/index.json
```

## 自动校验与自动合并

- 每个 PR 会自动运行 `Validate registry`：检查 `index.json`、zip 是否存在、SHA-256、`agui-package.json`、入口文件和路径越界。
- 维护者给 PR 添加 `automerge` 标签后，校验通过时 `Auto merge` 工作流会执行 squash merge 并删除分支。
- 仓库已开启 `Allow auto-merge`；如果校验失败，自动合并不会发生。
- 外部贡献者不能自行添加标签，自动合并仍由维护者逐个授权。

对应 workflow：

```text
.github/workflows/validate.yml
.github/workflows/automerge.yml
```

本地也可以先跑：

```powershell
python scripts/validate_registry.py
```

## 当前包

| 包 | 版本 | 说明 |
| --- | --- | --- |
| mathx | 0.1.0 | `clamp`、`lerp`、`round_to` |
