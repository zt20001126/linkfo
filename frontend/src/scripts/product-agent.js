(function () {
  const elements = {
    promptInput: document.getElementById("promptInput"),
    productBody: document.getElementById("productBody"),
    emptyState: document.getElementById("emptyState"),
    resultCount: document.getElementById("resultCount"),
    candidateCount: document.getElementById("candidateCount"),
    chipList: document.getElementById("chipList"),
    runBtn: document.getElementById("runBtn"),
    selectAll: document.getElementById("selectAll"),
    statusFilter: document.getElementById("statusFilter"),
    timeFilter: document.getElementById("timeFilter"),
    keywordFilter: document.getElementById("keywordFilter"),
    addSelectedBtn: document.getElementById("addSelectedBtn"),
    clearBtn: document.getElementById("clearBtn"),
    productToolTab: document.getElementById("productToolTab"),
    productToolPanel: document.getElementById("productToolPanel"),
    closeProductToolBtn: document.getElementById("closeProductToolBtn"),
    resetProductToolBtn: document.getElementById("resetProductToolBtn"),
    generatePromptBtn: document.getElementById("generatePromptBtn"),
    toolPlatform: document.getElementById("toolPlatform"),
    toolRegion: document.getElementById("toolRegion"),
    toolName: document.getElementById("toolName"),
    toolKeyword: document.getElementById("toolKeyword"),
    toolSortBy: document.getElementById("toolSortBy"),
    toolSortOrder: document.getElementById("toolSortOrder"),
    toolPage: document.getElementById("toolPage"),
    toolPageSize: document.getElementById("toolPageSize"),
    categoryTrigger: document.getElementById("categoryTrigger"),
    categoryTags: document.getElementById("categoryTags"),
    categoryMenu: document.getElementById("categoryMenu"),
    categoryOptions: document.getElementById("categoryOptions"),
    categoryCount: document.getElementById("categoryCount"),
    clearCategoryBtn: document.getElementById("clearCategoryBtn"),
    confirmCategoryBtn: document.getElementById("confirmCategoryBtn"),
    toast: document.getElementById("toast"),
    toastText: document.getElementById("toastText")
  };

  const PRODUCT_CATEGORIES = [
    "儿童时尚",
    "箱包",
    "穆斯林时尚",
    "宠物用品",
    "二手",
    "运动与户外",
    "五金工具",
    "女装与女士内衣",
    "厨房用品",
    "男装与男士内衣",
    "其它",
    "手机与数码",
    "鞋靴",
    "家纺布艺",
    "玩具和爱好"
  ];

  const state = {
    products: [],
    selectedIds: new Set(),
    query: {},
    selectedScene: "产品",
    selectedCategories: new Set(["运动与户外"])
  };

  function init() {
    renderCategoryOptions();
    renderCategorySelection();
    bindEvents();
    state.query = ProductAgentPromptParser.parsePrompt(elements.promptInput.value);
    renderQueryChips(state.query);
    renderProducts();
    renderIcons();
  }

  function bindEvents() {
    elements.runBtn.addEventListener("click", runSearch);
    elements.addSelectedBtn.addEventListener("click", saveSelectedProducts);
    elements.clearBtn.addEventListener("click", clearProducts);
    elements.selectAll.addEventListener("change", toggleVisibleSelection);
    elements.productBody.addEventListener("click", handleTableClick);
    elements.productBody.addEventListener("change", handleTableSelection);
    elements.productToolTab.addEventListener("click", openProductToolPanel);
    elements.closeProductToolBtn.addEventListener("click", closeProductToolPanel);
    elements.resetProductToolBtn.addEventListener("click", resetProductTool);
    elements.generatePromptBtn.addEventListener("click", generatePromptFromTool);
    elements.categoryTrigger.addEventListener("click", toggleCategoryMenu);
    elements.categoryOptions.addEventListener("change", handleCategoryChange);
    elements.categoryTags.addEventListener("click", handleCategoryTagClick);
    elements.clearCategoryBtn.addEventListener("click", clearCategories);
    elements.confirmCategoryBtn.addEventListener("click", closeCategoryMenu);

    [elements.statusFilter, elements.timeFilter, elements.keywordFilter].forEach((control) => {
      control.addEventListener("input", renderProducts);
      control.addEventListener("change", renderProducts);
    });

    document.querySelectorAll(".scene-tab").forEach((button) => {
      button.addEventListener("click", () => selectScene(button.dataset.scene));
    });

    document.addEventListener("click", (event) => {
      if (!elements.productToolPanel.contains(event.target) && event.target !== elements.productToolTab) {
        closeCategoryMenu();
      }
    });
  }

  function runSearch() {
    elements.runBtn.disabled = true;
    state.query = ProductAgentPromptParser.parsePrompt(elements.promptInput.value);
    renderQueryChips(state.query);

    window.setTimeout(() => {
      state.products = ProductAgentMockProducts.map((item) => ({
        ...item,
        keyword: state.query.keyword || item.keyword
      }));
      state.selectedIds.clear();
      elements.runBtn.disabled = false;
      renderProducts();
      showToast("已生成前端模拟查询结果，真实 EchoTik 接口待接入");
    }, 360);
  }

  function renderQueryChips(query) {
    const chips = [
      `站点 ${query.region}`,
      `关键词 ${query.keyword}`,
      `分类 ${query.category}`,
      `排序 ${query.sortBy}/${query.sortOrder === "desc" ? "降序" : "升序"}`,
      `第 ${query.page} 页`,
      `每页 ${query.pageSize}`
    ];

    elements.chipList.innerHTML = chips
      .map((label) => `<span class="chip">${escapeHtml(label)}</span>`)
      .join("");

    if (query.pageSize > 10) {
      elements.chipList.insertAdjacentHTML("beforeend", '<span class="chip is-warning">EchoTik 文档 page_size 最大 10，待确认</span>');
    }
  }

  function renderProducts() {
    const rows = getVisibleProducts();
    elements.productBody.innerHTML = rows.map(renderProductRow).join("");
    elements.emptyState.classList.toggle("is-visible", rows.length === 0);
    elements.resultCount.textContent = `${rows.length} 个产品`;
    elements.candidateCount.textContent = `${getSavedCount()} 个已加入候选`;
    elements.selectAll.checked = rows.length > 0 && rows.every((item) => state.selectedIds.has(item.id));
    renderIcons();
  }

  function openProductToolPanel() {
    elements.productToolPanel.hidden = false;
    elements.productToolTab.classList.add("is-active");
    renderIcons();
  }

  function closeProductToolPanel() {
    elements.productToolPanel.hidden = true;
    closeCategoryMenu();
  }

  function selectScene(scene) {
    state.selectedScene = scene;
    document.querySelectorAll(".scene-tab").forEach((button) => {
      button.classList.toggle("is-active", button.dataset.scene === scene);
    });
  }

  function renderCategoryOptions() {
    elements.categoryOptions.innerHTML = PRODUCT_CATEGORIES.map((category) => `
      <label class="category-option">
        <input type="checkbox" value="${escapeHtml(category)}" data-category-option ${state.selectedCategories.has(category) ? "checked" : ""}>
        <span>${escapeHtml(category)}</span>
      </label>
    `).join("");
  }

  function renderCategorySelection() {
    const categories = [...state.selectedCategories];
    elements.categoryTags.innerHTML = categories.map((category) => `
      <span class="category-tag">
        ${escapeHtml(category)}
        <button type="button" data-remove-category="${escapeHtml(category)}" aria-label="移除 ${escapeHtml(category)}">
          <i data-lucide="x" width="12" height="12"></i>
        </button>
      </span>
    `).join("");

    const placeholder = elements.categoryTrigger.querySelector(".category-placeholder");
    placeholder.hidden = categories.length > 0;
    elements.categoryCount.textContent = `已选 ${categories.length} 个`;

    elements.categoryOptions.querySelectorAll("[data-category-option]").forEach((checkbox) => {
      checkbox.checked = state.selectedCategories.has(checkbox.value);
    });

    renderIcons();
  }

  function toggleCategoryMenu() {
    const isOpen = elements.categoryMenu.hidden;
    elements.categoryMenu.hidden = !isOpen;
    elements.categoryTrigger.classList.toggle("is-open", isOpen);
    elements.categoryTrigger.setAttribute("aria-expanded", String(isOpen));
  }

  function closeCategoryMenu() {
    elements.categoryMenu.hidden = true;
    elements.categoryTrigger.classList.remove("is-open");
    elements.categoryTrigger.setAttribute("aria-expanded", "false");
  }

  function handleCategoryChange(event) {
    const checkbox = event.target.closest("[data-category-option]");
    if (!checkbox) return;

    if (checkbox.checked) {
      state.selectedCategories.add(checkbox.value);
    } else {
      state.selectedCategories.delete(checkbox.value);
    }
    renderCategorySelection();
  }

  function handleCategoryTagClick(event) {
    const removeButton = event.target.closest("[data-remove-category]");
    if (!removeButton) return;

    event.stopPropagation();
    state.selectedCategories.delete(removeButton.dataset.removeCategory);
    renderCategorySelection();
  }

  function clearCategories() {
    state.selectedCategories.clear();
    renderCategorySelection();
  }

  function resetProductTool() {
    selectScene("产品");
    elements.toolPlatform.value = "TikTok Shop";
    elements.toolRegion.value = "美国";
    elements.toolName.value = "EchoTik-TikTok商品搜索";
    elements.toolKeyword.value = "公路自行车";
    elements.toolSortBy.value = "总销量";
    elements.toolSortOrder.value = "降序";
    elements.toolPage.value = "1";
    elements.toolPageSize.value = "50";
    state.selectedCategories = new Set(["运动与户外"]);
    renderCategorySelection();
    closeCategoryMenu();
    showToast("选品工具参数已重置");
  }

  function generatePromptFromTool() {
    const keyword = elements.toolKeyword.value.trim();
    if (!keyword) {
      showToast("请填写商品关键词");
      elements.toolKeyword.focus();
      return;
    }

    const categories = [...state.selectedCategories];
    const categoryText = categories.length > 0 ? categories.join("、") : "全部类目";
    const prompt = `@${elements.toolName.value} 在 ${elements.toolPlatform.value}，${elements.toolRegion.value}站，商品关键词 ${keyword}，商品分类 ${categoryText}，按 ${elements.toolSortBy.value} 排序，排序方式 ${elements.toolSortOrder.value}，第 ${normalizePositiveNumber(elements.toolPage.value, 1)} 页，每页 ${normalizePositiveNumber(elements.toolPageSize.value, 50)} 条。`;

    elements.promptInput.value = prompt;
    state.query = ProductAgentPromptParser.parsePrompt(prompt);
    renderQueryChips(state.query);
    closeProductToolPanel();
    showToast("提示词已生成");
  }

  function renderProductRow(item) {
    const checked = state.selectedIds.has(item.id) ? "checked" : "";
    const statusText = item.status === "saved" ? "已加入" : "待定";
    const statusClass = item.status === "saved" ? "status is-saved" : "status";

    return `
      <tr>
        <td class="check-cell">
          <input type="checkbox" data-select="${escapeHtml(item.id)}" aria-label="选择 ${escapeHtml(item.title)}" ${checked}>
        </td>
        <td>
          <img class="product-img" src="${escapeHtml(item.image)}" alt="${escapeHtml(item.title)}">
        </td>
        <td>
          <span class="title-main">${escapeHtml(item.title)}</span>
          <span class="title-sub">${escapeHtml(item.category)}</span>
        </td>
        <td class="mono">${escapeHtml(item.id)}</td>
        <td>${escapeHtml(item.platform)}</td>
        <td><span class="${statusClass}">${statusText}</span></td>
        <td>
          <span class="metric">${formatNumber(item.totalSales)}</span>
          <span class="metric-sub">累计销量</span>
        </td>
        <td>
          <span class="metric">${formatNumber(item.sales30d)}</span>
          <span class="metric-sub">近30天</span>
        </td>
        <td>${escapeHtml(item.price)}</td>
        <td>${item.rating.toFixed(1)}</td>
        <td><span class="keyword">${escapeHtml(item.keyword)}</span></td>
        <td>${escapeHtml(item.addedAt)}</td>
        <td>
          <div class="row-actions">
            <button class="icon-btn" type="button" data-save="${escapeHtml(item.id)}" title="加入候选" aria-label="加入候选">
              <i data-lucide="plus" width="15" height="15"></i>
            </button>
            <button class="icon-btn" type="button" data-delete="${escapeHtml(item.id)}" title="删除" aria-label="删除">
              <i data-lucide="trash-2" width="15" height="15"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }

  function getVisibleProducts() {
    const status = elements.statusFilter.value;
    const keyword = elements.keywordFilter.value.trim().toLowerCase();
    const time = elements.timeFilter.value;

    return state.products.filter((item) => {
      const matchesStatus = status === "all" || item.status === status;
      const matchesKeyword = !keyword || `${item.title} ${item.keyword} ${item.id}`.toLowerCase().includes(keyword);
      const matchesTime = time === "all" || time === "today" || time === "7d";
      return matchesStatus && matchesKeyword && matchesTime;
    });
  }

  function saveSelectedProducts() {
    saveProducts([...state.selectedIds]);
  }

  function saveProducts(ids) {
    if (ids.length === 0) {
      showToast("请先选择产品");
      return;
    }

    state.products = state.products.map((item) => (
      ids.includes(item.id) ? { ...item, status: "saved" } : item
    ));
    renderProducts();
    showToast(`已加入 ${ids.length} 个候选产品`);
  }

  function clearProducts() {
    state.products = [];
    state.selectedIds.clear();
    renderProducts();
    showToast("产品列表已清空");
  }

  function toggleVisibleSelection() {
    getVisibleProducts().forEach((item) => {
      if (elements.selectAll.checked) {
        state.selectedIds.add(item.id);
      } else {
        state.selectedIds.delete(item.id);
      }
    });
    renderProducts();
  }

  function handleTableClick(event) {
    const saveButton = event.target.closest("[data-save]");
    const deleteButton = event.target.closest("[data-delete]");

    if (saveButton) {
      saveProducts([saveButton.dataset.save]);
    }

    if (deleteButton) {
      deleteProduct(deleteButton.dataset.delete);
    }
  }

  function handleTableSelection(event) {
    const checkbox = event.target.closest("[data-select]");
    if (!checkbox) return;

    if (checkbox.checked) {
      state.selectedIds.add(checkbox.dataset.select);
    } else {
      state.selectedIds.delete(checkbox.dataset.select);
    }
    renderProducts();
  }

  function deleteProduct(id) {
    state.products = state.products.filter((item) => item.id !== id);
    state.selectedIds.delete(id);
    renderProducts();
    showToast("已删除产品");
  }

  function getSavedCount() {
    return state.products.filter((item) => item.status === "saved").length;
  }

  function showToast(message) {
    elements.toastText.textContent = message;
    elements.toast.classList.add("is-visible");
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => elements.toast.classList.remove("is-visible"), 2200);
  }

  function formatNumber(value) {
    return new Intl.NumberFormat("zh-CN").format(value);
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function normalizePositiveNumber(value, fallback) {
    const number = Number(value);
    return Number.isFinite(number) && number > 0 ? Math.floor(number) : fallback;
  }

  function renderIcons() {
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  init();
})();
