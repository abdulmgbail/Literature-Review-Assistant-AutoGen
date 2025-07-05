# 📚 Literature Review Service

A powerful Python service that bridges AutoGen multi-agent systems with Streamlit frontends to conduct automated literature reviews. This service provides a clean, user-friendly interface for academic research by filtering out technical details and presenting polished literature reviews.

## 🌟 Features

- **Multi-Agent Literature Review**: Leverages AutoGen's multi-agent framework for comprehensive paper analysis
- **Real-time Progress Tracking**: Live updates during the review process
- **Clean Output Filtering**: Automatically removes function calls, raw data, and technical noise
- **Duplicate Content Detection**: Intelligent deduplication of results
- **Flexible Configuration**: Customizable search parameters and model selection
- **Error Handling**: Robust error management with graceful fallbacks
- **Streamlit Integration**: Seamless integration with Streamlit web applications

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│  Streamlit UI   │◄──►│ Literature Review    │◄──►│  AutoGen Team   │
│                 │    │      Service         │    │                 │
│ • User Input    │    │ • Message Filtering  │    │ • ArXiv Search  │
│ • Progress Bar  │    │ • Content Cleaning   │    │ • Paper Analysis│
│ • Results View  │    │ • Progress Tracking  │    │ • Review Writing│
└─────────────────┘    └──────────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

```bash
pip install streamlit
pip install autogen
# Add other dependencies as needed
```

## 📋 Configuration Options

| Parameter     | Type | Default                  | Description                               |
| ------------- | ---- | ------------------------ | ----------------------------------------- |
| `topic`       | str  | Required                 | Research topic for literature review      |
| `max_results` | int  | 5                        | Maximum number of papers to analyze       |
| `model_name`  | str  | "deepseek/deepseek-chat" | LLM model for analysis                    |
| `max_turns`   | int  | 2                        | Maximum conversation turns between agents |
| `api_key`     | str  | None                     | OpenAI Router API key                     |

## 🧠 How It Works

### 1. **Message Processing Pipeline**

- Extracts content from AutoGen message objects
- Filters out function calls and raw JSON data
- Removes duplicate content
- Extracts final formatted literature review

### 2. **Content Filtering**

The service automatically removes:

- `[FunctionCall(...)]` messages
- `[FunctionExecutionResult(...)]` outputs
- Raw JSON paper data
- Duplicate sections
- Technical debugging information

### 3. **Progress Tracking**

- **Initializing** (10%): Setting up AutoGen agents
- **Searching** (25%): Querying ArXiv for papers
- **Analyzing** (60%): Processing paper content
- **Summarizing** (80%): Generating final review
- **Completed** (100%): Review ready

## 📊 Example Output

**Input**: "RAG systems in conversational AI"

**Output**:

```markdown
Literature Review: RAG Systems in Conversational AI

Recent research focuses on making RAG systems more modular, diverse, and domain-specific. Below are three key papers addressing these challenges.

## Key Papers

### Modular RAG: Transforming RAG Systems into LEGO-like Reconfigurable Frameworks

**Authors**: Yunfan Gao, Yun Xiong, Meng Wang, Haofen Wang

**Problem**: The complexity of RAG systems increases as new retrievers, LLMs, and complementary technologies are integrated...

**Contributions**: Introduces a modular RAG framework that decomposes RAG into independent modules...

[Additional papers and analysis...]

## Key Insights

- Graph RAG shows superior performance in reasoning-heavy tasks
- Modular approaches enable flexible RAG architectures
- Domain-specific optimizations are crucial for production systems
```

## 📁 Project Structure

```
literature-review-service/
├── literature_review_service.py   # Main service code
├── agent_backend.py              # AutoGen team configuration
├── streamlit_app.py              # Streamlit frontend
├── requirements.txt              # Dependencies
├── README.md                     # This file
└── examples/
    ├── basic_usage.py
    ├── streamlit_integration.py
    └── custom_filtering.py
```

## 🔑 Environment Setup

Create a `.env` file:

```env
OPENAI_ROUTER_API_KEY=your_api_key_here
```

Or use Streamlit secrets:

```toml
# .streamlit/secrets.toml
OPENAI_ROUTER_API_KEY = "your_api_key_here"
```

## 🐛 Troubleshooting

### Common Issues

1. **Empty Results**: Check if AutoGen backend is returning proper message objects
2. **Duplicate Content**: Ensure `clean_content()` method is working correctly
3. **Function Calls Showing**: Verify filtering patterns in `is_function_call_message()`
4. **API Errors**: Check API key configuration and model availability

## 🙏 Acknowledgments

- **AutoGen**: For the powerful multi-agent framework
- **ArXiv**: For providing access to academic papers
- **Streamlit**: For the excellent web app framework
- **OpenAI Router**: For model access and routing

**Made with Streamlit, AutoGen**
