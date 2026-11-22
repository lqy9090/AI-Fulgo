# AI-Fulgo: Week 1 - 第一次调用 LLM

本项目是 AI 大模型开发学习路径 **Week 1** 的实践成果。项目构建了一个支持多轮对话、流式输出、持久化存储以及超时与异常处理的交互式 AI CLI 工具。

---

## 目录
- [第一周目标验收](#第一周目标验收)
- [核心知识点总结](#核心知识点总结)
  - [1. 什么是 LLM？它和传统程序有什么区别？](#1-什么是-llm它和传统程序有什么区别)
  - [2. 什么是 Token 与 Context Window？](#2-什么是-token-与-context-window)
  - [3. Temperature 与 Max Output Tokens](#3-temperature-与-max-output-tokens)
  - [4. Prompt 的基本结构](#4-prompt-的基本结构)
  - [5. API 调用与 Streaming（流式传输）](#5-api-调用与-streaming流式传输)
- [项目架构与功能](#项目架构与功能)
- [快速开始](#快速开始)
- [测试验证](#测试验证)

---

## 第一周目标验收

| 需求项 | 达成状态 | 实现方式 |
| :--- | :---: | :--- |
| **调用 LLM API** | ✅ 已达成 | 基于 Anthropic SDK，配合 LiteLLM 网关或官方接口调用 |
| **支持 Streaming** | ✅ 已达成 | 使用 `client.messages.stream` 与 `stream.text_stream` 实时逐字输出 |
| **保存对话记录** | ✅ 已达成 | 双格式持久化：`.json`（结构化元数据）+ `.md`（排版良好的聊天日志） |
| **处理 API Timeout 和 Error** | ✅ 已达成 | 针对 `APITimeoutError`、`APIConnectionError`、401/429/400 精细化处理，并带异常回滚机制 |
| **支持多轮对话** | ✅ 已达成 | 交互式 CLI 终端交互，在 `ChatSession` 中动态维护上下文全量消息 |

---

## 核心知识点总结

### 1. 什么是 LLM？它和传统程序有什么区别？
- **LLM（大语言模型，Large Language Model）**：基于海量文本自监督预训练出的深度学习模型，本质是一个概率语言模型。其核心能力是**根据当前给定的上文（Context），预测最可能跟随的下一个词（Token）**。
- **与传统程序的对比**：
  - **传统程序**：基于确定性算法和控制流（`if/else`、状态机），输入与输出是因果确定的，对语法格式要求严苛。
  - **LLM**：基于神经网络概率推理，对模糊、非结构化的自然语言具有极强的语义理解、常识推理与内容生成能力。

### 2. 什么是 Token 与 Context Window？
- **Token（令牌/标记）**：
  - 模型无法直接处理字符串字符，文本会经过分词器（Tokenizer）切分为 Token 并转换为数值向量。
  - 通常 1 个英文单词约为 1~2 个 Tokens，1 个常用汉字约为 1~2 个 Tokens。
- **Context Window（上下文窗口）**：
  - 模型单次请求中能处理的最大 Token 数量（包括传入的提示词 + 生成的回答）。
  - LLM 服务是**无状态（Stateless）**的，多轮对话中能够“记住前文”依靠的是客户端每次将历史对话全量打包传递。历史消息越长，占用的上下文窗口越多。

### 3. Temperature 与 Max Output Tokens
- **Max Output Tokens（最大输出限制）**：
  - 限制模型单次生成的最大 Token 数量，避免无限生成或额度失控。
- **Temperature（采样温度）**：
  - 控制输出词概率分布的平滑程度：
    - `Temperature -> 0`：几乎只选概率最高的词，输出确定、严谨，适合代码编写、格式提取与数学推理。
    - `Temperature -> 1`：增加低概率词的选择机会，输出更富创造力、多样性，适合文学创作与构思方案。

### 4. Prompt 的基本结构
主流大模型通常采用 **Role-based Messages** 体系：
- **System Prompt**：全局指导规则、角色设定与安全边界。
- **User Message**：用户的具体提问、指令或输入数据。
- **Assistant Message**：模型的回复。多轮对话中 User 与 Assistant 交替排列，构成完整记忆上下文。

### 5. API 调用与 Streaming（流式传输）
- **阻塞调用（Non-streaming）**：客户端等待服务器全部计算完毕后一次性返回，首字延迟（TTFT）较长。
- **流式传输（Streaming）**：基于 SSE（Server-Sent Events）长连接机制，服务端每生成一个或数个 Token 便立即推送到客户端，客户端实时渲染，带来打字机般的流畅交互体验。

---

## 项目架构与功能

```
AI-Fulgo/
├── RequestAPI.py           # 主程序：交互式 CLI 终端、流式输出、超时与异常捕获
├── chat_storage.py         # 存储管理器：维护消息上下文、持久化为 JSON 与 Markdown
├── test_chat_storage.py    # 存储功能单元测试
├── test_error_handling.py  # 异常处理与上下文回滚测试
├── .env.example            # 环境变量配置模板
└── .gitignore              # 忽略敏感信息（.env）与对话历史（chat_histories/）
```

---

## 快速开始

### 1. 安装依赖
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install anthropic python-dotenv
```

### 2. 配置环境变量
复制 `.env.example` 为 `.env` 并填写对应配置：
```bash
cp .env.example .env
```
`.env` 内容示例：
```ini
LITELLM_MASTER_KEY=your_api_key_here
ANTHROPIC_BASE_URL=http://127.0.0.1:4011
ANTHROPIC_MODEL=claude-opus-4-6
REQUEST_TIMEOUT=30.0
```

### 3. 运行交互式聊天
```bash
python RequestAPI.py
```
- 输入任意内容与 AI 进行多轮对话。
- 输入 `exit`、`quit` 或 `q` 退出。
- 退出后，对话记录将自动保存在 `chat_histories/` 目录中：
  - `chat_histories/{session_id}.json`（结构化数据）
  - `chat_histories/{session_id}.md`（Markdown 排版）

---

## 测试验证

运行项目单元测试验证存储与错误处理逻辑：
```bash
python test_chat_storage.py
python test_error_handling.py
```
