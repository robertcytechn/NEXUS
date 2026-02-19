<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
    // Referencia al DataTable para exportación
    dt: {
        type: Object,
        required: false,
        default: null
    },
    // Datos de la tabla para impresión
    datos: {
        type: Array,
        default: () => []
    },
    // Título del reporte
    tituloReporte: {
        type: String,
        default: 'Reporte'
    },
    // Nombre del archivo al exportar
    nombreArchivo: {
        type: String,
        default: 'export'
    },
    // Mostrar botón de exportación
    mostrarExportacion: {
        type: Boolean,
        default: true
    },
    // Mostrar botón de imprimir
    mostrarImprimir: {
        type: Boolean,
        default: true
    },
    // Mostrar botón de refrescar
    mostrarRefrescar: {
        type: Boolean,
        default: true
    },
    // Mostrar selector de columnas
    mostrarSelectorColumnas: {
        type: Boolean,
        default: true
    },
    // Columnas disponibles para mostrar/ocultar
    columnas: {
        type: Array,
        default: () => []
    },
    // Columnas seleccionadas (v-model)
    columnasSeleccionadas: {
        type: Array,
        default: () => []
    },
    // Mostrar buscador global
    mostrarBuscador: {
        type: Boolean,
        default: true
    },
    // Formato de fecha para el nombre del archivo
    incluirFechaEnNombre: {
        type: Boolean,
        default: true
    }
});

const emit = defineEmits(['refrescar', 'update:columnasSeleccionadas']);

const menuExportar = ref();
const popoverColumnas = ref();
const busquedaGlobal = ref('');

// Nombre del archivo con fecha
const obtenerNombreArchivo = () => {
    let nombre = props.nombreArchivo;
    if (props.incluirFechaEnNombre) {
        const fecha = new Date();
        const fechaString = fecha.toISOString().split('T')[0];
        nombre = `${nombre}_${fechaString}`;
    }
    return nombre;
};

// Exportar a CSV
const exportarCSV = () => {
    if (props.dt && props.dt.exportCSV) {
        props.dt.exportCSV();
    }
};

// Exportar a Excel mejorado con metadatos
const exportarExcel = () => {
    const columnasVisibles = props.columnas.filter(c => c.visible);
    
    if (!props.datos || props.datos.length === 0) {
        console.warn('No hay datos para exportar');
        return;
    }

    // Crear CSV mejorado con metadatos
    let csv = '\uFEFF'; // BOM para Excel UTF-8
    
    // Header con información de la aplicación
    csv += '"NEXUS - Core Nexus Manager"\n';
    csv += '"' + props.tituloReporte + '"\n';
    csv += '"Fecha de exportación: ' + new Date().toLocaleString('es-MX') + '"\n';
    csv += '"Total de registros: ' + props.datos.length + '"\n';
    csv += '\n'; // Línea vacía
    
    // Headers de columnas
    csv += columnasVisibles.map(col => '"' + col.label + '"').join(',') + '\n';
    
    // Datos
    props.datos.forEach(fila => {
        const valores = columnasVisibles.map(col => {
            let valor = fila[col.field];
            
            // Formatear valores
            if (typeof valor === 'boolean') {
                valor = valor ? 'Activo' : 'Inactivo';
            } else if (valor === null || valor === undefined) {
                valor = 'N/A';
            } else if (col.field.includes('fecha') || col.field.includes('_en')) {
                try {
                    valor = new Date(valor).toLocaleString('es-MX');
                } catch (e) {
                    // Si no es fecha válida, dejar como está
                }
            }
            
            // Escapar comillas y envolver en comillas
            return '"' + String(valor).replace(/"/g, '""') + '"';
        });
        
        csv += valores.join(',') + '\n';
    });
    
    // Descargar archivo
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', obtenerNombreArchivo() + '.csv');
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

// Exportar a PDF
const exportarPDF = async () => {
    imprimirTabla();
};

// Exportar a JSON
const exportarJSON = () => {
    const columnasVisibles = props.columnas.filter(c => c.visible);
    
    if (!props.datos || props.datos.length === 0) {
        console.warn('No hay datos para exportar');
        return;
    }

    // Crear objeto JSON con metadatos
    const exportData = {
        aplicacion: 'NEXUS - Core Nexus Manager',
        reporte: props.tituloReporte,
        fecha_exportacion: new Date().toISOString(),
        total_registros: props.datos.length,
        columnas: columnasVisibles.map(col => col.label),
        datos: props.datos.map(fila => {
            const registro = {};
            columnasVisibles.forEach(col => {
                registro[col.field] = fila[col.field];
            });
            return registro;
        })
    };
    
    // Descargar archivo JSON
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', obtenerNombreArchivo() + '.json');
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

// Imprimir solo la tabla con columnas seleccionadas
const imprimirTabla = () => {
    const columnasVisibles = props.columnas.filter(c => c.visible);
    
    if (!props.datos || props.datos.length === 0) {
        console.warn('No hay datos para imprimir');
        return;
    }

    // Logo SVG de NEXUS completo
    const logoSVG = '<svg viewBox="0 0 54 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 50px; height: 38px; vertical-align: middle;"><path fill-rule="evenodd" clip-rule="evenodd" d="M17.1637 19.2467C17.1566 19.4033 17.1529 19.561 17.1529 19.7194C17.1529 25.3503 21.7203 29.915 27.3546 29.915C32.9887 29.915 37.5561 25.3503 37.5561 19.7194C37.5561 19.5572 37.5524 19.3959 37.5449 19.2355C38.5617 19.0801 39.5759 18.9013 40.5867 18.6994L40.6926 18.6782C40.7191 19.0218 40.7326 19.369 40.7326 19.7194C40.7326 27.1036 34.743 33.0896 27.3546 33.0896C19.966 33.0896 13.9765 27.1036 13.9765 19.7194C13.9765 19.374 13.9896 19.0316 14.0154 18.6927L14.0486 18.6994C15.0837 18.9062 16.1223 19.0886 17.1637 19.2467ZM33.3284 11.4538C31.6493 10.2396 29.5855 9.52381 27.3546 9.52381C25.1195 9.52381 23.0524 10.2421 21.3717 11.4603C20.0078 11.3232 18.6475 11.1387 17.2933 10.907C19.7453 8.11308 23.3438 6.34921 27.3546 6.34921C31.36 6.34921 34.9543 8.10844 37.4061 10.896C36.0521 11.1292 34.692 11.3152 33.3284 11.4538ZM43.826 18.0518C43.881 18.6003 43.9091 19.1566 43.9091 19.7194C43.9091 28.8568 36.4973 36.2642 27.3546 36.2642C18.2117 36.2642 10.8 28.8568 10.8 19.7194C10.8 19.1615 10.8276 18.61 10.8816 18.0663L7.75383 17.4411C7.66775 18.1886 7.62354 18.9488 7.62354 19.7194C7.62354 30.6102 16.4574 39.4388 27.3546 39.4388C38.2517 39.4388 47.0855 30.6102 47.0855 19.7194C47.0855 18.9439 47.0407 18.1789 46.9536 17.4267L43.826 18.0518ZM44.2613 9.54743L40.9084 10.2176C37.9134 5.95821 32.9593 3.1746 27.3546 3.1746C21.7442 3.1746 16.7856 5.96385 13.7915 10.2305L10.4399 9.56057C13.892 3.83178 20.1756 0 27.3546 0C34.5281 0 40.8075 3.82591 44.2613 9.54743Z" fill="#06b6d4"/><mask id="mask0_1413_1551" style="mask-type: alpha" maskUnits="userSpaceOnUse" x="0" y="8" width="54" height="11"><path d="M27 18.3652C10.5114 19.1944 0 8.88892 0 8.88892C0 8.88892 16.5176 14.5866 27 14.5866C37.4824 14.5866 54 8.88892 54 8.88892C54 8.88892 43.4886 17.5361 27 18.3652Z" fill="#06b6d4"/></mask><g mask="url(#mask0_1413_1551)"><path d="M-4.673e-05 8.88887L3.73084 -1.91434L-8.00806 17.0473L-4.673e-05 8.88887ZM27 18.3652L26.4253 6.95109L27 18.3652ZM54 8.88887L61.2673 17.7127L50.2691 -1.91434L54 8.88887ZM-4.673e-05 8.88887C-8.00806 17.0473 -8.00469 17.0505 -8.00132 17.0538C-8.00018 17.055 -7.99675 17.0583 -7.9944 17.0607C-7.98963 17.0653 -7.98474 17.0701 -7.97966 17.075C-7.96949 17.0849 -7.95863 17.0955 -7.94707 17.1066C-7.92401 17.129 -7.89809 17.1539 -7.86944 17.1812C-7.8122 17.236 -7.74377 17.3005 -7.66436 17.3743C-7.50567 17.5218 -7.30269 17.7063 -7.05645 17.9221C-6.56467 18.3532 -5.89662 18.9125 -5.06089 19.5534C-3.39603 20.83 -1.02575 22.4605 1.98012 24.0457C7.97874 27.2091 16.7723 30.3226 27.5746 29.7793L26.4253 6.95109C20.7391 7.23699 16.0326 5.61231 12.6534 3.83024C10.9703 2.94267 9.68222 2.04866 8.86091 1.41888C8.45356 1.10653 8.17155 0.867278 8.0241 0.738027C7.95072 0.673671 7.91178 0.637576 7.90841 0.634492C7.90682 0.63298 7.91419 0.639805 7.93071 0.65557C7.93897 0.663455 7.94952 0.673589 7.96235 0.686039C7.96883 0.692262 7.97582 0.699075 7.98338 0.706471C7.98719 0.710167 7.99113 0.714014 7.99526 0.718014C7.99729 0.720008 8.00047 0.723119 8.00148 0.724116C8.00466 0.727265 8.00796 0.730446 -4.673e-05 8.88887ZM27.5746 29.7793C37.6904 29.2706 45.9416 26.3684 51.6602 23.6054C54.5296 22.2191 56.8064 20.8465 58.4186 19.7784C59.2265 19.2431 59.873 18.7805 60.3494 18.4257C60.5878 18.2482 60.7841 18.0971 60.9374 17.977C61.014 17.9169 61.0799 17.8645 61.1349 17.8203C61.1624 17.7981 61.1872 17.7781 61.2093 17.7602C61.2203 17.7512 61.2307 17.7427 61.2403 17.7348C61.2452 17.7308 61.2499 17.727 61.2544 17.7233C61.2566 17.7215 61.2598 17.7188 61.261 17.7179C61.2642 17.7153 61.2673 17.7127 54 8.88887C46.7326 0.0650536 46.7357 0.0625219 46.7387 0.0600241C46.7397 0.0592345 46.7427 0.0567658 46.7446 0.0551857C46.7485 0.0520238 46.7521 0.0489887 46.7557 0.0460799C46.7628 0.0402623 46.7694 0.0349487 46.7753 0.0301318C46.7871 0.0204986 46.7966 0.0128495 46.8037 0.00712562C46.818 -0.00431848 46.8228 -0.00808311 46.8184 -0.00463784C46.8096 0.00228345 46.764 0.0378652 46.6828 0.0983779C46.5199 0.219675 46.2165 0.439161 45.7812 0.727519C44.9072 1.30663 43.5257 2.14765 41.7061 3.02677C38.0469 4.79468 32.7981 6.63058 26.4253 6.95109L27.5746 29.7793ZM54 8.88887C50.2691 -1.91433 50.27 -1.91467 50.271 -1.91498C50.2712 -1.91506 50.272 -1.91535 50.2724 -1.9155C50.2733 -1.91581 50.274 -1.91602 50.2743 -1.91616C50.2752 -1.91643 50.275 -1.91636 50.2738 -1.91595C50.2714 -1.91515 50.2652 -1.91302 50.2552 -1.9096C50.2351 -1.90276 50.1999 -1.89078 50.1503 -1.874C50.0509 -1.84043 49.8938 -1.78773 49.6844 -1.71863C49.2652 -1.58031 48.6387 -1.377 47.8481 -1.13035C46.2609 -0.635237 44.0427 0.0249875 41.5325 0.6823C36.215 2.07471 30.6736 3.15796 27 3.15796V26.0151C33.8087 26.0151 41.7672 24.2495 47.3292 22.7931C50.2586 22.026 52.825 21.2618 54.6625 20.6886C55.5842 20.4011 56.33 20.1593 56.8551 19.986C57.1178 19.8993 57.3258 19.8296 57.4735 19.7797C57.5474 19.7548 57.6062 19.7348 57.6493 19.72C57.6709 19.7127 57.6885 19.7066 57.7021 19.7019C57.7089 19.6996 57.7147 19.6976 57.7195 19.696C57.7219 19.6952 57.7241 19.6944 57.726 19.6938C57.7269 19.6934 57.7281 19.693 57.7286 19.6929C57.7298 19.6924 57.7309 19.692 54 8.88887ZM27 3.15796C23.3263 3.15796 17.7849 2.07471 12.4674 0.6823C9.95717 0.0249875 7.73904 -0.635237 6.15184 -1.13035C5.36118 -1.377 4.73467 -1.58031 4.3155 -1.71863C4.10609 -1.78773 3.94899 -1.84043 3.84961 -1.874C3.79994 -1.89078 3.76474 -1.90276 3.74471 -1.9096C3.73469 -1.91302 3.72848 -1.91515 3.72613 -1.91595C3.72496 -1.91636 3.72476 -1.91643 3.72554 -1.91616C3.72593 -1.91602 3.72657 -1.91581 3.72745 -1.9155C3.72789 -1.91535 3.72874 -1.91506 3.72896 -1.91498C3.72987 -1.91467 3.73084 -1.91433 -4.673e-05 8.88887C-3.73093 19.692 -3.72983 19.6924 -3.72868 19.6929C-3.72821 19.693 -3.72698 19.6934 -3.72603 19.6938C-3.72415 19.6944 -3.72201 19.6952 -3.71961 19.696C-3.71482 19.6976 -3.70901 19.6996 -3.7022 19.7019C-3.68858 19.7066 -3.67095 19.7127 -3.6494 19.72C-3.60629 19.7348 -3.54745 19.7548 -3.47359 19.7797C-3.32589 19.8296 -3.11788 19.8993 -2.85516 19.986C-2.33008 20.1593 -1.58425 20.4011 -0.662589 20.6886C1.17485 21.2618 3.74125 22.026 6.67073 22.7931C12.2327 24.2495 20.1913 26.0151 27 26.0151V3.15796Z" fill="#06b6d4"/></g></svg>';

    // Crear HTML de la tabla
    let html = '<!DOCTYPE html><html><head><title>' + props.tituloReporte + '</title><style>';
    html += 'body { font-family: Arial, sans-serif; padding: 20px; }';
    html += '.header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #06b6d4; }';
    html += '.header-brand { display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 15px; }';
    html += '.header-brand-text { font-size: 18px; font-weight: bold; color: #06b6d4; }';
    html += '.header-subtitle { color: #666; font-size: 13px; margin-top: 5px; }';
    html += 'h1 { text-align: center; color: #333; margin: 15px 0; font-size: 24px; }';
    html += 'table { width: 100%; border-collapse: collapse; margin-top: 20px; }';
    html += 'th { background-color: #f8f9fa; color: #333; font-weight: bold; padding: 12px; text-align: left; border: 1px solid #ddd; }';
    html += 'td { padding: 10px 12px; border: 1px solid #ddd; }';
    html += 'tr:nth-child(even) { background-color: #f8f9fa; }';
    html += '.fecha { text-align: right; color: #666; font-size: 12px; margin-bottom: 10px; }';
    html += '.footer { margin-top: 30px; padding-top: 20px; border-top: 2px solid #ddd; text-align: center; color: #666; font-size: 12px; }';
    html += '.footer-brand { display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 10px; font-size: 14px; font-weight: bold; color: #06b6d4; }';
    html += '@media print { body { padding: 10px; } }';
    html += '</style></head><body>';
    
    // Header con logo y branding arriba
    html += '<div class="header">';
    html += '<div class="header-brand">';
    html += logoSVG;
    html += '<span class="header-brand-text">NEXUS |CNM|</span>';
    html += '</div>';
    html += '<div class="header-subtitle">Core Nexus Manager - Sistema de Gestión</div>';
    html += '</div>';
    
    html += '<div class="fecha">Fecha de impresión: ' + new Date().toLocaleString('es-MX') + '</div>';
    html += '<h1>' + props.tituloReporte + '</h1>';
    html += '<table><thead><tr>';

    // Agregar headers de columnas visibles
    columnasVisibles.forEach(col => {
        html += '<th>' + col.label + '</th>';
    });

    html += '</tr></thead><tbody>';

    // Agregar filas de datos
    props.datos.forEach(fila => {
        html += '<tr>';
        columnasVisibles.forEach(col => {
            let valor = fila[col.field];
            
            // Formatear valores especiales
            if (typeof valor === 'boolean') {
                valor = valor ? 'Activo' : 'Inactivo';
            } else if (valor === null || valor === undefined) {
                valor = 'N/A';
            } else if (col.field.includes('fecha') || col.field.includes('_en')) {
                // Formatear fechas
                try {
                    valor = new Date(valor).toLocaleString('es-MX');
                } catch (e) {
                    // Si no es una fecha válida, dejar como está
                }
            }
            
            html += '<td>' + valor + '</td>';
        });
        html += '</tr>';
    });

    html += '</tbody></table>';
    
    // Footer con logo y marca NEXUS
    html += '<div class="footer">';
    html += '<div>Documento generado por Core Nexus Manager</div>';
    html += '<div class="footer-brand">';
    html += logoSVG;
    html += '<span>NEXUS |CNM|</span>';
    html += '</div></div>';
    
    html += '</body></html>';

    // Abrir ventana de impresión
    const ventanaImpresion = window.open('', '_blank');
    if (ventanaImpresion) {
        ventanaImpresion.document.write(html);
        ventanaImpresion.document.close();
        ventanaImpresion.focus();
        
        // Esperar a que cargue e imprimir
        setTimeout(() => {
            ventanaImpresion.print();
            ventanaImpresion.close();
        }, 250);
    }
};

// Imprimir
const imprimir = () => {
    imprimirTabla();
};

// Refrescar datos
const refrescar = () => {
    emit('refrescar');
};

// Toggle visibilidad de columna
const toggleColumna = (columna) => {
    columna.visible = !columna.visible;
    emit('update:columnasSeleccionadas', props.columnas);
};

// Items del menú de exportación
const itemsExportar = computed(() => [
    {
        label: 'CSV',
        icon: 'pi pi-file',
        command: () => exportarCSV()
    },
    {
        label: 'Excel',
        icon: 'pi pi-file-excel',
        command: () => exportarExcel()
    },
    {
        label: 'PDF',
        icon: 'pi pi-file-pdf',
        command: () => exportarPDF()
    },
    {
        label: 'JSON',
        icon: 'pi pi-code',
        command: () => exportarJSON()
    }
]);

defineExpose({
    exportarCSV,
    exportarExcel,
    exportarPDF,
    imprimir,
    busquedaGlobal
});
</script>

<template>
    <div class="flex flex-wrap items-center justify-between gap-2 mb-4">
        <!-- Lado izquierdo: Título y Búsqueda -->
        <div class="flex items-center gap-3">
            <span class="text-xl font-bold">{{ tituloReporte }}</span>
            
            <IconField v-if="mostrarBuscador">
                <InputIcon>
                    <i class="pi pi-search" />
                </InputIcon>
                <InputText 
                    v-model="busquedaGlobal" 
                    placeholder="Buscar..." 
                    class="w-full md:w-80"
                />
            </IconField>
        </div>

        <!-- Lado derecho: Botones de acción -->
        <div class="flex items-center gap-2">
            <!-- Botón Refrescar -->
            <Button 
                v-if="mostrarRefrescar"
                icon="pi pi-refresh" 
                rounded 
                outlined
                severity="secondary"
                @click="refrescar"
                v-tooltip.top="'Refrescar datos'"
            />

            <!-- Selector de Columnas -->
            <Button 
                v-if="mostrarSelectorColumnas && columnas.length > 0"
                icon="pi pi-table" 
                rounded 
                outlined
                severity="secondary"
                @click="(event) => popoverColumnas.toggle(event)"
                v-tooltip.top="'Seleccionar columnas'"
            />
            <Popover ref="popoverColumnas">
                <div class="flex flex-col gap-3 w-60 p-3">
                    <div class="font-semibold text-sm border-b pb-2 mb-2">
                        Columnas Visibles
                    </div>
                    <div 
                        v-for="columna in columnas" 
                        :key="columna.field"
                        class="flex items-center gap-2 p-2 hover:bg-surface-100 dark:hover:bg-surface-800 rounded cursor-pointer"
                        @click="toggleColumna(columna)"
                    >
                        <Checkbox 
                            :modelValue="columna.visible" 
                            :binary="true"
                            class="pointer-events-none"
                        />
                        <span class="flex-1">
                            {{ columna.label }}
                        </span>
                    </div>
                </div>
            </Popover>

            <!-- Botones Imprimir y Exportar (ocultos en móvil) -->
            <div class="hidden md:flex items-center gap-2">
                <Button 
                    v-if="mostrarImprimir"
                    icon="pi pi-print" 
                    rounded 
                    outlined
                    severity="secondary"
                    @click="imprimir"
                    v-tooltip.top="'Imprimir'"
                />

                <Button 
                    v-if="mostrarExportacion"
                    icon="pi pi-download" 
                    rounded 
                    outlined
                    severity="success"
                    @click="menuExportar.toggle($event)"
                    v-tooltip.top="'Exportar'"
                />
                <Menu ref="menuExportar" :model="itemsExportar" :popup="true" />
            </div>

            <!-- Slot para botones personalizados -->
            <slot name="acciones-extra"></slot>
        </div>
    </div>
</template>

<!--
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                        📋 GUÍA DE USO: DataTableToolbar Component                            ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝

📌 DESCRIPCIÓN:
   Componente reutilizable de toolbar para DataTables con funcionalidades de:
   - Búsqueda global
   - Exportación (CSV, Excel, PDF)
   - Impresión con logo NEXUS
   - Selector de columnas visibles
   - Refrescar datos
   - Slot para botones personalizados

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 PROPS:

   🔹 dt (Object, optional)
      - Referencia al componente DataTable (para exportación)
      - Requiere: ref="dt" en el DataTable
      - Default: null

   🔹 datos (Array, required)
      - Array de datos que se muestran en la tabla
      - Usado para impresión y validación
      - Default: []

   🔹 tituloReporte (String)
      - Título que aparece en el toolbar y en documentos impresos
      - Default: 'Reporte'

   🔹 nombreArchivo (String)
      - Nombre base del archivo al exportar
      - Default: 'export'

   🔹 mostrarExportacion (Boolean)
      - Mostrar/ocultar botón de exportación
      - Default: true

   🔹 mostrarImprimir (Boolean)
      - Mostrar/ocultar botón de imprimir
      - Default: true

   🔹 mostrarRefrescar (Boolean)
      - Mostrar/ocultar botón de refrescar
      - Default: true

   🔹 mostrarSelectorColumnas (Boolean)
      - Mostrar/ocultar selector de columnas
      - Default: true

   🔹 columnas (Array, required for column selector)
      - Array de objetos con estructura:
        [
          { field: 'nombre', label: 'Nombre', visible: true },
          { field: 'edad', label: 'Edad', visible: false }
        ]
      - Default: []

   🔹 mostrarBuscador (Boolean)
      - Mostrar/ocultar campo de búsqueda global
      - Default: true

   🔹 incluirFechaEnNombre (Boolean)
      - Agregar fecha al nombre del archivo exportado
      - Default: true

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📤 EVENTOS:

   🔹 @refrescar
      - Se emite cuando el usuario hace clic en el botón refrescar
      - Debe implementar la lógica para recargar datos

   🔹 @update:columnasSeleccionadas
      - Se emite cuando el usuario cambia la visibilidad de columnas
      - Usa v-model:columnas-seleccionadas para sincronización automática

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 EJEMPLO DE USO COMPLETO:

1️⃣ PASO 1: Configurar el componente Vue

<script setup>
import { ref, onMounted, watch } from 'vue';
import api from '@/service/api';
import DataTableToolbar from '@/components/DataTableToolbar.vue';

// Referencias
const datos = ref([]);
const loading = ref(false);
const dt = ref(); // Referencia al DataTable
const toolbarRef = ref(); // Referencia al Toolbar

// Configurar filtros para búsqueda
const filtros = ref({
    global: { value: null, matchMode: 'contains' }
});

// Definir columnas (IMPORTANTE: incluir todas las columnas de tu tabla)
const columnas = ref([
    { field: 'id', label: 'ID', visible: false },           // Oculta por defecto
    { field: 'nombre', label: 'Nombre', visible: true },
    { field: 'email', label: 'Email', visible: true },
    { field: 'telefono', label: 'Teléfono', visible: true },
    { field: 'estado', label: 'Estado', visible: true },
    { field: 'creado_en', label: 'Fecha Creación', visible: false }
]);

// Sincronizar búsqueda del toolbar con DataTable
watch(() => toolbarRef.value?.busquedaGlobal, (nuevoValor) => {
    if (filtros.value.global) {
        filtros.value.global.value = nuevoValor;
    }
}, { deep: true });

// Función para cargar datos
const cargarDatos = async () => {
    loading.value = true;
    try {
        const response = await api.get('tu-endpoint/');
        datos.value = response.data;
    } catch (error) {
        console.error('Error:', error);
    } finally {
        loading.value = false;
    }
};

// Helper para verificar visibilidad de columna
const esColumnaVisible = (field) => {
    const columna = columnas.value.find(c => c.field === field);
    return columna ? columna.visible : true;
};

onMounted(() => {
    cargarDatos();
});
</script>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣ PASO 2: Implementar el template

<template>
    <div class="card">
        <!-- 🎛️ TOOLBAR 
        <DataTableToolbar
            ref="toolbarRef"
            :dt="dt"
            :datos="datos"
            titulo-reporte="Mi Reporte Personalizado"
            nombre-archivo="mi_archivo"
            :columnas="columnas"
            :mostrar-exportacion="true"
            :mostrar-imprimir="true"
            :mostrar-refrescar="true"
            :mostrar-selector-columnas="true"
            :mostrar-buscador="true"
            @refrescar="cargarDatos"
            v-model:columnas-seleccionadas="columnas"
        >
            <!-- Slot opcional para botones extra
            <template #acciones-extra>
                <Button 
                    icon="pi pi-plus" 
                    label="Nuevo"
                    rounded
                    severity="primary"
                    @click="crearNuevo"
                />
            </template>
        </DataTableToolbar>
        
        <!-- 📊 DATATABLE
        <DataTable 
            ref="dt"
            :value="datos" 
            :loading="loading"
            v-model:filters="filtros"
            :globalFilterFields="['nombre', 'email', 'telefono']"
            paginator 
            :rows="10" 
            :rowsPerPageOptions="[5, 10, 20, 50]"
            dataKey="id"
            filterDisplay="menu"
            showGridlines
            stripedRows
        >
            <template #empty>No se encontraron registros.</template>
            <template #loading>Cargando datos...</template>
            
            <!-- ⚠️ IMPORTANTE: Usar v-if con esColumnaVisible() para cada columna
            
            <Column 
                v-if="esColumnaVisible('id')"
                field="id" 
                header="ID" 
                sortable 
            />
            
            <Column 
                v-if="esColumnaVisible('nombre')"
                field="nombre" 
                header="Nombre" 
                sortable 
            >
                <template #body="{ data }">
                    <div class="font-semibold">{{ data.nombre }}</div>
                </template>
            </Column>
            
            <Column 
                v-if="esColumnaVisible('email')"
                field="email" 
                header="Email" 
                sortable 
            />
            
            <Column 
                v-if="esColumnaVisible('telefono')"
                field="telefono" 
                header="Teléfono" 
                sortable 
            />
            
            <Column 
                v-if="esColumnaVisible('estado')"
                field="estado" 
                header="Estado" 
                sortable 
            >
                <template #body="{ data }">
                    <Tag 
                        :value="data.estado ? 'Activo' : 'Inactivo'" 
                        :severity="data.estado ? 'success' : 'danger'" 
                    />
                </template>
            </Column>
            
            <Column 
                v-if="esColumnaVisible('creado_en')"
                field="creado_en" 
                header="Fecha Creación" 
                sortable 
            >
                <template #body="{ data }">
                    {{ new Date(data.creado_en).toLocaleString('es-MX') }}
                </template>
            </Column>
            
            <!-- Columna de acciones (siempre visible, no exportable)
            <Column header="Acciones" :exportable="false">
                <template #body="{ data }">
                    <div class="flex gap-2">
                        <Button 
                            icon="pi pi-pencil" 
                            size="small"
                            severity="info"
                            rounded 
                            outlined
                            @click="editar(data)"
                        />
                        <Button 
                            icon="pi pi-trash" 
                            size="small"
                            severity="danger"
                            rounded 
                            outlined
                            @click="eliminar(data)"
                        />
                    </div>
                </template>
            </Column>
        </DataTable>
    </div>
</template>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CHECKLIST DE IMPLEMENTACIÓN:

   ☑️ Importar DataTableToolbar component
   ☑️ Crear ref para DataTable (dt)
   ☑️ Crear ref para Toolbar (toolbarRef)
   ☑️ Definir array de columnas con { field, label, visible }
   ☑️ Configurar filtros con global.value
   ☑️ Implementar watch para sincronizar búsqueda
   ☑️ Pasar datos al toolbar mediante :datos="tuArrayDeDatos"
   ☑️ Pasar ref del DataTable mediante :dt="dt"
   ☑️ Agregar v-if="esColumnaVisible('campo')" en TODAS las columnas
   ☑️ Implementar función esColumnaVisible(field)
   ☑️ Conectar evento @refrescar con función de carga
   ☑️ Usar v-model:columnas-seleccionadas="columnas"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎨 CONFIGURACIONES COMUNES:

   📄 Solo búsqueda y refrescar:
   <DataTableToolbar
       ref="toolbarRef"
       :datos="datos"
       titulo-reporte="Mi Tabla"
       :mostrar-exportacion="false"
       :mostrar-imprimir="false"
       :mostrar-selector-columnas="false"
       @refrescar="cargarDatos"
   />

   📋 Toolbar completo con exportación:
   <DataTableToolbar
       ref="toolbarRef"
       :dt="dt"
       :datos="datos"
       :columnas="columnas"
       titulo-reporte="Reporte Completo"
       nombre-archivo="reporte_completo"
       @refrescar="cargarDatos"
       v-model:columnas-seleccionadas="columnas"
   />

   🔍 Solo búsqueda (sin botones):
   <DataTableToolbar
       ref="toolbarRef"
       :datos="datos"
       titulo-reporte="Búsqueda Simple"
       :mostrar-exportacion="false"
       :mostrar-imprimir="false"
       :mostrar-refrescar="false"
       :mostrar-selector-columnas="false"
   />

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ NOTAS IMPORTANTES:

   1. SINCRONIZACIÓN DE BÚSQUEDA:
      El watch() es obligatorio para sincronizar el input de búsqueda del toolbar
      con los filtros del DataTable. Sin esto, la búsqueda no funcionará.

   2. VISIBILIDAD DE COLUMNAS:
      Todas las columnas del DataTable deben tener v-if="esColumnaVisible('campo')"
      para que el selector de columnas funcione correctamente.

   3. EXPORTACIÓN:
      Para que funcione la exportación, debes pasar la referencia del DataTable
      mediante :dt="dt" y agregar ref="dt" en el DataTable.

   4. IMPRESIÓN:
      La impresión incluye automáticamente el logo NEXUS y solo imprime las
      columnas visibles. Los datos se formatean automáticamente (fechas, booleanos).

   5. CAMPOS GLOBALES DE BÚSQUEDA:
      Configura :globalFilterFields en el DataTable con los campos que quieres
      que sean buscables: :globalFilterFields="['nombre', 'email', 'telefono']"

   6. FORMATO DE FECHAS:
      Las columnas que incluyen 'fecha' o '_en' en su field se formatean
      automáticamente como fechas en la impresión.

   7. VALORES BOOLEANOS:
      Los campos booleanos se convierten automáticamente a 'Activo'/'Inactivo'
      en la impresión.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 TIPS Y MEJORES PRÁCTICAS:

   • Usa nombres descriptivos en el campo 'label' de las columnas
   • Mantén el field sincronizado con el nombre del campo en tu API
   • Oculta columnas técnicas (ID, timestamps) por defecto con visible: false
   • Implementa siempre la función esColumnaVisible() para mantener sincronía
   • Usa :exportable="false" en columnas de acciones
   • El slot #acciones-extra es ideal para botones de "Crear", "Importar", etc.
   • Personaliza el nombreArchivo según el módulo para mejor organización

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 FUNCIONALIDADES DEL TOOLBAR:

   🔄 Refrescar: Recarga los datos llamando al evento @refrescar
   
   🔍 Búsqueda: Filtra globalmente en los campos especificados en globalFilterFields
   
   📥 Exportar:
      • CSV: Exporta la tabla completa en formato CSV
      • Excel: Exporta la tabla completa (formato CSV compatible con Excel)
      • PDF: Abre diálogo de impresión con formato PDF
   
   🖨️ Imprimir: Genera documento HTML con:
      • Logo NEXUS en el footer
      • Solo columnas visibles
      • Fecha de impresión
      • Formato profesional con estilos
      • Branding "NEXUS |CNM|"
   
   📋 Selector de Columnas:
      • Muestra/oculta columnas dinámicamente
      • Checkboxes interactivos
      • Se sincroniza con v-if en las columnas
      • Persiste durante la sesión
   
   ➕ Acciones Extra: Slot para botones personalizados (crear, importar, etc.)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🐛 TROUBLESHOOTING:

   ❌ Problema: "La búsqueda no funciona"
   ✅ Solución: Verifica que hayas implementado el watch() para sincronizar
               toolbarRef.value?.busquedaGlobal con filtros.value.global.value

   ❌ Problema: "El selector de columnas no oculta las columnas"
   ✅ Solución: Asegúrate de que todas las columnas del DataTable tengan
               v-if="esColumnaVisible('nombreDelCampo')"

   ❌ Problema: "La exportación no funciona"
   ✅ Solución: Verifica que hayas pasado :dt="dt" al toolbar y que el
               DataTable tenga ref="dt"

   ❌ Problema: "Error: dt.exportCSV is not a function"
   ✅ Solución: El DataTable aún no está montado. Asegúrate de que dt.value
               no sea undefined cuando se llama la función.

   ❌ Problema: "La impresión sale en blanco"
   ✅ Solución: Verifica que :datos="tuArray" tenga valores y que las columnas
               tengan visible: true

   ❌ Problema: "El logo no se ve en la impresión"
   ✅ Solución: El logo está embebido como SVG inline, debería verse siempre.
               Verifica la configuración de impresión del navegador.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 EJEMPLO RÁPIDO (Código Mínimo):

<script setup>
import { ref, watch } from 'vue';
import DataTableToolbar from '@/components/DataTableToolbar.vue';

const datos = ref([]);
const dt = ref();
const toolbarRef = ref();
const filtros = ref({ global: { value: null, matchMode: 'contains' } });
const columnas = ref([
    { field: 'nombre', label: 'Nombre', visible: true },
    { field: 'email', label: 'Email', visible: true }
]);

watch(() => toolbarRef.value?.busquedaGlobal, (val) => {
    if (filtros.value.global) filtros.value.global.value = val;
}, { deep: true });

const esColumnaVisible = (field) => columnas.value.find(c => c.field === field)?.visible ?? true;
const cargarDatos = async () => { /* tu lógica */ };
</script>

<template>
    <div class="card">
        <DataTableToolbar
            ref="toolbarRef"
            :dt="dt"
            :datos="datos"
            titulo-reporte="Mi Tabla"
            :columnas="columnas"
            @refrescar="cargarDatos"
            v-model:columnas-seleccionadas="columnas"
        />
        
        <DataTable 
            ref="dt"
            :value="datos"
            v-model:filters="filtros"
            :globalFilterFields="['nombre', 'email']"
            paginator
        >
            <Column v-if="esColumnaVisible('nombre')" field="nombre" header="Nombre" sortable />
            <Column v-if="esColumnaVisible('email')" field="email" header="Email" sortable />
        </DataTable>
    </div>
</template>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ ¡LISTO! Ahora tienes un toolbar profesional y reutilizable para todos tus DataTables.

   Para más información sobre PrimeVue DataTable:
   👉 https://primevue.org/datatable/

   Desarrollado para Core Nexus Manager (CNM)
   🔷 NEXUS |CNM| - Sistema de Gestión de Casinos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-->
