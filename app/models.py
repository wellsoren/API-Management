from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from sqlmodel import Field, SQLModel, select


@dataclass
class ProviderConfig:
    """单个提供商的基础配置"""
    name: str
    base_url_openai: str = ""
    base_url_anthropic: str = ""
    website: str = ""


# 预置的 26 个模型提供商（按首字母排序），附带正确的默认接口地址和官网
PRESET_PROVIDERS: List[ProviderConfig] = [
    ProviderConfig("Agnes AI", "https://apihub.agnes-ai.com/v1", "", "https://platform.agnes-ai.com/"),
    ProviderConfig("阿里云百炼", "https://{WorkspaceId}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1", "", "https://bailian.console.aliyun.com/"),
    ProviderConfig("Anthropic", "", "https://api.anthropic.com/", "https://platform.claude.com/"),
    ProviderConfig("百度千帆", "https://qianfan.baidubce.com/v2", "", "https://cloud.baidu.com/product-s/qianfan_home"),
    ProviderConfig("DeepSeek", "https://api.deepseek.com/", "https://api.deepseek.com/anthropic", "https://platform.deepseek.com/"),
    ProviderConfig("Google Gemini", "https://generativelanguage.googleapis.com/v1beta", "", "https://ai.google.dev/"),
    ProviderConfig("GitHub", "https://api.github.com/", "", "https://docs.github.com/rest"),
    ProviderConfig("硅基流动", "https://api.siliconflow.cn/v1", "", "https://siliconflow.cn/"),
    ProviderConfig("火山方舟", "https://ark.cn-beijing.volces.com/", "", "https://ark.volcengine.com/"),
    ProviderConfig("LongCat", "https://api.longcat.chat/openai", "https://api.longcat.chat/anthropic", "https://longcat.chat/"),
    ProviderConfig("MiniMax", "https://api.minimaxi.com/v1", "https://api.minimaxi.com/anthropic", "https://platform.minimaxi.com/"),
    ProviderConfig("秘塔AI", "https://metaso.cn/search-api/playground", "", "https://metaso.cn/"),
    ProviderConfig("Nvidia NIM", "https://integrate.api.nvidia.com/v1", "", "https://build.nvidia.com/"),
    ProviderConfig("Ollama", "http://localhost:11434/v1", "", "https://ollama.com/"),
    ProviderConfig("OpenAI", "https://api.openai.com/v1", "", "https://platform.openai.com/"),
    ProviderConfig("OpenCode", "https://api.opencode.ai/v1", "", "https://opencode.ai/"),
    ProviderConfig("OpenRouter", "https://openrouter.ai/api/v1", "", "https://openrouter.ai/"),
    ProviderConfig("商汤科技", "https://token.sensenova.cn/v1", "", "https://www.sensenova.cn/token-plan"),
    ProviderConfig("Tavily", "https://api.tavily.com/", "", "https://tavily.com/"),
    ProviderConfig("腾讯混元", "https://api.hunyuan.cloud.tencent.com/v1", "", "https://cloud.tencent.com/product/tclm"),
    ProviderConfig("UniFuncs", "", "", "https://unifuncs.com/"),
    ProviderConfig("XiaoMiMo", "https://api.xiaomimimo.com/v1", "", "https://mimo.mi.com/"),
    ProviderConfig("月之暗面", "https://api.moonshot.cn/v1", "", "https://platform.kimi.com/"),
    ProviderConfig("跃阶星辰", "https://api.stepfun.com/v1", "", "https://platform.stepfun.com/"),
    ProviderConfig("智谱AI", "https://open.bigmodel.cn/api/paas/v4", "", "https://open.bigmodel.cn/"),
    ProviderConfig("在问", "https://oneapi.zaiwenai.com/v1", "https://oneapi.zaiwenai.com/v1/chat/claude", "https://platform.zaiwenai.com/"),
    ProviderConfig("自定义模型", "", "", ""),
]

PRESET_PROVIDER_NAMES = [p.name for p in PRESET_PROVIDERS]


def get_provider_config(name: str) -> ProviderConfig | None:
    """按名称查找预置提供商配置"""
    for p in PRESET_PROVIDERS:
        if p.name == name:
            return p
    return None


PROVIDER_CONFIG_DICTS = [
    {"name": p.name, "base_url_openai": p.base_url_openai, "base_url_anthropic": p.base_url_anthropic, "website": p.website}
    for p in PRESET_PROVIDERS
]
"""ProviderConfig 的字典表示，用于传给 Jinja2 模板（tojson 序列化）"""


def get_all_providers(session) -> list[str]:
    """返回预置提供商名称列表 + 数据库中已有的额外提供商（去重合并）"""
    db_providers = session.exec(select(ApiInfo.provider).distinct()).all()
    db_set = {p for p in db_providers if p}
    merged = list(dict.fromkeys(PRESET_PROVIDER_NAMES + sorted(db_set, key=str.lower)))
    return merged


class ApiInfo(SQLModel, table=True):
    """API 接口信息模型"""

    id: int | None = Field(default=None, primary_key=True)
    provider: str = Field(default="", index=True, description="模型提供商")
    name: str = Field(index=True, description="API 名称")
    url_openai: str = Field(default="", description="OpenAI 兼容接口地址")
    url_anthropic: str = Field(default="", description="Anthropic 原生接口地址")
    model_name: str = Field(default="", description="模型名")
    model_attr: str = Field(default="", description="模型属性：文本/图像/语音/向量/嵌入等")
    api_key: str = Field(default="", description="API Key")
    app_usage: str = Field(default="", description="所属应用")
    website: str = Field(default="", description="官网地址")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
