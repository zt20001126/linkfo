from app.schemas.product_search import EchoTikProductListParams, EchoTikProductSearchResult


class EchoTikProductService:
    """EchoTik 商品服务，占位阶段只回显参数，后续在这里封装真实 API 调用。"""

    async def search_products(self, params: EchoTikProductListParams) -> EchoTikProductSearchResult:
        """搜索 EchoTik 商品。

        Step 1: 接收已经标准化的 EchoTik 商品查询参数。
        Step 2: 占位阶段不发起外部请求，返回空商品列表。
        Step 3: 后续真实接入时在本服务内处理鉴权、超时、限流和安全错误转换。
        """

        return EchoTikProductSearchResult(implemented=False, params=params, items=[])
