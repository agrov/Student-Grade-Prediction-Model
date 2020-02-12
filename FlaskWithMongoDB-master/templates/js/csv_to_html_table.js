var CsvToHtmlTable;
CsvToHtmlTable= CsvToHtmlTable || {};

CsvToHtmlTable = {
    init: function (options) {
        options = options || {};
        var csvPath = options.csvPath || "";
        var el = options.element || "table-container";
        var allowDownload = options.allowDownload || false;
        var csvOptions = options.csvOptions || {};
        var datatablesOptions = options.datatablesOptions || {};
        var customFormatting = options.customFormatting || [];
        var customTemplates = {};
        $.each(customFormatting, function (i, v) {
            var colIdx = v[0];
            var func = v[1];
            customTemplates[parseInt(colIdx)] = func;
        });

        var $table = $("<table class='table table-striped table-condensed' id='" + el + "-table'></table>");
        var $containerElement = $("#" + el);
        $containerElement.empty().append($table);

        $.when($.get(csvPath)).then(
            function (data) {
                var csvData = $.csv.toArrays(data, csvOptions);
                var $tableHead = $("<thead></thead>");
                var csvHeaderRow = csvData[0];
                var $tableHeadRow = $("<tr></tr>");
                for (var headerIdx = 0; headerIdx < csvHeaderRow.length; headerIdx++) {
                    $tableHeadRow.append($("<th></th>").text(csvHeaderRow[parseInt(headerIdx)]));
                }
                $tableHead.append($tableHeadRow);

                $table.append($tableHead);
                var $tableBody = $("<tbody></tbody>");

                for (var rowIdx = 1; rowIdx < csvData.length; rowIdx++) {
                    var $tableBodyRow = $("<tr></tr>");
                    for (var colIdx = 0; colIdx < csvData[parseInt(rowIdx)].length; colIdx++) {
                        var $tableBodyRowTd = $("<td></td>");
                        var cellTemplateFunc = customTemplates[parseInt(colIdx)];
                        if (cellTemplateFunc) {
                            $tableBodyRowTd.html(cellTemplateFunc(csvData[parseInt(rowIdx)][parseInt(colIdx)]));
                        } else {
                            $tableBodyRowTd.text(csvData[parseInt(rowIdx)][parseInt(colIdx)]);
                        }
                        $tableBodyRow.append($tableBodyRowTd);
                        $tableBody.append($tableBodyRow);
                    }
                }
                $table.append($tableBody);

                $table.DataTable(datatablesOptions);

                if (allowDownload) {
                    $containerElement.append("<p><a class='btn btn-info' href='" + csvPath + "'><i class='glyphicon glyphicon-download'></i> Download as CSV</a></p>");
                }
            });
    }
};
