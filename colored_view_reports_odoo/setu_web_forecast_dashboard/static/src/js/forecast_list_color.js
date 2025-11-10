/** @odoo-module **/

console.log("✅ Forecast color watcher active");

function applyRowColors() {
    const rows = document.querySelectorAll(".setu_forecast_tree_view table.o_list_table tbody tr.o_data_row");
    if (!rows.length) return;

    rows.forEach(tr => {
        const colorCell = tr.querySelector('td[name="trigger_row_color"]');
        if (colorCell) {
            const colorValue = colorCell.textContent.trim();
            if (colorValue && /^#([0-9A-Fa-f]{3,8})$/.test(colorValue)) {
                tr.querySelectorAll("td").forEach(td =>
                    td.style.setProperty("background-color", colorValue, "important")
                );
            }
        }
    });
    console.log(`🎨 Colored ${rows.length} rows dynamically`);
}

function startWatching() {
    const table = document.querySelector(".setu_forecast_tree_view table.o_list_table");
    if (table) {
        console.log("✅ Forecast table detected!");
        applyRowColors();

        // Reapply on reload or pagination
        const observer = new MutationObserver(() => applyRowColors());
        observer.observe(table, { childList: true, subtree: true });
    } else {
        console.warn("⏳ Waiting for forecast table...");
    }
}

/**
 * 🧠 Core improvement:
 * Watch `.o_action_manager` for dynamic view changes
 * — called every time a new view (like list, kanban, form) is mounted
 */
function initWhenListRenders() {
    const actionManager = document.querySelector(".o_action_manager");
    if (!actionManager) {
        console.warn("⏳ Waiting for .o_action_manager...");
        setTimeout(initWhenListRenders, 300);
        return;
    }

    const observer = new MutationObserver(() => {
        const forecastView = document.querySelector(".setu_forecast_tree_view table.o_list_table");
        if (forecastView) {
            console.log("📄 List view appeared — running startWatching()");
            startWatching();
        }
    });

    // Observe view changes in main action area
    observer.observe(actionManager, { childList: true, subtree: true });
}

initWhenListRenders();
