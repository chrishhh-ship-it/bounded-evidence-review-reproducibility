"""
ai_provider.py — 统一AI提供商注册中心 + 智能模型路由器

所有模块通过此文件访问AI能力，不再各自维护provider配置。
支持：DeepSeek / Kimi / Claude / OpenAI / Gemini / 通义千问 / 豆包 / Ollama
"""

from __future__ import annotations

import json
import time
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# 数据目录
# ─────────────────────────────────────────────────────────────
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# ─────────────────────────────────────────────────────────────
# Provider 注册表 — 所有支持的AI提供商
# ─────────────────────────────────────────────────────────────
PROVIDERS: Dict[str, dict] = {
    "deepseek": {
        "name": "DeepSeek",
        "icon": "🔭",
        "base_url": "https://api.deepseek.com/chat/completions",
        "default_model": "deepseek-chat",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "compat": "openai",          # API兼容类型
        "key_hint": "sk-... (api.deepseek.com)",
        "strengths": ["writing", "translation", "summarize", "coding"],
        "cost_tier": "low",          # low / medium / high
    },
    "kimi": {
        "name": "Kimi",
        "icon": "🌙",
        "base_url": "https://api.moonshot.cn/v1/chat/completions",
        "default_model": "moonshot-v1-32k",
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "compat": "openai",
        "key_hint": "sk-... (api.moonshot.cn)",
        "strengths": ["long_context", "summarize", "deep_read"],
        "cost_tier": "low",
    },
    "openai": {
        "name": "ChatGPT",
        "icon": "🤖",
        "base_url": "https://aiapi.world/v1/chat/completions",
        "default_model": "gpt-4o-mini",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        "compat": "openai",
        "key_hint": "sk-... (aiapi.world)",
        "strengths": ["deep_read", "gap_analysis", "brainstorm"],
        "cost_tier": "high",
    },
    "claude": {
        "name": "Claude",
        "icon": "🧠",
        "base_url": "https://api.anthropic.com/v1/messages",
        "default_model": "claude-sonnet-4-20250514",
        "models": [
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
        ],
        "compat": "anthropic",
        "key_hint": "sk-ant-... (anthropic.com)",
        "strengths": ["deep_read", "gap_analysis", "writing", "critic"],
        "cost_tier": "high",
    },
    "gemini": {
        "name": "Gemini",
        "icon": "✨",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        "default_model": "gemini-2.0-flash",
        "models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        "compat": "gemini",
        "key_hint": "AIza... (aistudio.google.com)",
        "strengths": ["brainstorm", "long_context", "summarize"],
        "cost_tier": "medium",
    },
    "qwen": {
        "name": "通义千问",
        "icon": "🌊",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "default_model": "qwen-turbo",
        "models": ["qwen-turbo", "qwen-plus", "qwen-max", "qwen2.5-72b-instruct"],
        "compat": "openai",
        "key_hint": "sk-... (dashscope.aliyuncs.com)",
        "strengths": ["writing", "translation", "summarize"],
        "cost_tier": "low",
    },
    "doubao": {
        "name": "豆包",
        "icon": "🫘",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "default_model": "",
        "models": [],
        "compat": "openai",
        "key_hint": "endpoint_id 填入模型字段",
        "strengths": ["summarize", "writing"],
        "cost_tier": "low",
    },
    "ollama": {
        "name": "Ollama (本地)",
        "icon": "🏠",
        "base_url": "http://localhost:11434/api/chat",
        "default_model": "qwen2.5:7b",
        "models": ["qwen2.5:7b", "qwen2.5:14b", "llama3.1:8b", "deepseek-r1:8b",
                    "nomic-embed-text"],
        "compat": "ollama",
        "key_hint": "无需Key，本地运行",
        "strengths": ["summarize", "writing", "embedding"],
        "cost_tier": "free",
    },
    "siliconflow": {
        "name": "SiliconFlow",
        "icon": "⚡",
        "base_url": "https://api.siliconflow.cn/v1/chat/completions",
        "default_model": "deepseek-ai/DeepSeek-V3",
        "models": [
            "deepseek-ai/DeepSeek-V3",
            "Qwen/Qwen2.5-72B-Instruct",
            "THUDM/glm-4-9b-chat",
        ],
        "compat": "openai",
        "key_hint": "sk-... (siliconflow.cn)",
        "strengths": ["summarize", "writing", "translation"],
        "cost_tier": "low",
    },
}


# ─────────────────────────────────────────────────────────────
# 调用结果记录
# ─────────────────────────────────────────────────────────────
@dataclass
class CallRecord:
    provider: str = ""
    model: str = ""
    task_type: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    success: bool = True
    error: str = ""
    timestamp: str = ""


# ─────────────────────────────────────────────────────────────
# 统一调用接口
# ─────────────────────────────────────────────────────────────
def call_provider(
    provider_id: str,
    api_key: str,
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    max_tokens: int = 2000,
    temperature: float = 0.7,
    timeout: int = 60,
) -> Tuple[str, Optional[dict]]:
    """
    统一调用任意 provider 的 chat API。

    返回: (content_text, usage_dict_or_None)
    """
    import requests as _req

    prov = PROVIDERS.get(provider_id)
    if not prov:
        raise ValueError(f"未知 provider: {provider_id}")

    compat = prov["compat"]
    use_model = model or prov["default_model"]
    base_url = prov["base_url"]

    # ── OpenAI 兼容 ──
    if compat == "openai":
        return _call_openai_compat(
            _req, base_url, api_key, use_model, messages,
            max_tokens, temperature, timeout
        )
    # ── Anthropic ──
    elif compat == "anthropic":
        return _call_anthropic(
            _req, base_url, api_key, use_model, messages,
            max_tokens, temperature, timeout
        )
    # ── Gemini ──
    elif compat == "gemini":
        return _call_gemini(
            _req, base_url, api_key, use_model, messages,
            max_tokens, temperature, timeout
        )
    # ── Ollama ──
    elif compat == "ollama":
        return _call_ollama(
            _req, base_url, use_model, messages,
            max_tokens, temperature, timeout
        )
    else:
        raise ValueError(f"未知兼容类型: {compat}")


def _call_openai_compat(req, url, key, model, messages, max_tokens, temp, timeout):
    """OpenAI 兼容格式（DeepSeek/Kimi/OpenAI/Qwen/豆包/SiliconFlow）"""
    import time as _time
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temp,
    }
    # 429 智能退避重试（最多3次，指数退避 5s/15s/30s）
    for attempt in range(3):
        resp = req.post(url, json=payload, headers=headers, timeout=timeout)
        if resp.status_code == 429:
            wait = [5, 15, 30][attempt]
            logger.warning(f"[{model}] 429 限流，等待 {wait}s 后重试 ({attempt+1}/3)")
            _time.sleep(wait)
            continue
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        usage = {
            "input_tokens": data.get("usage", {}).get("prompt_tokens", 0),
            "output_tokens": data.get("usage", {}).get("completion_tokens", 0),
            "total_tokens": data.get("usage", {}).get("total_tokens", 0),
        }
        return content, usage
    # 3次都429，抛出异常
    resp.raise_for_status()


def _call_anthropic(req, url, key, model, messages, max_tokens, temp, timeout):
    """Anthropic Claude 格式"""
    # 提取 system message
    system_text = ""
    chat_messages = []
    for m in messages:
        if m["role"] == "system":
            system_text += m["content"] + "\n"
        else:
            chat_messages.append(m)
    if not chat_messages:
        chat_messages = [{"role": "user", "content": system_text.strip()}]
        system_text = ""

    headers = {
        "Content-Type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": model,
        "messages": chat_messages,
        "max_tokens": max_tokens,
        "temperature": temp,
    }
    if system_text.strip():
        payload["system"] = system_text.strip()

    import time as _time
    for attempt in range(3):
        resp = req.post(url, json=payload, headers=headers, timeout=timeout)
        if resp.status_code == 429:
            wait = [5, 15, 30][attempt]
            logger.warning(f"[{model}] 429 限流，等待 {wait}s 后重试 ({attempt+1}/3)")
            _time.sleep(wait)
            continue
        resp.raise_for_status()
        data = resp.json()
        content = data["content"][0]["text"]
        usage = {
            "input_tokens": data.get("usage", {}).get("input_tokens", 0),
            "output_tokens": data.get("usage", {}).get("output_tokens", 0),
            "total_tokens": (
                data.get("usage", {}).get("input_tokens", 0)
                + data.get("usage", {}).get("output_tokens", 0)
            ),
        }
        return content, usage
    resp.raise_for_status()


def _call_gemini(req, url_template, key, model, messages, max_tokens, temp, timeout):
    """Google Gemini 格式"""
    url = url_template.replace("{model}", model) + f"?key={key}"
    # 转换 messages → Gemini contents 格式
    contents = []
    for m in messages:
        role = "user" if m["role"] in ("user", "system") else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    payload = {
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temp,
        },
    }
    import time as _time
    for attempt in range(3):
        resp = req.post(url, json=payload, timeout=timeout)
        if resp.status_code == 429:
            wait = [5, 15, 30][attempt]
            logger.warning(f"[{model}] 429 限流，等待 {wait}s 后重试 ({attempt+1}/3)")
            _time.sleep(wait)
            continue
        resp.raise_for_status()
        data = resp.json()
        content = data["candidates"][0]["content"]["parts"][0]["text"]
        usage_meta = data.get("usageMetadata", {})
        usage = {
            "input_tokens": usage_meta.get("promptTokenCount", 0),
            "output_tokens": usage_meta.get("candidatesTokenCount", 0),
            "total_tokens": usage_meta.get("totalTokenCount", 0),
        }
        return content, usage
    resp.raise_for_status()


def _call_ollama(req, url, model, messages, max_tokens, temp, timeout):
    """Ollama 本地模型格式"""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temp,
        },
    }
    resp = req.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    content = data.get("message", {}).get("content", "")
    usage = {
        "input_tokens": data.get("prompt_eval_count", 0),
        "output_tokens": data.get("eval_count", 0),
        "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
    }
    return content, usage


# ─────────────────────────────────────────────────────────────
# 智能模型路由器
# ─────────────────────────────────────────────────────────────
class ModelRouter:
    """
    根据任务类型自动选择最佳可用模型。

    使用方式：
        router = ModelRouter(api_keys={"deepseek": "sk-...", "kimi": "sk-..."})
        provider_id, model = router.route("deep_read")
        content, usage = call_provider(provider_id, router.get_key(provider_id), messages)
    """

    # 任务类型 → 推荐模型列表（按优先级排序）
    TASK_ROUTES: Dict[str, List[Tuple[str, str]]] = {
        # (provider_id, model)
        "summarize": [
            ("deepseek", "deepseek-chat"),
            ("qwen", "qwen-turbo"),
            ("kimi", "moonshot-v1-8k"),
            ("ollama", "qwen2.5:7b"),
        ],
        "deep_read": [
            ("claude", "claude-sonnet-4-20250514"),
            ("openai", "gpt-4o"),
            ("kimi", "moonshot-v1-128k"),
            ("deepseek", "deepseek-chat"),
        ],
        "brainstorm": [
            ("gemini", "gemini-2.0-flash"),
            ("openai", "gpt-4o"),
            ("deepseek", "deepseek-chat"),
            ("qwen", "qwen-plus"),
        ],
        "gap_analysis": [
            ("claude", "claude-sonnet-4-20250514"),
            ("openai", "gpt-4o"),
            ("deepseek", "deepseek-reasoner"),
            ("kimi", "moonshot-v1-32k"),
        ],
        "writing": [
            ("deepseek", "deepseek-chat"),
            ("qwen", "qwen-max"),
            ("claude", "claude-sonnet-4-20250514"),
            ("kimi", "moonshot-v1-32k"),
        ],
        "translation": [
            ("deepseek", "deepseek-chat"),
            ("qwen", "qwen-turbo"),
            ("ollama", "qwen2.5:7b"),
        ],
        "critic": [
            ("claude", "claude-sonnet-4-20250514"),
            ("openai", "gpt-4o"),
            ("deepseek", "deepseek-reasoner"),
        ],
        "topic_discovery": [
            ("claude", "claude-sonnet-4-20250514"),
            ("openai", "gpt-4o"),
            ("deepseek", "deepseek-chat"),
            ("gemini", "gemini-1.5-pro"),
        ],
    }

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """
        参数:
            api_keys: {provider_id: api_key} 字典。
                      key为空字符串视为未配置。
                      ollama 不需要key。
        """
        self._keys: Dict[str, str] = api_keys or {}
        self._perf_log: List[CallRecord] = []
        self._perf_path = _DATA_DIR / "model_performance.jsonl"
        self._load_perf_log()

    def _load_perf_log(self):
        """加载历史表现记录"""
        if self._perf_path.exists():
            try:
                lines = self._perf_path.read_text(encoding="utf-8").strip().split("\n")
                for line in lines[-500:]:  # 只保留最近500条
                    if line.strip():
                        self._perf_log.append(
                            CallRecord(**json.loads(line))
                        )
            except Exception:
                pass

    def set_keys(self, keys: Dict[str, str]):
        """批量设置 API keys"""
        self._keys.update(keys)

    def get_key(self, provider_id: str) -> str:
        return self._keys.get(provider_id, "")

    def is_available(self, provider_id: str) -> bool:
        """检查 provider 是否可用（有key或是本地模型）"""
        if provider_id == "ollama":
            return True  # 本地模型，总是"可用"（实际可用性在调用时检查）
        key = self._keys.get(provider_id, "")
        return bool(key and key.strip())

    def available_providers(self) -> List[str]:
        """返回所有已配置（有key）的 provider 列表"""
        return [pid for pid in PROVIDERS if self.is_available(pid)]

    def route(
        self,
        task_type: str,
        budget: str = "balanced",
        exclude: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """
        为指定任务类型选择最佳可用模型。

        参数:
            task_type: 任务类型 (summarize/deep_read/brainstorm/...)
            budget: "fast"(快+便宜) / "balanced"(平衡) / "best"(质量优先)
            exclude: 排除的 provider_id 列表

        返回:
            (provider_id, model_name)

        异常:
            RuntimeError: 没有可用的模型
        """
        exclude = set(exclude or [])
        candidates = self.TASK_ROUTES.get(task_type, [])

        # 按 budget 过滤
        if budget == "fast":
            cost_ok = {"free", "low"}
        elif budget == "best":
            cost_ok = {"free", "low", "medium", "high"}
        else:  # balanced
            cost_ok = {"free", "low", "medium"}

        for provider_id, model in candidates:
            if provider_id in exclude:
                continue
            if not self.is_available(provider_id):
                continue
            prov = PROVIDERS.get(provider_id, {})
            if prov.get("cost_tier", "high") not in cost_ok and budget != "best":
                continue
            return provider_id, model

        # 降级：任意可用的 provider
        for provider_id, model in candidates:
            if provider_id not in exclude and self.is_available(provider_id):
                return provider_id, model

        # 最终降级：返回任何有key的provider
        for pid in PROVIDERS:
            if pid not in exclude and self.is_available(pid):
                prov = PROVIDERS[pid]
                return pid, prov["default_model"]

        raise RuntimeError(
            f"没有可用的AI模型。请配置至少一个API Key。任务类型: {task_type}"
        )

    def call(
        self,
        task_type: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 2000,
        temperature: float = 0.7,
        budget: str = "balanced",
        provider_id: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Tuple[str, str, Optional[dict]]:
        """
        高级接口：自动路由 + 调用 + 记录表现。

        返回: (content, model_used_str, usage_dict)
            model_used_str 格式: "provider_id:model"
        """
        if provider_id and model:
            pid, mdl = provider_id, model
        elif provider_id:
            pid = provider_id
            mdl = PROVIDERS.get(pid, {}).get("default_model", "")
        else:
            pid, mdl = self.route(task_type, budget=budget)

        key = self.get_key(pid)
        t0 = time.time()
        try:
            content, usage = call_provider(
                pid, key, messages,
                model=mdl, max_tokens=max_tokens, temperature=temperature,
            )
            latency = int((time.time() - t0) * 1000)
            self._record(pid, mdl, task_type, latency, True, usage=usage)
            return content, f"{pid}:{mdl}", usage
        except Exception as e:
            latency = int((time.time() - t0) * 1000)
            self._record(pid, mdl, task_type, latency, False, error=str(e))
            # 尝试降级到下一个可用模型
            try:
                pid2, mdl2 = self.route(task_type, budget=budget, exclude=[pid])
                key2 = self.get_key(pid2)
                t1 = time.time()
                content, usage = call_provider(
                    pid2, key2, messages,
                    model=mdl2, max_tokens=max_tokens, temperature=temperature,
                )
                latency2 = int((time.time() - t1) * 1000)
                self._record(pid2, mdl2, task_type, latency2, True, usage=usage)
                logger.info(f"模型降级: {pid}:{mdl} → {pid2}:{mdl2}")
                return content, f"{pid2}:{mdl2}", usage
            except Exception as e2:
                raise RuntimeError(
                    f"所有模型调用失败。主模型({pid}:{mdl}): {e} | 降级模型: {e2}"
                ) from e2

    def _record(self, pid, model, task_type, latency_ms, success,
                usage=None, error=""):
        """记录调用结果"""
        rec = CallRecord(
            provider=pid,
            model=model,
            task_type=task_type,
            input_tokens=(usage or {}).get("input_tokens", 0),
            output_tokens=(usage or {}).get("output_tokens", 0),
            latency_ms=latency_ms,
            success=success,
            error=error,
            timestamp=datetime.now().isoformat(),
        )
        self._perf_log.append(rec)
        # 持久化
        try:
            _DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(self._perf_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
        except Exception:
            pass

    def get_leaderboard(self, task_type: Optional[str] = None) -> Dict[str, dict]:
        """
        各模型表现排行榜。

        返回: {model_str: {calls, success_rate, avg_latency_ms, avg_tokens}}
        """
        from collections import defaultdict
        stats = defaultdict(lambda: {"calls": 0, "success": 0,
                                      "total_latency": 0, "total_tokens": 0})
        for rec in self._perf_log:
            if task_type and rec.task_type != task_type:
                continue
            key = f"{rec.provider}:{rec.model}"
            s = stats[key]
            s["calls"] += 1
            s["success"] += int(rec.success)
            s["total_latency"] += rec.latency_ms
            s["total_tokens"] += rec.output_tokens

        result = {}
        for key, s in stats.items():
            n = s["calls"]
            result[key] = {
                "calls": n,
                "success_rate": round(s["success"] / n, 2) if n else 0,
                "avg_latency_ms": round(s["total_latency"] / n) if n else 0,
                "avg_tokens": round(s["total_tokens"] / n) if n else 0,
            }
        return dict(sorted(result.items(), key=lambda x: -x[1]["calls"]))


# ─────────────────────────────────────────────────────────────
# 便捷函数
# ─────────────────────────────────────────────────────────────
_global_router: Optional[ModelRouter] = None


def get_router(api_keys: Optional[Dict[str, str]] = None) -> ModelRouter:
    """获取全局 ModelRouter 单例"""
    global _global_router
    if _global_router is None:
        _global_router = ModelRouter(api_keys=api_keys)
    elif api_keys:
        _global_router.set_keys(api_keys)
    return _global_router


def quick_call(
    task_type: str,
    prompt: str,
    system: str = "",
    api_keys: Optional[Dict[str, str]] = None,
    **kwargs,
) -> str:
    """
    最简调用：一行代码完成 路由+调用。

    用法:
        answer = quick_call("summarize", "请总结这篇论文...", api_keys={...})
    """
    router = get_router(api_keys)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    content, model_used, _ = router.call(task_type, messages, **kwargs)
    return content


def call_ai(
    prompt: str,
    system: str = "",
    provider: str = "auto",
    api_key: str = "",
    model: Optional[str] = None,
    task_type: str = "writing",
    max_tokens: int = 2000,
    temperature: float = 0.7,
    timeout: int = 60,
    budget: str = "balanced",
) -> str:
    """
    兼容旧代码的统一入口。

    - provider="auto": 走 ModelRouter 自动路由
    - provider="kimi"/"claude"/...: 直接指定 provider 调用
    """
    messages: List[Dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    if provider == "auto":
        router = get_router()
        content, _, _ = router.call(
            task_type,
            messages,
            budget=budget,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout,
        )
        return content

    if provider not in PROVIDERS:
        raise ValueError(f"未知 provider: {provider}")

    if provider != "ollama" and not api_key:
        raise ValueError(f"{provider} 缺少 API Key")

    content, _usage = call_provider(
        provider,
        api_key,
        messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        timeout=timeout,
    )
    return content
