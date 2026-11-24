
/**
 * My Project Hub 2.0
 * 網站最後更新日期顯示
 */

// 真正修改網站內容時，更新這個日期
const SITE_LAST_UPDATED = "2026-11-24";

document.addEventListener("DOMContentLoaded", () => {
    const updateElement = document.getElementById("last-updated");

    if (!updateElement) return;

    updateElement.dateTime = SITE_LAST_UPDATED;
    updateElement.textContent = SITE_LAST_UPDATED;
});
