# 请求检视

**AstrBot 插件** — 在所有其他插件完成注入后，打印发给模型的完整请求构成，用于排查 token 异常或 prompt 注入问题。

## 功能

- 以 `priority=-2000` 在所有钩子中最后执行，看到的是发给模型的最终状态
- 两种输出模式：
  - `summary`（默认）：每轮打印一行，显示 `system_prompt` / `prompt` / `contexts` 的字符数
  - `full`：打印每个字段的完整文本内容
- 在 AstrBot 面板中启用/禁用即可控制是否输出，不影响任何其他插件

## 配置

在 AstrBot 的 Web 后台配置输出模式：

| 字段 | 说明 |
|------|------|
| **output_mode** | `summary`：只打印字符数；`full`：打印完整内容 |

## 日志示例

**summary 模式：**

```
[Noir:FriendMessage:xxxxx] 请求检视: system_prompt=263字 | prompt=4788字 | contexts=0条/0字
```

**full 模式：**

```
[Noir:FriendMessage:xxxxx] 请求检视 [FULL] ============================================================
[Noir:FriendMessage:xxxxx] 请求检视 [system_prompt] (263字):
...
[Noir:FriendMessage:xxxxx] 请求检视 [prompt] (4788字):
...
[Noir:FriendMessage:xxxxx] 请求检视 [contexts] 空
[Noir:FriendMessage:xxxxx] 请求检视 [END] ============================================================
```

## 安装

将 `request_inspector` 文件夹放入 AstrBot 的插件目录，重启 AstrBot 即可。

## 文件结构

```
request_inspector/
├── main.py             # 插件主体
├── metadata.yaml       # AstrBot 插件元数据
├── _conf_schema.json   # 配置项定义
└── README.md           # 本文件
```

## 作者

Felis Abyssalis

## 许可证

F(A) = A(F)
