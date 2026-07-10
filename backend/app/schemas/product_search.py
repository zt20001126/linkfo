from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.common.constants import MAX_PROMPT_LENGTH


class ProductSearchRequest(BaseModel):
    """选品搜索请求，用于接收前端输入的自然语言提示词。"""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=MAX_PROMPT_LENGTH,
        description="用户输入的选品提示词，后端会解析为 EchoTik 查询参数",
    )

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:
        """去除首尾空白后校验提示词，避免空字符串进入业务解析。"""

        prompt = value.strip()
        if not prompt:
            raise ValueError("prompt 不能为空")
        return prompt


class HealthData(BaseModel):
    """健康检查响应数据，用于前端或运维确认后端服务可用。"""

    service: str = Field(..., description="服务名称")
    status: str = Field(..., description="服务运行状态")


class CapabilityTool(BaseModel):
    """Agent 工具能力描述，用于告诉前端当前可展示的后端能力。"""

    id: str = Field(..., description="工具唯一标识")
    name: str = Field(..., description="工具展示名称")
    status: str = Field(..., description="工具当前实现状态")


class ProductCapabilitiesData(BaseModel):
    """Agent 能力列表响应数据，用于承载后端支持的工具集合。"""

    tools: list[CapabilityTool] = Field(..., description="Agent 工具列表")


class ProductSearchQuery(BaseModel):
    """提示词解析后的业务查询对象，用于连接自然语言和 EchoTik 参数。"""

    model_config = ConfigDict(populate_by_name=True)

    platform: str = Field(..., description="目标平台名称")
    region: str = Field(..., description="EchoTik 站点地区编码")
    keyword: str = Field(..., description="商品关键词")
    category_name: str = Field(..., alias="categoryName", description="商品分类名称")
    sort_by: str = Field(..., alias="sortBy", description="排序字段业务值")
    echotik_sort_field: int = Field(..., alias="echotikSortField", description="EchoTik 排序字段枚举值")
    sort_order: str = Field(..., alias="sortOrder", description="排序方向，asc 或 desc")
    page: int = Field(..., ge=1, description="查询页码")
    page_size: int = Field(..., alias="pageSize", ge=1, description="每页返回数量")


class EchoTikProductListParams(BaseModel):
    """EchoTik 商品列表参数，用于后续真实商品 API 请求。"""

    region: str = Field(..., description="EchoTik 站点地区编码")
    page_num: int = Field(..., ge=1, description="EchoTik 页码参数")
    page_size: int = Field(..., ge=1, description="EchoTik 每页数量参数")
    product_sort_field: int = Field(..., description="EchoTik 商品排序字段")
    sort_type: int = Field(..., description="EchoTik 排序方向枚举，0 升序，1 降序")


class EchoTikProductSearchResult(BaseModel):
    """EchoTik 商品搜索结果占位对象，用于隔离后续真实 API 返回结构。"""

    implemented: bool = Field(..., description="真实 EchoTik API 是否已经接入")
    params: EchoTikProductListParams = Field(..., description="本次调用准备使用的 EchoTik 参数")
    items: list[dict[str, Any]] = Field(default_factory=list, description="商品列表，占位阶段为空数组")


class ProductSearchData(BaseModel):
    """选品搜索响应数据，包含原始提示词、解析结果、EchoTik 参数和商品列表。"""

    model_config = ConfigDict(populate_by_name=True)

    prompt: str = Field(..., description="用户提交的原始提示词")
    query: ProductSearchQuery = Field(..., description="后端解析出的业务查询对象")
    echotik_params: EchoTikProductListParams = Field(
        ...,
        alias="echotikParams",
        description="准备提交给 EchoTik 的查询参数",
    )
    items: list[dict[str, Any]] = Field(default_factory=list, description="商品搜索结果列表")
