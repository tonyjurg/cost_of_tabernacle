(function () {
  const MATERIAL_META = [
    { id: "gold", name: "Gold", color: "#c79a19" },
    { id: "silver", name: "Silver", color: "#8a97a6" },
    { id: "bronze", name: "Bronze", color: "#a05e2a" },
    { id: "blue-yarn", name: "Blue yarn", color: "#2b5f8a" },
    { id: "purple-yarn", name: "Purple yarn", color: "#714f91" },
    { id: "scarlet-yarn", name: "Scarlet yarn", color: "#b14a47" },
    { id: "fine-linen", name: "Fine twined linen", color: "#9d927c" },
    { id: "onyx", name: "Onyx shoulder stones", color: "#202020" },
    { id: "breastpiece-stones", name: "Breastpiece stones", color: "#4c8d65" },
    { id: "acacia-wood", name: "Acacia wood", color: "#8c6d43" },
    { id: "olive-oil", name: "Olive oil for the light", color: "#7b8d34" },
    { id: "myrrh", name: "Myrrh (anointing oil recipe)", color: "#7a5333" },
    { id: "cinnamon", name: "Sweet cinnamon (anointing oil recipe)", color: "#b36a3c" },
    { id: "calamus", name: "Aromatic cane / calamus", color: "#4d7f45" },
    { id: "cassia", name: "Cassia (anointing oil recipe)", color: "#8d5a2f" },
    { id: "anointing-oil-olive-oil", name: "Olive oil (anointing oil recipe)", color: "#9aab45" },
  ];

  const state = {
    currency: "USD",
    mode: "total",
    history: null,
    chart: null,
    loadedFrom: "unknown",
  };

  const elements = {
    currencyToggle: document.querySelector("#history-currency-toggle"),
    seriesMode: document.querySelector("#series-mode"),
    status: document.querySelector("#history-status"),
    updatedBadge: document.querySelector("#history-updated-badge"),
    sourceBadge: document.querySelector("#history-source-badge"),
    snapshotCount: document.querySelector("#snapshot-count"),
    firstSnapshot: document.querySelector("#first-snapshot"),
    latestTotal: document.querySelector("#latest-total"),
    latestTable: document.querySelector("#latest-history-table"),
    chartCanvas: document.querySelector("#history-chart"),
  };

  elements.currencyToggle.addEventListener("click", (event) => {
    const button = event.target.closest("[data-currency]");
    if (!button) {
      return;
    }

    state.currency = button.dataset.currency;
    syncCurrencyButtons();
    render();
  });

  elements.seriesMode.addEventListener("change", () => {
    state.mode = elements.seriesMode.value;
    renderChart();
  });

  syncCurrencyButtons();
  loadHistory();

  async function loadHistory() {
    if (window.TABERNACLE_PRICE_HISTORY && Array.isArray(window.TABERNACLE_PRICE_HISTORY.entries)) {
      state.history = window.TABERNACLE_PRICE_HISTORY;
      state.loadedFrom = "embedded JS mirror";
      render();
      return;
    }

    try {
      const response = await fetch("./data/price-history.json", { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      state.history = await response.json();
      state.loadedFrom = "JSON fetch";
      render();
    } catch (error) {
      setHistorySummary(
        "Could not load the history data file yet. Run the recorder script to create snapshots.",
        "History file not loaded.",
        "Sources: Yahoo Finance futures, Frankfurter FX, static retail and grocery proxies."
      );
      elements.snapshotCount.textContent = "0";
      elements.firstSnapshot.textContent = "--";
      elements.latestTotal.textContent = "--";
      elements.latestTable.innerHTML = "";
    }
  }

  function render() {
    const entries = getEntries();
    if (!entries.length) {
      setHistorySummary(
        "No history snapshots yet. Run the recorder script once and refresh this page.",
        "No snapshots recorded yet.",
        "Sources: Yahoo Finance futures, Frankfurter FX, static retail and grocery proxies."
      );
      elements.snapshotCount.textContent = "0";
      elements.firstSnapshot.textContent = "--";
      elements.latestTotal.textContent = "--";
      elements.latestTable.innerHTML = "";
      renderChart();
      return;
    }

    const firstEntry = entries[0];
    const latestEntry = entries[entries.length - 1];
    const latestTotal = state.currency === "EUR" ? latestEntry.documentedTotalEur : latestEntry.documentedTotalUsd;

    setHistorySummary(
      `Loaded ${entries.length} recorded snapshots. Latest snapshot: ${formatDateTime(latestEntry.recordedAt)}.`,
      `History range: ${formatShortDate(firstEntry.recordedAt)} to ${formatShortDate(latestEntry.recordedAt)} | Loaded via ${state.loadedFrom}.`,
      "Sources: Yahoo Finance historical futures, Frankfurter FX, static retail and grocery proxies for non-metals."
    );
    elements.snapshotCount.textContent = String(entries.length);
    elements.firstSnapshot.textContent = formatDateTime(firstEntry.recordedAt);
    elements.latestTotal.textContent = formatMoney(latestTotal, state.currency);
    elements.latestTable.innerHTML = buildLatestTableMarkup(latestEntry);

    renderChart();
  }

  function renderChart() {
    const entries = getEntries();
    const labels = entries.map((entry) => formatShortDate(entry.recordedAt));
    const config = getChartConfig(entries, labels);

    if (state.chart) {
      state.chart.destroy();
    }

    state.chart = new Chart(elements.chartCanvas, config);
  }

  function getChartConfig(entries, labels) {
    if (!entries.length) {
      return {
        type: "line",
        data: { labels: [], datasets: [] },
        options: baseChartOptions("No data yet"),
      };
    }

    if (state.mode === "total") {
      return {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: `Documented total (${state.currency})`,
              data: entries.map((entry) => state.currency === "EUR" ? entry.documentedTotalEur : entry.documentedTotalUsd),
              borderColor: "#245c7d",
              backgroundColor: "rgba(36, 92, 125, 0.18)",
              borderWidth: 2,
              pointRadius: 2,
              tension: 0.25,
            },
          ],
        },
        options: baseChartOptions(`Documented total (${state.currency})`),
      };
    }

    const fieldName = state.mode === "rowTotals"
      ? (state.currency === "EUR" ? "rowTotalEur" : "rowTotalUsd")
      : (state.currency === "EUR" ? "unitPriceEur" : "unitPriceUsd");

    const datasets = MATERIAL_META
      .map((material) => {
        const values = entries.map((entry) => {
          const row = entry.materials[material.id];
          return row ? row[fieldName] : null;
        });

        if (values.every((value) => value === null || value === undefined)) {
          return null;
        }

        return {
          label: material.name,
          data: values,
          borderColor: material.color,
          backgroundColor: material.color,
          borderWidth: 2,
          pointRadius: 1.5,
          spanGaps: true,
          tension: 0.2,
        };
      })
      .filter(Boolean);

    const title = state.mode === "rowTotals" ? `Row totals (${state.currency})` : `Unit prices (${state.currency})`;

    return {
      type: "line",
      data: { labels, datasets },
      options: baseChartOptions(title),
    };
  }

  function baseChartOptions(title) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "nearest",
        intersect: false,
      },
      plugins: {
        legend: {
          position: "bottom",
        },
        title: {
          display: true,
          text: title,
        },
        tooltip: {
          callbacks: {
            label(context) {
              const value = context.parsed.y;
              if (value === null || value === undefined) {
                return `${context.dataset.label}: n/a`;
              }

              return `${context.dataset.label}: ${formatMoney(value, state.currency)}`;
            },
          },
        },
      },
      scales: {
        y: {
          ticks: {
            callback(value) {
              return compactMoney(value, state.currency);
            },
          },
        },
      },
    };
  }

  function buildLatestTableMarkup(entry) {
    return MATERIAL_META.map((material) => {
      const row = entry.materials[material.id];
      if (!row) {
        return "";
      }

      const unitValue = state.currency === "EUR" ? row.unitPriceEur : row.unitPriceUsd;
      const rowValue = state.currency === "EUR" ? row.rowTotalEur : row.rowTotalUsd;

      return `
        <tr>
          <td>
            <p class="material-title">${escapeHtml(row.name)}</p>
            <span class="material-meta">${escapeHtml(row.verses)}</span>
          </td>
          <td>${unitValue === null ? "N/A" : `<span class="value-strong">${formatMoney(unitValue, state.currency)}</span>`}</td>
          <td>${rowValue === null ? "N/A" : `<span class="value-strong">${formatMoney(rowValue, state.currency)}</span>`}</td>
          <td><span class="small-note">${escapeHtml(row.pricingBasis)}</span></td>
        </tr>
      `;
    }).join("");
  }

  function getEntries() {
    if (!state.history || !Array.isArray(state.history.entries)) {
      return [];
    }

    return state.history.entries;
  }

  function setHistorySummary(statusText, updatedText, sourceText) {
    if (elements.status) {
      elements.status.textContent = statusText;
    }
    if (elements.updatedBadge) {
      elements.updatedBadge.textContent = updatedText;
    }
    if (elements.sourceBadge) {
      elements.sourceBadge.textContent = sourceText;
    }
  }

  function syncCurrencyButtons() {
    document.querySelectorAll("#history-currency-toggle [data-currency]").forEach((button) => {
      const isActive = button.dataset.currency === state.currency;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });
  }

  function formatMoney(value, currency) {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      maximumFractionDigits: value >= 1000 ? 0 : 2,
    }).format(value);
  }

  function compactMoney(value, currency) {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      notation: "compact",
      maximumFractionDigits: 1,
    }).format(value);
  }

  function formatShortDate(value) {
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    }).format(new Date(value));
  }

  function formatDateTime(value) {
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(value));
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }
})();
