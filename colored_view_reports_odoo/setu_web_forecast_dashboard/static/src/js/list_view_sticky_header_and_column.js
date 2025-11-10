/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";

const originalComputeColumnWidths = ListRenderer.prototype.computeColumnWidthsFromContent;
const originalOnClickSortColumn = ListRenderer.prototype.onClickSortColumn;

function measureTextWidth(text, font) {
    if (!measureTextWidth._canvas) {
        measureTextWidth._canvas = document.createElement("canvas");
        measureTextWidth._ctx = measureTextWidth._canvas.getContext("2d");
    }
    const ctx = measureTextWidth._ctx;
    ctx.font = font;
    return ctx.measureText(text || "").width || 0;
}

patch(ListRenderer.prototype, {
    setup() {
        super.setup();
    },

    _onClickIcon(ev, record) {
        if (this.props?.list?.resModel !== "forecast.report.line") {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();

        const $clickedHeader = $(ev.currentTarget).closest("th");
        const columnIndex = $clickedHeader.index();

        $(this.__owl__.bdom.parentEl.querySelectorAll(".sticky-column")).removeClass("sticky-column");
        $(this.__owl__.bdom.parentEl.querySelectorAll(".clicked-header")).removeClass("clicked-header");
        $clickedHeader.addClass("clicked-header");

        const $tableHeaders = $(this.__owl__.bdom.parentEl.querySelectorAll(".o_list_table th"));
        const $tableRows = $(this.__owl__.bdom.parentEl.querySelectorAll(".o_list_table tr"));
        const $tfootRow = $(this.__owl__.bdom.parentEl.querySelectorAll(".o_list_table tfoot tr")[0]?.children || []);
        const $selectedFooterCells = $tfootRow.filter(`td:nth-child(-n+${columnIndex + 1})`);
        $selectedFooterCells.addClass("sticky-column");

        const $selectedColumns = $(this.__owl__.bdom.parentEl.querySelectorAll(`.o_data_row td:nth-child(-n+${columnIndex + 1})`));
        const $selectedHeaderCells = $tableHeaders.filter(`th:nth-child(-n+${columnIndex + 1})`);

        $tableHeaders.removeClass("sticky-column").css("left", "");
        $(this.__owl__.bdom.parentEl.querySelectorAll(".o_data_row td")).removeClass("sticky-column").css("left", "");

        $selectedColumns.addClass("sticky-column");
        $selectedHeaderCells.addClass("sticky-column");
        $tableHeaders.filter(".sticky-column").css("top", "0");

        const columnsToAdjust = columnIndex + 1;
        $tableRows.each(function (index, row) {
            const $headerCells = $(row).find("th");
            const $rowCells = $(row).find("td");
            for (let i = 0; i < columnsToAdjust; i++) {
                if ($headerCells.eq(i).length) $headerCells.eq(i).css("left", `${$headerCells.eq(i).position().left}px`);
                if ($rowCells.eq(i).length) $rowCells.eq(i).css("left", `${$rowCells.eq(i).position().left}px`);
            }
        });
    },

    // ✅ FIXED METHOD
    async onClickSortColumn(column) {
        // Only handle forecast.report.line; otherwise, call the normal logic directly.
        if (this.props?.list?.resModel !== "forecast.report.line") {
            return originalOnClickSortColumn.call(this, column);
        }

        // Call Odoo’s built-in sorting logic first
        await originalOnClickSortColumn.call(this, column);

        // Then reapply sticky column adjustments
        $(this.__owl__.bdom.parentEl.querySelectorAll(".sticky-column")).removeClass("sticky-column");
        $(this.__owl__.bdom.parentEl.querySelectorAll(".clicked-header")).removeClass("clicked-header");
        const $tableHeaders = $(this.__owl__.bdom.parentEl.querySelectorAll(".o_list_table th"));
        $tableHeaders.removeClass("sticky-column").css("left", "");
    },

    computeColumnWidthsFromContent(allowedWidth) {
        if (this.props?.list?.resModel !== "forecast.report.line") {
            return originalComputeColumnWidths.apply(this, arguments);
        }

        const columnWidths = originalComputeColumnWidths.apply(this, arguments);
        const table = this.tableRef?.el;
        if (!table) return columnWidths;

        const headers = [...table.querySelectorAll("thead th")];
        const rows = [...table.querySelectorAll("tbody tr")].slice(0, 20);

        headers.forEach((th, i) => {
            if (!th) return;
            if (th.classList.contains("o_list_button") || th.classList.contains("o_optional_columns_dropdown") || th.classList.contains("o_list_controller")) return;

            const cs = window.getComputedStyle(th);
            const font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
            const headerWidth = measureTextWidth((th.innerText || "").trim(), font);

            let contentWidth = 0;
            for (const row of rows) {
                const td = row.querySelector(`td:nth-child(${i + 1})`);
                if (!td) continue;
                const txt = (td.innerText || td.querySelector("input,textarea,select")?.value || "").trim();
                const w = measureTextWidth(txt, font);
                if (w > contentWidth) contentWidth = w;
            }

            const PADDING = 40;
            const MIN_COL = 92;
            const width = Math.max(Math.ceil(Math.max(headerWidth, contentWidth) + PADDING), MIN_COL);
            columnWidths[i] = Math.max(width, columnWidths[i] || 0);

            th.style.width = `${columnWidths[i]}px`;
            th.style.minWidth = `${columnWidths[i]}px`;
        });

        return columnWidths;
    },
});
