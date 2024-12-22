function sortTable(columnIndex) {
    const table = document.getElementById("bidsTable");
    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.rows);
    const isAscending = tbody.dataset.sortOrder === "asc";

    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].innerText;
        const bText = b.cells[columnIndex].innerText;

        if (columnIndex === 0) { // Для времени ставки
            return isAscending ? new Date(aText) - new Date(bText) : new Date(bText) - new Date(aText);
        } else if (columnIndex === 3 || columnIndex === 4) { // Для суммы ставки и разницы ставок
            return isAscending ? parseFloat(aText) - parseFloat(bText) : parseFloat(bText) - parseFloat(aText);
        } else { // Для остальных столбцов
            return isAscending ? aText.localeCompare(bText) : bText.localeCompare(aText);
        }
    });

    // Удаляем старые строки и добавляем отсортированные
    rows.forEach(row => tbody.appendChild(row));

    // Меняем порядок сортировки
    tbody.dataset.sortOrder = isAscending ? "desc" : "asc";

    // Обновляем индикаторы сортировки
    updateSortIndicators(columnIndex, isAscending);
}

function updateSortIndicators(columnIndex, isAscending) {
    const headers = document.querySelectorAll("#bidsTable th");
    headers.forEach((header, index) => {
        const indicator = header.querySelector(".sort-indicator");
        if (index === columnIndex) {
            indicator.className = isAscending ? "sort-indicator sort-asc" : "sort-indicator sort-desc";
        } else {
            indicator.className = "sort-indicator"; // Сброс индикаторов для остальных заголовков
        }
    });
}

// Устанавливаем сортировку по умолчанию при загрузке страницы
document.addEventListener("DOMContentLoaded", function() {
    const tbody = document.getElementById("bidsTable").tBodies[0];
    tbody.dataset.sortOrder = "desc"; // Устанавливаем порядок по умолчанию
    sortTable(0); // Сортируем по первому столбцу (время ставки)
});