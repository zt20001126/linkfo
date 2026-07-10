(function () {
  const DEFAULT_CATEGORY_TEXT = "全部类目";

  function buildProductSearchPrompt(params) {
    const categories = normalizeCategories(params.categories);
    const categoryText = categories.length > 0 ? categories.join("、") : DEFAULT_CATEGORY_TEXT;

    return `@${params.toolName} 在 ${params.platform}，${params.region}站，商品关键词 ${params.keyword}，商品分类 ${categoryText}，按 ${params.sortBy} 排序，排序方式 ${params.sortOrder}，第 ${normalizePositiveNumber(params.page, 1)} 页，每页 ${normalizePositiveNumber(params.pageSize, 50)} 条。`;
  }

  function normalizeCategories(categories) {
    return Array.isArray(categories)
      ? categories.map((category) => String(category).trim()).filter(Boolean)
      : [];
  }

  function normalizePositiveNumber(value, fallback) {
    const number = Number(value);
    return Number.isFinite(number) && number > 0 ? Math.floor(number) : fallback;
  }

  window.ProductAgentPromptBuilder = {
    buildProductSearchPrompt
  };
})();
