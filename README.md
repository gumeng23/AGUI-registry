# AGUI Registry

Agui 包的中央索引。`agui install <包名>[@版本]` 默认读取：

```text
https://raw.githubusercontent.com/gumeng23/AGUI-registry/main/index.json
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

1. 在 `packages/src/<name>/` 准备 `agui-package.json` 和 `.ag` 文件。
2. 打包：

```powershell
Compress-Archive -Path packages/src/mathx/* -DestinationPath packages/mathx-0.1.0.zip -Force
```

3. 计算 SHA-256：

```powershell
(Get-FileHash packages/mathx-0.1.0.zip -Algorithm SHA256).Hash.ToLower()
```

4. 在 `index.json` 添加版本，提交并推送。
5. 用户安装：

```powershell
agui install mathx
agui install mathx@0.1.0
```

也可以指定索引：

```powershell
agui install mathx --registry https://example.com/index.json
```

## 当前包

| 包 | 版本 | 说明 |
| --- | --- | --- |
| mathx | 0.1.0 | `clamp`、`lerp`、`round_to` |
