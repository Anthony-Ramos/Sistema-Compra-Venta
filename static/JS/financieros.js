document.addEventListener("DOMContentLoaded", () => {

    // =========================
    // Formato auxiliar
    // =========================
    function formatNumero(valor) {
        return new Intl.NumberFormat("es-SV", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(parseFloat(valor) || 0);
    }

    // =========================
    // Función auxiliar para tablas
    // =========================
    function renderTable(id, headers, rows) {
        const tabla = document.getElementById(id);
        tabla.innerHTML = "";

        let thead = "<thead><tr>";
        headers.forEach(h => thead += `<th>${h}</th>`);
        thead += "</tr></thead>";

        let tbody = "<tbody>";
        rows.forEach(r => {
            tbody += "<tr>";
            r.forEach(c => tbody += `<td>${c}</td>`);
            tbody += "</tr>";
        });
        tbody += "</tbody>";

        tabla.innerHTML = thead + tbody;
    }

    // =========================
    // Función auxiliar para gráficas
    // =========================
    function renderizarGrafico(ctxId, tipo, labels, datasets, opciones = {}) {
        const ctx = document.getElementById(ctxId).getContext("2d");

        // Destruir gráfico anterior si existe
        if (window[ctxId] instanceof Chart) {
            window[ctxId].destroy();
        }

        window[ctxId] = new Chart(ctx, {
            type: tipo,
            data: { labels, datasets },
            options: Object.assign({
                responsive: true,
                plugins: { legend: { position: "bottom" } }
            }, opciones)
        });
    }

    // =========================
    // Cargar Reportes según meses
    // =========================
    function cargarReportes() {
        const inicioElem = document.getElementById("inicio");
        const finElem = document.getElementById("fin");

        const inicio = inicioElem ? inicioElem.value : "";
        const fin = finElem ? finElem.value : "";

        const query = `?inicio=${inicio}&fin=${fin}`;

        // 1. Estado de Resultados
        fetch(`/api/finanzas/estado_resultados${query}`)
            .then(res => res.json())
            .then(data => {
                const meses = data.map(r => r.mes);
                const ingresos = data.map(r => parseFloat(r.ingresos));
                const costos = data.map(r => parseFloat(r.costos));
                const utilidad = data.map(r => parseFloat(r.utilidad));

                renderizarGrafico(
                    "graficoResultados",
                    "bar",
                    meses,
                    [
                        { label: "Ingresos", data: ingresos, backgroundColor: "rgba(46, 204, 113, 0.7)" },
                        { label: "Costos", data: costos, backgroundColor: "rgba(231, 76, 60, 0.7)" },
                        { label: "Utilidad", data: utilidad, backgroundColor: "rgba(52, 152, 219, 0.7)" }
                    ]
                );

                renderTable("tablaResultados",
                    ["Mes", "Ingresos ($)", "Costos ($)", "Utilidad ($)"],
                    data.map(r => [
                        r.mes,
                        formatNumero(r.ingresos),
                        formatNumero(r.costos),
                        formatNumero(r.utilidad)
                    ])
                );
            });

        // 2. Margen de Rentabilidad
        fetch(`/api/finanzas/margen${query}`)
            .then(res => res.json())
            .then(data => {
                const meses = data.map(r => r.mes);
                const margen = data.map(r => parseFloat(r.margen));

                renderizarGrafico(
                    "graficoMargen",
                    "line",
                    meses,
                    [{ label: "Margen %", data: margen, borderColor: "rgba(155, 89, 182, 1)", fill: false }]
                );

                renderTable("tablaMargen",
                    ["Mes", "Margen (%)"],
                    data.map(r => [r.mes, formatNumero(r.margen)])
                );
            });

        // 3. Flujo de Caja
        fetch(`/api/finanzas/flujo${query}`)
            .then(res => res.json())
            .then(data => {
                const meses = data.map(r => r.mes);
                const ingresos = data.map(r => parseFloat(r.ingresos));
                const egresos = data.map(r => parseFloat(r.egresos));
                const flujo = data.map(r => parseFloat(r.flujo_neto));

                renderizarGrafico(
                    "graficoFlujo",
                    "bar",
                    meses,
                    [
                        { label: "Ingresos", data: ingresos, backgroundColor: "rgba(46, 204, 113, 0.7)" },
                        { label: "Egresos", data: egresos, backgroundColor: "rgba(231, 76, 60, 0.7)" },
                        { label: "Flujo Neto", data: flujo, backgroundColor: "rgba(52, 152, 219, 0.7)" }
                    ]
                );

                renderTable("tablaFlujo",
                    ["Mes", "Ingresos ($)", "Egresos ($)", "Flujo Neto ($)"],
                    data.map(r => [
                        r.mes,
                        formatNumero(r.ingresos),
                        formatNumero(r.egresos),
                        formatNumero(r.flujo_neto)
                    ])
                );
            });

        // 4. Punto de Equilibrio
        fetch(`/api/finanzas/equilibrio${query}`)
            .then(res => res.json())
            .then(data => {
                const meses = data.map(r => r.mes);
                const ingresos = data.map(r => parseFloat(r.ingresos));
                const costos = data.map(r => parseFloat(r.costos));

                renderizarGrafico(
                    "graficoEquilibrio",
                    "line",
                    meses,
                    [
                        { label: "Ingresos", data: ingresos, borderColor: "rgba(46, 204, 113, 1)", fill: false },
                        { label: "Costos", data: costos, borderColor: "rgba(231, 76, 60, 1)", fill: false }
                    ]
                );

                renderTable("tablaEquilibrio",
                    ["Mes", "Ingresos ($)", "Costos ($)", "Estado"],
                    data.map(r => [
                        r.mes,
                        formatNumero(r.ingresos),
                        formatNumero(r.costos),
                        r.estado
                    ])
                );
            });

        // 5. Crecimiento de Ventas
        fetch(`/api/finanzas/crecimiento${query}`)
            .then(res => res.json())
            .then(data => {
                const meses = data.map(r => r.mes);
                const ingresos = data.map(r => parseFloat(r.ingresos));
                const crecimiento = data.map(r => r.crecimiento ? parseFloat(r.crecimiento) : 0);

                renderizarGrafico(
                    "graficoCrecimiento",
                    "line",
                    meses,
                    [
                        { label: "Ingresos", data: ingresos, borderColor: "rgba(52, 152, 219, 1)", fill: false },
                        { label: "Crecimiento %", data: crecimiento, borderColor: "rgba(241, 196, 15, 1)", fill: false }
                    ]
                );

                renderTable("tablaCrecimiento",
                    ["Mes", "Ingresos ($)", "Crecimiento (%)"],
                    data.map(r => [
                        r.mes,
                        formatNumero(r.ingresos),
                        formatNumero(r.crecimiento ?? 0)
                    ])
                );
            });
    }

    // =========================
    // Actualizar link único del PDF general
    // =========================
    function actualizarLinkGeneralPDF() {
        const inicio = document.getElementById("inicio").value;
        const fin = document.getElementById("fin").value;
        const query = `?inicio=${inicio}&fin=${fin}`;

        const link = document.getElementById("pdfGeneral");
        if (link) {
            link.href = `/reportes/general/pdf${query}`;
        }
    }

    // =========================
    // Botones y eventos
    // =========================
    document.getElementById("btnGenerar").addEventListener("click", () => {
        cargarReportes();
        actualizarLinkGeneralPDF();
    });

    document.getElementById("inicio").addEventListener("change", actualizarLinkGeneralPDF);
    document.getElementById("fin").addEventListener("change", actualizarLinkGeneralPDF);

    // Cargar reportes y actualizar link al iniciar
    cargarReportes();
    actualizarLinkGeneralPDF();
});
