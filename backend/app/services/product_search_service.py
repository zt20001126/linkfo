from app.exceptions.business_exception import BusinessException
from app.schemas.product_search import ProductSearchData, ProductSearchRequest
from app.services.echotik_product_service import EchoTikProductService
from app.services.prompt_parser_service import PromptParserService


class ProductSearchService:
    """选品搜索编排服务，负责串联提示词解析和 EchoTik 商品服务。"""

    def __init__(
        self,
        prompt_parser_service: PromptParserService,
        echotik_product_service: EchoTikProductService,
    ) -> None:
        self._prompt_parser_service = prompt_parser_service
        self._echotik_product_service = echotik_product_service

    async def search(self, request: ProductSearchRequest) -> ProductSearchData:
        """执行选品搜索。

        Step 1: 校验并保留用户提示词。
        Step 2: 解析提示词，构造 EchoTik 商品列表参数。
        Step 3: 调用 EchoTik 商品服务并组装统一响应数据。
        """

        prompt = request.prompt.strip()
        if not prompt:
            raise BusinessException(code="INVALID_PROMPT", message="请传入 prompt 字段")

        query = self._prompt_parser_service.parse_product_search_prompt(prompt)
        echotik_params = self._prompt_parser_service.build_echotik_product_list_params(query)
        result = await self._echotik_product_service.search_products(echotik_params)

        return ProductSearchData(
            prompt=prompt,
            query=query,
            echotikParams=echotik_params,
            items=result.items,
        )


def get_product_search_service() -> ProductSearchService:
    """提供选品搜索服务实例，后续可替换为容器或更细粒度依赖注入。"""

    return ProductSearchService(
        prompt_parser_service=PromptParserService(),
        echotik_product_service=EchoTikProductService(),
    )
