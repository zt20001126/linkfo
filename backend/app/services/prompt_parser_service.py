import re
from dataclasses import dataclass

from app.common.constants import (
    ASC_SORT_TYPE,
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    DEFAULT_REGION,
    DESC_SORT_TYPE,
)
from app.schemas.product_search import EchoTikProductListParams, ProductSearchQuery


@dataclass(frozen=True)
class PromptOption:
    """提示词可识别选项，用于把中文标签映射成业务值和 EchoTik 枚举。"""

    label: str
    value: str
    echotik_value: int | None = None


REGION_OPTIONS = [
    PromptOption(label="美国站", value="US"),
    PromptOption(label="英国站", value="GB"),
    PromptOption(label="泰国站", value="TH"),
    PromptOption(label="越南站", value="VN"),
    PromptOption(label="马来西亚站", value="MY"),
    PromptOption(label="菲律宾站", value="PH"),
    PromptOption(label="新加坡站", value="SG"),
    PromptOption(label="印尼站", value="ID"),
]

SORT_FIELD_OPTIONS = [
    PromptOption(label="总销量", value="total_sale_cnt", echotik_value=1),
    PromptOption(label="总GMV", value="total_sale_gmv_amt", echotik_value=2),
    PromptOption(label="SKU均价", value="spu_avg_price", echotik_value=3),
    PromptOption(label="近7天销量", value="total_sale_7d_cnt", echotik_value=4),
    PromptOption(label="近30天销量", value="total_sale_30d_cnt", echotik_value=5),
    PromptOption(label="近7天GMV", value="total_sale_gmv_7d_amt", echotik_value=6),
    PromptOption(label="近30天GMV", value="total_sale_gmv_30d_amt", echotik_value=7),
]


class PromptParserService:
    """提示词解析服务，负责把选品自然语言映射为 EchoTik 商品查询参数。"""

    def parse_product_search_prompt(self, prompt: str) -> ProductSearchQuery:
        """解析选品提示词。

        Step 1: 从提示词中识别平台、地区、关键词和类目。
        Step 2: 把排序中文标签映射成 EchoTik 排序字段枚举。
        Step 3: 读取分页信息并组装业务查询对象。
        """

        sort_field = self._find_option(SORT_FIELD_OPTIONS, prompt) or SORT_FIELD_OPTIONS[0]
        region = self._find_option(REGION_OPTIONS, prompt)

        return ProductSearchQuery(
            platform="TikTok Shop" if "TikTok Shop" in prompt else "TikTok",
            region=region.value if region else DEFAULT_REGION,
            keyword=self._read_text(prompt, r"商品关键词\s*([^，,。]+)", ""),
            categoryName=self._read_text(prompt, r"商品分类\s*([^，,。]+)", ""),
            sortBy=sort_field.value,
            echotikSortField=sort_field.echotik_value or SORT_FIELD_OPTIONS[0].echotik_value,
            sortOrder="desc" if "降序" in prompt else "asc",
            page=self._read_number(prompt, r"第\s*(\d+)\s*页", DEFAULT_PAGE),
            pageSize=self._read_number(prompt, r"每页\s*(\d+)\s*条", DEFAULT_PAGE_SIZE),
        )

    def build_echotik_product_list_params(self, query: ProductSearchQuery) -> EchoTikProductListParams:
        """构造 EchoTik 商品列表参数。

        Step 1: 透传已识别的地区和分页参数。
        Step 2: 把后端业务排序方向转换成 EchoTik sort_type 枚举。
        """

        return EchoTikProductListParams(
            region=query.region,
            page_num=query.page,
            page_size=query.page_size,
            product_sort_field=query.echotik_sort_field,
            sort_type=DESC_SORT_TYPE if query.sort_order == "desc" else ASC_SORT_TYPE,
        )

    def _find_option(self, options: list[PromptOption], text: str) -> PromptOption | None:
        """从提示词中查找第一个命中的配置项。"""

        return next((option for option in options if option.label in text), None)

    def _read_text(self, text: str, pattern: str, fallback: str) -> str:
        """按正则读取提示词片段，读取不到时使用安全默认值。"""

        matched = re.search(pattern, text)
        return matched.group(1).strip() if matched else fallback

    def _read_number(self, text: str, pattern: str, fallback: int) -> int:
        """按正则读取正整数，避免无效分页值进入 EchoTik 参数。"""

        raw_value = self._read_text(text, pattern, str(fallback))
        number = int(raw_value)
        return number if number > 0 else fallback
