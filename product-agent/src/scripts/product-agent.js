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
    toast: document.getElementById("toast"),
    toastText: document.getElementById("toastText")
  };

  const state = {
    products: [],
    selectedIds: new Set(),
    query: {}
  };

  function init() {
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

    [elements.statusFilter, elements.timeFilter, elements.keywordFilter].forEach((control) => {
      control.addEventListener("input", renderProducts);
      control.addEventListener("change", renderProducts);
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

  function renderIcons() {
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  init();
})();
