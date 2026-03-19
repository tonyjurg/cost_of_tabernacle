(function () {
  const TROY_OUNCES_PER_KILOGRAM = 32.150746568627;
  const POUNDS_PER_KILOGRAM = 2.2046226218;
  const SHEKELS_PER_TALENT = 3000;
  const GRAMS_PER_SHEKEL = 11.4;
  const LITERS_PER_HIN = 3.66;

  const FALLBACK_QUOTES = {
    XAU: { price: 4988.899902, updatedAt: "2026-03-16T09:31:35Z" },
    XAG: { price: 78.862999, updatedAt: "2026-03-16T09:31:34Z" },
    HG: { price: 5.787914, updatedAt: "2026-03-16T09:31:38Z" },
    usdToEur: 0.87138,
    fxDate: "2026-03-13",
  };

  const MATERIALS = [
    {
      id: "gold",
      name: "Gold",
      verses: "Exod. 38:24; 39:2-3, 8, 15-20, 25, 30",
      amountKind: "weightKg",
      amountText: "29 talents + 730 shekels",
      amountValue: kilogramsFromTalentsAndShekels(29, 730),
      priceType: "live-metal",
      liveSymbol: "XAU",
      pricingBasis: "Live Gold-API spot quote, converted from troy ounces to kilograms.",
      sourceLabel: "Gold-API",
      sourceUrl: "https://gold-api.com/",
    },
    {
      id: "silver",
      name: "Silver",
      verses: "Exod. 38:25-28",
      amountKind: "weightKg",
      amountText: "100 talents + 1,775 shekels",
      amountValue: kilogramsFromTalentsAndShekels(100, 1775),
      priceType: "live-metal",
      liveSymbol: "XAG",
      pricingBasis: "Live Gold-API spot quote, converted from troy ounces to kilograms.",
      sourceLabel: "Gold-API",
      sourceUrl: "https://gold-api.com/",
    },
    {
      id: "bronze",
      name: "Bronze",
      verses: "Exod. 38:29-31; 39:39",
      amountKind: "weightKg",
      amountText: "70 talents + 2,400 shekels",
      amountValue: kilogramsFromTalentsAndShekels(70, 2400),
      priceType: "derived-bronze",
      pricingBasis: "Estimated from live copper because there is no widely quoted public bronze spot feed.",
      sourceLabel: "Gold-API copper",
      sourceUrl: "https://gold-api.com/",
    },
    {
      id: "blue-yarn",
      name: "Blue yarn",
      verses: "Exod. 26:1-6, 31, 36; 27:16; 39:1-5, 8, 21-24, 29, 31",
      amountKind: "unspecified",
      amountText: "Used in at least 1,220 sq cubits of explicitly dimensioned woven panels, plus veil, entrance screen, and garments; yarn share not stated",
      priceType: "snapshot",
      unitPriceUsd: 7.3,
      priceUnit: "per 100 g skein",
      pricingBasis: "Current public retail proxy for blue wool yarn.",
      sourceLabel: "Patons Classic Wool Worsted Country Blue",
      sourceUrl: "https://www.woolandcompany.com/products/patons-classic-wool-worsted-country-blue",
    },
    {
      id: "purple-yarn",
      name: "Purple yarn",
      verses: "Exod. 26:1-6, 31, 36; 27:16; 39:1-5, 8, 21, 24, 29",
      amountKind: "unspecified",
      amountText: "Used in at least 1,220 sq cubits of explicitly dimensioned woven panels, plus veil, entrance screen, and garments; yarn share not stated",
      priceType: "snapshot",
      unitPriceUsd: 9.99,
      priceUnit: "per 50 g skein",
      pricingBasis: "Current public retail proxy for purple wool yarn.",
      sourceLabel: "Rauma Finullgarn 441 Purple",
      sourceUrl: "https://www.woolandcompany.com/products/rauma-finullgarn-441-purple",
    },
    {
      id: "scarlet-yarn",
      name: "Scarlet yarn",
      verses: "Exod. 26:1-6, 31, 36; 27:16; 39:1-5, 8, 24, 29",
      amountKind: "unspecified",
      amountText: "Used in at least 1,220 sq cubits of explicitly dimensioned woven panels, plus veil, entrance screen, and garments; yarn share not stated",
      priceType: "snapshot",
      unitPriceUsd: 7.3,
      priceUnit: "per 100 g skein",
      pricingBasis: "Current public retail proxy for scarlet wool yarn.",
      sourceLabel: "Patons Classic Wool Worsted Scarlet",
      sourceUrl: "https://www.woolandcompany.com/products/patons-classic-wool-worsted-scarlet",
    },
    {
      id: "fine-linen",
      name: "Fine twined linen",
      verses: "Exod. 26:1-6; 27:9-18; 39:2-5, 8, 24, 27-29",
      amountKind: "unspecified",
      amountText: "At least 2,620 sq cubits of fine-linen fabric have explicit dimensions, plus veil, entrance screen, and garments without full cut measurements",
      priceType: "snapshot",
      unitPriceUsd: 21.83,
      priceUnit: "per yard",
      pricingBasis: "Current public retail proxy for 100% linen fabric.",
      sourceLabel: "Fabrics-Store IL019 linen",
      sourceUrl: "https://fabrics-store.com/fabrics/linen-fabric-IL019-natural-middle/",
    },
    {
      id: "onyx",
      name: "Onyx shoulder stones",
      verses: "Exod. 39:6-7",
      amountKind: "count",
      amountText: "2 stones",
      amountValue: 2,
      priceType: "snapshot",
      unitPriceUsd: 1.95,
      priceUnit: "per stone",
      pricingBasis: "Current public retail proxy for a black onyx cabochon.",
      sourceLabel: "PMC Supplies black onyx cabochon",
      sourceUrl: "https://pmcsupplies.com/14x10-mm-black-onyx-oval-cabochon-per-piece.html",
    },
    {
      id: "breastpiece-stones",
      name: "Breastpiece stones",
      verses: "Exod. 39:10-14",
      amountKind: "count",
      amountText: "12 stones",
      amountValue: 12,
      priceType: "snapshot",
      unitPriceUsd: 1.0,
      priceUnit: "per stone",
      pricingBasis: "Current public mixed-cabochon proxy; the biblical set spans multiple gemstones.",
      sourceLabel: "Pioneer Gem assorted cabochons",
      sourceUrl: "https://www.pioneergem.com/CABOCHONS%2C%20ASSORTED.htm",
    },
    {
      id: "acacia-wood",
      name: "Acacia wood",
      verses: "Exod. 25:10, 23; 26:15-29; 27:1; 30:1; 39:33-39",
      amountKind: "unspecified",
      amountText: "48 boards and 15 bars are counted, and major furnishings have stated outer dimensions; total wood volume remains unstated",
      priceType: "snapshot",
      unitPriceUsd: 15.5,
      priceUnit: "per board foot",
      pricingBasis: "Current public retail proxy for acacia lumber.",
      sourceLabel: "Bell Forest Products acacia lumber",
      sourceUrl: "https://www.bellforestproducts.com/acacia/lumber/",
    },
    {
      id: "rams-skins",
      name: "Rams' skins dyed red",
      verses: "Exod. 26:14; 36:19; 39:34",
      amountKind: "unspecified",
      amountText: "1 dyed-rams'-skin covering layer; hide count and total area are not stated",
      priceType: "unavailable",
      pricingBasis: "No reliable current public source matched the biblical material closely enough.",
    },
    {
      id: "outer-hides",
      name: "Outer covering hides",
      verses: "Exod. 26:14; 36:19; 39:34",
      amountKind: "unspecified",
      amountText: "1 outermost covering layer; hide count and total area are not stated",
      priceType: "unavailable",
      pricingBasis: "Translations differ between sea cow hides, porpoise skins, and durable leather.",
    },
    {
      id: "olive-oil",
      name: "Olive oil for the light",
      verses: "Exod. 27:20-21; 39:37",
      amountKind: "unspecified",
      amountText: "Oil is commanded for continual lamp service, but no fixed volume is stated",
      priceType: "snapshot",
      unitPriceUsd: 14.99,
      priceUnit: "per liter",
      pricingBasis: "Current public grocery proxy for 1 liter olive oil.",
      sourceLabel: "Whole Foods Market Mediterranean EVOO (1L)",
      sourceUrl: "https://www.goodontop.com/cooking-oil/whole-foods-market-mediterranean-extra-virgin-olive-oil-1l.html",
    },
    {
      id: "myrrh",
      name: "Myrrh (anointing oil recipe)",
      verses: "Exod. 30:23-25; 39:38",
      amountKind: "weightKg",
      amountText: "500 shekels",
      amountValue: kilogramsFromShekels(500),
      priceType: "snapshot",
      unitPriceUsd: 143.30047,
      priceUnit: "per kg",
      pricingBasis: "Current public retail proxy for myrrh gum used as a stand-in for the flowing myrrh in Exodus 30.",
      sourceLabel: "Kitchen Closeout myrrh resin (1 lb)",
      sourceUrl: "https://kitchen-closeout.com/products/myrrh-resin-1lb-mr",
    },
    {
      id: "cinnamon",
      name: "Sweet cinnamon (anointing oil recipe)",
      verses: "Exod. 30:23-25; 39:38",
      amountKind: "weightKg",
      amountText: "250 shekels",
      amountValue: kilogramsFromShekels(250),
      priceType: "snapshot",
      unitPriceUsd: 17.262195,
      priceUnit: "per kg",
      pricingBasis: "Current public retail proxy for cinnamon sticks used as a stand-in for the spice in Exodus 30.",
      sourceLabel: "WebstaurantStore Regal cinnamon sticks (3 lb)",
      sourceUrl: "https://www.webstaurantstore.com/regal-cinnamon-sticks-3-lb/102708090.html",
    },
    {
      id: "calamus",
      name: "Aromatic cane / calamus (anointing oil recipe)",
      verses: "Exod. 30:23-25; 39:38",
      amountKind: "weightKg",
      amountText: "250 shekels",
      amountValue: kilogramsFromShekels(250),
      priceType: "snapshot",
      unitPriceUsd: 57.320188,
      priceUnit: "per kg",
      pricingBasis: "Current public retail proxy for calamus root powder used as a stand-in for the aromatic cane in Exodus 30.",
      sourceLabel: "Penn Herb calamus root powder (16 oz)",
      sourceUrl: "https://www.pennherb.com/calamus-root-powder-16-oz-077P16",
    },
    {
      id: "cassia",
      name: "Cassia (anointing oil recipe)",
      verses: "Exod. 30:24-25; 39:38",
      amountKind: "weightKg",
      amountText: "500 shekels",
      amountValue: kilogramsFromShekels(500),
      priceType: "snapshot",
      unitPriceUsd: 27.535737,
      priceUnit: "per kg",
      pricingBasis: "Current public retail proxy for cassia bark used as a stand-in for the cassia in Exodus 30.",
      sourceLabel: "NY Spice Shop cassia bark (1 lb)",
      sourceUrl: "https://nyspiceshop.com/products/cassia-bark-cinnamon-herbs",
    },
    {
      id: "anointing-oil-olive-oil",
      name: "Olive oil (anointing oil recipe)",
      verses: "Exod. 30:24-25; 39:38",
      amountKind: "volumeL",
      amountText: "1 hin",
      amountValue: litersFromHin(1),
      priceType: "snapshot",
      unitPriceUsd: 14.99,
      priceUnit: "per liter",
      pricingBasis: "Current public grocery proxy for olive oil; Exodus 30 specifies one hin in the anointing oil recipe.",
      sourceLabel: "Whole Foods Market Mediterranean EVOO (1L)",
      sourceUrl: "https://www.goodontop.com/cooking-oil/whole-foods-market-mediterranean-extra-virgin-olive-oil-1l.html",
    },
    {
      id: "sweet-incense",
      name: "Sweet incense",
      verses: "Exod. 30:34-36; 39:38",
      amountKind: "unspecified",
      amountText: "Four equal parts are named, but the total batch size is not stated",
      priceType: "unavailable",
      pricingBasis: "Exodus 30 gives equal parts for the incense ingredients, but not a total batch size or fully certain modern identifications for every ingredient.",
    },
  ];

  const state = {
    currency: "USD",
    bronzeFactor: 1.12,
    liveQuotes: {
      XAU: { ...FALLBACK_QUOTES.XAU },
      XAG: { ...FALLBACK_QUOTES.XAG },
      HG: { ...FALLBACK_QUOTES.HG },
      usdToEur: FALLBACK_QUOTES.usdToEur,
      fxDate: FALLBACK_QUOTES.fxDate,
    },
    liveStatus: {
      usingFallback: true,
      hasError: false,
      message: "Using built-in fallback quotes while live prices load.",
    },
  };

  const elements = {
    currencyToggle: document.querySelector("#currency-toggle"),
    bronzeFactor: document.querySelector("#bronze-factor"),
    refreshButton: document.querySelector("#refresh-prices"),
    liveStatus: document.querySelector("#live-status"),
    updatedBadge: document.querySelector("#calculator-updated-badge"),
    sourceBadge: document.querySelector("#calculator-source-badge"),
    tableLiveSummary: document.querySelector("#table-live-summary"),
    tableUpdatedSummary: document.querySelector("#table-updated-summary"),
    tableSourceSummary: document.querySelector("#table-source-summary"),
    documentedTotal: document.querySelector("#documented-total"),
    quantifiedRows: document.querySelector("#quantified-rows"),
    openRows: document.querySelector("#open-rows"),
    tableBody: document.querySelector("#materials-table"),
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

  elements.bronzeFactor.addEventListener("input", () => {
    const nextValue = Number.parseFloat(elements.bronzeFactor.value);
    if (Number.isFinite(nextValue)) {
      state.bronzeFactor = clamp(nextValue, 1, 2);
      render();
    }
  });

  elements.refreshButton.addEventListener("click", () => {
    refreshLiveQuotes();
  });

  syncCurrencyButtons();
  render();
  refreshLiveQuotes();

  function render() {
    const rows = MATERIALS.map((material) => buildRowView(material));
    const documentedTotal = rows.reduce((sum, row) => sum + (row.rowTotalUsd ?? 0), 0);
    const quantifiedCount = rows.filter((row) => row.rowTotalUsd !== null).length;
    const openCount = rows.filter((row) => row.amountKind === "unspecified").length;
    const updatedText = buildUpdatedBadgeText();
    const sourceText = "Sources: Gold-API metals, Frankfurter FX, current public retail and grocery proxies.";

    elements.documentedTotal.textContent = formatMoney(convertCurrency(documentedTotal), state.currency);
    elements.quantifiedRows.textContent = String(quantifiedCount);
    elements.openRows.textContent = String(openCount);
    if (elements.liveStatus) {
      elements.liveStatus.textContent = state.liveStatus.message;
    }
    if (elements.updatedBadge) {
      elements.updatedBadge.textContent = updatedText;
    }
    if (elements.sourceBadge) {
      elements.sourceBadge.textContent = sourceText;
    }
    elements.tableLiveSummary.textContent = state.liveStatus.message;
    elements.tableUpdatedSummary.textContent = updatedText;
    elements.tableSourceSummary.textContent = sourceText;
    elements.tableBody.innerHTML = rows.map(renderRowMarkup).join("");
  }

  async function refreshLiveQuotes() {
    setRefreshState(true);
    state.liveStatus = {
      usingFallback: true,
      hasError: false,
      message: "Refreshing live metal and FX feeds...",
    };
    render();

    const results = await Promise.allSettled([
      fetchJson("https://api.gold-api.com/price/XAU"),
      fetchJson("https://api.gold-api.com/price/XAG"),
      fetchJson("https://api.gold-api.com/price/HG"),
      fetchJson("https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR"),
    ]);

    const [gold, silver, copper, fx] = results;
    const fulfilled = results.filter((result) => result.status === "fulfilled").length;

    if (gold.status === "fulfilled") {
      state.liveQuotes.XAU = {
        price: gold.value.price,
        updatedAt: gold.value.updatedAt,
      };
    }

    if (silver.status === "fulfilled") {
      state.liveQuotes.XAG = {
        price: silver.value.price,
        updatedAt: silver.value.updatedAt,
      };
    }

    if (copper.status === "fulfilled") {
      state.liveQuotes.HG = {
        price: copper.value.price,
        updatedAt: copper.value.updatedAt,
      };
    }

    if (fx.status === "fulfilled") {
      state.liveQuotes.usdToEur = fx.value.rates.EUR;
      state.liveQuotes.fxDate = fx.value.date;
    }

    if (fulfilled === results.length) {
      state.liveStatus = {
        usingFallback: false,
        hasError: false,
        message: `Live feeds updated. Metals: ${relativeDateSummary([
          state.liveQuotes.XAU.updatedAt,
          state.liveQuotes.XAG.updatedAt,
          state.liveQuotes.HG.updatedAt,
        ])}. FX date: ${state.liveQuotes.fxDate}.`,
      };
    } else if (fulfilled > 0) {
      state.liveStatus = {
        usingFallback: false,
        hasError: false,
        message: `Partially refreshed ${fulfilled}/4 live feeds. Any missing values are still using the built-in March 2026 fallback snapshot.`,
      };
    } else {
      state.liveStatus = {
        usingFallback: true,
        hasError: true,
        message: "Live feeds were unavailable, so the table is using the built-in March 2026 fallback snapshot.",
      };
    }

    setRefreshState(false);
    render();
  }

  function buildRowView(material) {
    const unitPriceUsd = getUnitPriceUsd(material);
    const rowTotalUsd =
      unitPriceUsd !== null && material.amountKind !== "unspecified"
        ? unitPriceUsd * material.amountValue
        : null;

    return {
      ...material,
      unitPriceUsd,
      rowTotalUsd,
      formattedAmount: formatAmount(material),
      formattedUnitPrice:
        unitPriceUsd === null
          ? "Unavailable"
          : `${formatMoney(convertCurrency(unitPriceUsd), state.currency)} ${material.priceUnit ? `<span class="small-note">${escapeHtml(material.priceUnit)}</span>` : ""}`,
      formattedRowTotal:
        rowTotalUsd === null ? "N/A" : formatMoney(convertCurrency(rowTotalUsd), state.currency),
      pricingPill: getPricingPill(material.priceType),
    };
  }

  function getUnitPriceUsd(material) {
    if (material.priceType === "snapshot") {
      return material.unitPriceUsd;
    }

    if (material.priceType === "live-metal") {
      const quote = state.liveQuotes[material.liveSymbol];
      return quote.price * TROY_OUNCES_PER_KILOGRAM;
    }

    if (material.priceType === "derived-bronze") {
      const copperUsdPerPound = state.liveQuotes.HG.price;
      return copperUsdPerPound * POUNDS_PER_KILOGRAM * state.bronzeFactor;
    }

    return null;
  }

  function formatAmount(material) {
    if (material.amountKind === "weightKg") {
      return `${escapeHtml(material.amountText)} <span class="small-note">(${formatNumber(material.amountValue, 2)} kg)</span>`;
    }

    if (material.amountKind === "volumeL") {
      return `${escapeHtml(material.amountText)} <span class="small-note">(${formatNumber(material.amountValue, 2)} L)</span>`;
    }

    return escapeHtml(material.amountText);
  }

  function renderRowMarkup(row) {
    const sourceMarkup = row.sourceUrl
      ? `<a class="source-link" href="${row.sourceUrl}" target="_blank" rel="noreferrer">${escapeHtml(row.sourceLabel)}</a>`
      : "No current source linked";

    return `
      <tr>
        <td>
          <p class="material-title">${escapeHtml(row.name)}</p>
          <span class="material-meta">${escapeHtml(row.verses)}</span>
        </td>
        <td>${row.formattedAmount}</td>
        <td>
          <span class="value-strong">${row.formattedUnitPrice}</span>
        </td>
        <td>
          <span class="value-strong">${row.formattedRowTotal}</span>
        </td>
        <td>
          <span class="status-pill ${row.pricingPill.className}">${row.pricingPill.label}</span>
          <span class="small-note">${escapeHtml(row.pricingBasis)}</span>
          <span class="small-note">${sourceMarkup}</span>
        </td>
      </tr>
    `;
  }

  function getPricingPill(priceType) {
    if (priceType === "live-metal" || priceType === "derived-bronze") {
      return { className: "status-live", label: "Live" };
    }

    if (priceType === "snapshot") {
      return { className: "status-snapshot", label: "Snapshot" };
    }

    return { className: "status-gap", label: "Gap" };
  }

  function convertCurrency(usdValue) {
    if (state.currency === "EUR") {
      return usdValue * state.liveQuotes.usdToEur;
    }

    return usdValue;
  }

  function formatMoney(value, currency) {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      maximumFractionDigits: value >= 1000 ? 0 : 2,
    }).format(value);
  }

  function formatNumber(value, decimals) {
    return new Intl.NumberFormat("en-US", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  }

  function kilogramsFromTalentsAndShekels(talents, shekels) {
    const totalShekels = talents * SHEKELS_PER_TALENT + shekels;
    return (totalShekels * GRAMS_PER_SHEKEL) / 1000;
  }

  function kilogramsFromShekels(shekels) {
    return (shekels * GRAMS_PER_SHEKEL) / 1000;
  }

  function litersFromHin(hin) {
    return hin * LITERS_PER_HIN;
  }

  function syncCurrencyButtons() {
    document.querySelectorAll("[data-currency]").forEach((button) => {
      const isActive = button.dataset.currency === state.currency;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });
  }

  function setRefreshState(isLoading) {
    elements.refreshButton.disabled = isLoading;
    elements.refreshButton.textContent = isLoading ? "Refreshing..." : "Refresh live prices";
  }

  async function fetchJson(url) {
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), 8000);

    try {
      const response = await fetch(url, { signal: controller.signal });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } finally {
      window.clearTimeout(timeoutId);
    }
  }

  function relativeDateSummary(values) {
    const presentValues = values.filter(Boolean);
    if (!presentValues.length) {
      return "updated";
    }

    const newest = [...presentValues].sort().at(-1);
    return newest.replace("T", " ").replace("Z", " UTC");
  }

  function buildUpdatedBadgeText() {
    const newestMetalUpdate = [state.liveQuotes.XAU.updatedAt, state.liveQuotes.XAG.updatedAt, state.liveQuotes.HG.updatedAt]
      .filter(Boolean)
      .sort()
      .at(-1);

    if (state.liveStatus.usingFallback || state.liveStatus.hasError) {
      return `Fallback snapshot: ${formatIsoDateTime(newestMetalUpdate)} | FX ${state.liveQuotes.fxDate}`;
    }

    return `Live prices updated: ${formatIsoDateTime(newestMetalUpdate)} | FX ${state.liveQuotes.fxDate}`;
  }

  function formatIsoDateTime(value) {
    if (!value) {
      return "unknown";
    }

    return value.replace("T", " ").replace("Z", " UTC");
  }

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
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
