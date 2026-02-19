import { onMounted, onUpdated, nextTick } from 'vue';

/**
 * Composable para hacer DataTables responsive en móvil
 * Agrega automáticamente data-label a las celdas basándose en los headers
 * 
 * @param {Ref} dtRef - Referencia al componente DataTable
 * @returns {Function} updateLabels - Función para actualizar manualmente los labels
 */
export function useResponsiveDataTable(dtRef) {
    
    const updateLabels = () => {
        nextTick(() => {
            if (!dtRef.value) return;
            
            // Obtener el elemento DOM del DataTable
            const tableElement = dtRef.value.$el?.querySelector('table') || 
                                 dtRef.value.$el?.querySelector('.p-datatable-table');
            
            if (!tableElement) return;

            // Obtener headers
            const headers = Array.from(tableElement.querySelectorAll('thead th'))
                .map(th => th.textContent.trim());

            if (headers.length === 0) return;

            // Aplicar data-label a cada celda
            const rows = tableElement.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                cells.forEach((cell, index) => {
                    if (headers[index] && headers[index] !== '') {
                        cell.setAttribute('data-label', headers[index]);
                    }
                });
            });
        });
    };

    // Actualizar labels cuando el componente se monta
    onMounted(() => {
        updateLabels();
    });

    // Actualizar labels cuando cambian los datos
    onUpdated(() => {
        updateLabels();
    });

    return {
        updateLabels
    };
}
