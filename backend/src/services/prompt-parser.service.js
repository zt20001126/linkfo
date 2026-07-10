const REGION_MAP = [
  { label: "美国站", value: "US" },
  { label: "英国站", value: "GB" },
  { label: "泰国站", value: "TH" },
  { label: "越南站", value: "VN" },
  { label: "马来西亚站", value: "MY" },
  { label: "菲律宾站", value: "PH" },
  { label: "新加坡站", value: "SG" },
  { label: "印尼站", value: "ID" }
];

const SORT_FIELD_MAP = [
  { label: "总销量", value: "total_sale_cnt", echotikValue: 1 },
  { label: "总GMV", value: "total_sale_gmv_amt", echotikValue: 2 },
  { label: "SKU均价", value: "spu_avg_price", echotikValue: 3 },
  { label: "近7天销量", value: "total_sale_7d_cnt", echotikValue: 4 },
  { label: "近30天销量", value: "total_sale_30d_cnt", echotikValue: 5 },
  { label: "近7天GMV", value: "total_sale_gmv_7d_amt", echotikValue: 6 },
  { label: "近30天GMV", value: "total_sale_gmv_30d_amt", echotikValue: 7 }
];

export function parseProductSearchPrompt(prompt) {
  const sortField = findOption(SORT_FIELD_MAP, prompt) || SORT_FIELD_MAP[0];
  const region = findOption(REGION_MAP, prompt);

  return {
    platform: prompt.includes("TikTok Shop") ? "TikTok Shop" : "TikTok",
    region: region ? region.value : "US",
    keyword: readText(prompt, /商品关键词\s*([^，,。]+)/, ""),
    categoryName: readText(prompt, /商品分类\s*([^，,。]+)/, ""),
    sortBy: sortField.value,
    echotikSortField: sortField.echotikValue,
    sortOrder: prompt.includes("降序") ? "desc" : "asc",
    page: readNumber(prompt, /第\s*(\d+)\s*页/, 1),
    pageSize: readNumber(prompt, /每页\s*(\d+)\s*条/, 10)
  };
}

export function buildEchoTikProductListParams(query) {
  return {
    region: query.region,
    page_num: query.page,
    page_size: query.pageSize,
    product_sort_field: query.echotikSortField,
    sort_type: query.sortOrder === "desc" ? 1 : 0
  };
}

function findOption(options, text) {
  return options.find((option) => text.includes(option.label));
}

function readText(text, pattern, fallback) {
  return text.match(pattern)?.[1]?.trim() || fallback;
}

function readNumber(text, pattern, fallback) {
  return Number(readText(text, pattern, fallback));
}
