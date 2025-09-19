document.addEventListener("DOMContentLoaded", () => {
    const btnGenerar = document.getElementById("btnGenerar");
    const fechaInicio = document.getElementById("fechaInicio");
    const fechaFin = document.getElementById("fechaFin");

    let grafico = null;

    function generarFechasCompletas(inicio, fin) {
        const inicioCompleto = inicio + "-01";
        const [anio, mes] = fin.split("-");
        const ultimoDia = new Date(anio, mes, 0).getDate();
        const finCompleto = fin + "-" + ultimoDia;
        return { inicioCompleto, finCompleto };
    }

    function generarMeses(inicio, fin) {
        let [anioInicio, mesInicio] = inicio.split("-").map(Number);
        let [anioFin, mesFin] = fin.split("-").map(Number);

        let fecha = new Date(anioInicio, mesInicio - 1);
        let fechaFin = new Date(anioFin, mesFin - 1);

        let meses = [];
        while (fecha <= fechaFin) {
            meses.push(fecha.toISOString().slice(0, 7)); // YYYY-MM
            fecha.setMonth(fecha.getMonth() + 1);
        }
        return meses;
    }

    function completarMeses(data, inicio, fin) {
        const mesesCompletos = generarMeses(inicio, fin);
        const dataDict = {};
        data.forEach(r => {
            dataDict[r.mes] = r;
        });

        return mesesCompletos.map(mes => {
            if (dataDict[mes]) {
                return dataDict[mes];
            }
            return {
                mes: mes,
                ingresos: 0.00,
                costos: 0.00,
                utilidad: 0.00,
                margen_rentabilidad: 0.00
            };
        });
    }

    function actualizarReporte(data) {
        if (!data || data.length === 0) {
            document.querySelector("#tablaRentabilidad tbody").innerHTML =
                `<tr><td colspan="5" style="text-align:center">No hay datos disponibles para el rango seleccionado.</td></tr>`;
            document.getElementById("conclusion").textContent = "No hay datos disponibles.";
            document.getElementById("fechaReporte").textContent =
                "Fecha de generación: " + new Date().toLocaleString("es-ES");
            if (grafico) grafico.destroy();
            return;
        }

        const meses = data.map(r => {
            const [anio, mes] = r.mes.split("-");
            const fecha = new Date(anio, mes - 1);
            return fecha.toLocaleDateString("es-ES", { month: "short", year: "numeric" });
        });

        const ingresos = data.map(r => parseFloat(r.ingresos));
        const costos = data.map(r => parseFloat(r.costos));
        const utilidad = data.map(r => parseFloat(r.utilidad));

        if (grafico) grafico.destroy();
        grafico = new Chart(document.getElementById("graficoRentabilidad"), {
            type: "bar",
            data: {
                labels: meses,
                datasets: [
                    { label: "Ingresos", data: ingresos, backgroundColor: "rgba(46,204,113,0.7)", borderColor: "rgba(39,174,96,1)", borderWidth: 1, borderRadius: 6 },
                    { label: "Costos", data: costos, backgroundColor: "rgba(231,76,60,0.7)", borderColor: "rgba(192,57,43,1)", borderWidth: 1, borderRadius: 6 },
                    { label: "Utilidad", data: utilidad, backgroundColor: "rgba(52,152,219,0.7)", borderColor: "rgba(41,128,185,1)", borderWidth: 1, borderRadius: 6 }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: "bottom" },
                    tooltip: { callbacks: { label: ctx => ` ${ctx.dataset.label}: $${ctx.raw.toFixed(2)}` } }
                },
                scales: { y: { beginAtZero: true, ticks: { callback: v => "$" + v } } }
            }
        });

        const tbody = document.querySelector("#tablaRentabilidad tbody");
        tbody.innerHTML = "";
        data.forEach(r => {
            const [anio, mes] = r.mes.split("-");
            const fecha = new Date(anio, mes - 1);
            const mesLabel = fecha.toLocaleDateString("es-ES", { month: "short", year: "numeric" });

            tbody.insertAdjacentHTML("beforeend", `
                <tr>
                    <td style="text-align:center">${mesLabel}</td>
                    <td>${Number(r.ingresos).toFixed(2)}</td>
                    <td>${Number(r.costos).toFixed(2)}</td>
                    <td>${Number(r.utilidad).toFixed(2)}</td>
                    <td>${Number(r.margen_rentabilidad).toFixed(2)}%</td>
                </tr>
            `);
        });

        const totalUtilidad = utilidad.reduce((a, b) => a + b, 0);
        const mesMax = meses[utilidad.indexOf(Math.max(...utilidad))];
        const mesMin = meses[utilidad.indexOf(Math.min(...utilidad))];

        let conclusion = "";
        if (totalUtilidad > 0) {
            conclusion = `La empresa es rentable, con una utilidad total de $${totalUtilidad.toFixed(2)}. El mejor mes fue ${mesMax}, y el de menor rendimiento fue ${mesMin}.`;
        } else if (totalUtilidad < 0) {
            conclusion = `Se reporta una pérdida total de $${Math.abs(totalUtilidad).toFixed(2)}. El mes más desfavorable fue ${mesMin}.`;
        } else {
            conclusion = "Los ingresos y costos se equilibraron, sin ganancias ni pérdidas.";
        }

        document.getElementById("conclusion").textContent = conclusion;
        document.getElementById("fechaReporte").textContent = "Fecha de generación: " + new Date().toLocaleString("es-ES");
    }

    btnGenerar.addEventListener("click", () => {
        if (!fechaInicio.value || !fechaFin.value) {
            alert("Seleccione un rango de fechas válido.");
            return;
        }

        const { inicioCompleto, finCompleto } = generarFechasCompletas(
            fechaInicio.value,
            fechaFin.value
        );

        // --- API JSON ---
        fetch(`/api/reportes/rentabilidad?inicio=${inicioCompleto}&fin=${finCompleto}`)
            .then(res => res.json())
            .then(data => {
                data = completarMeses(data, fechaInicio.value, fechaFin.value);
                actualizarReporte(data);
            })
            .catch(err => {
                console.error("Error al obtener datos:", err);
                document.getElementById("conclusion").textContent = "Error al obtener los datos.";
            });

        // --- Actualizar link del PDF ---
        const btnPdf = document.getElementById("btnPdf");
        btnPdf.href = `/reportes/rentabilidad/pdf?inicio=${inicioCompleto}&fin=${finCompleto}`;
    });
});
