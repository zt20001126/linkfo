from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.common.constants import DEFAULT_CATEGORY_MAPPING_SOURCE, SEARCH_RECORD_STATUS_SKIPPED
from app.db.base import Base


class ProductSearchRecord(Base):
    """选品查询记录模型，用于保存用户提示词、EchoTik 请求摘要和安全响应摘要。"""

    __tablename__ = "product_search_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="查询记录主键")
    prompt: Mapped[str] = mapped_column(Text, comment="用户提交的原始提示词")
    region: Mapped[str] = mapped_column(String(16), index=True, comment="EchoTik 地区编码")
    keyword: Mapped[str] = mapped_column(String(256), default="", comment="内部保留的商品关键词，不直接提交给 EchoTik")
    category_name: Mapped[str] = mapped_column(String(128), default="", comment="用户输入的分类名称")
    category_id: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="EchoTik 一级分类 ID")
    category_l2_id: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="EchoTik 二级分类 ID")
    category_l3_id: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="EchoTik 三级分类 ID")
    page_num: Mapped[int] = mapped_column(Integer, comment="EchoTik 查询页码")
    page_size: Mapped[int] = mapped_column(Integer, comment="EchoTik 每页数量")
    product_sort_field: Mapped[int] = mapped_column(Integer, comment="EchoTik 商品排序字段枚举")
    sort_type: Mapped[int] = mapped_column(Integer, comment="EchoTik 排序方向枚举，0 升序，1 降序")
    request_params: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, comment="脱敏后的 EchoTik 请求参数")
    response_summary: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, comment="脱敏后的响应摘要")
    status: Mapped[str] = mapped_column(String(32), default=SEARCH_RECORD_STATUS_SKIPPED, comment="查询状态")
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="安全业务错误码")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )


class ProductCategoryMapping(Base):
    """商品分类映射模型，用于维护用户分类名称到 EchoTik 分类 ID 的本地映射。"""

    __tablename__ = "product_category_mapping"
    __table_args__ = (
        Index("ix_product_category_mapping_region_name", "region", "category_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="分类映射主键")
    region: Mapped[str] = mapped_column(String(16), comment="EchoTik 地区编码")
    category_name: Mapped[str] = mapped_column(String(128), comment="用户输入或运营维护的分类名称")
    category_id: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="EchoTik 一级分类 ID")
    category_l2_id: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="EchoTik 二级分类 ID")
    category_l3_id: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="EchoTik 三级分类 ID")
    source: Mapped[str] = mapped_column(String(32), default=DEFAULT_CATEGORY_MAPPING_SOURCE, comment="映射来源")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用该映射")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )
