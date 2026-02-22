import api from './api';

/**
 * Servicio global para la gestión de tickets y bitácoras técnicas
 * Centraliza la lógica de creación para evitar duplicación de código
 */

/**
 * Crea un ticket de manera global con todas las validaciones necesarias
 * @param {Object} params - Parámetros del ticket
 * @param {number} params.maquinaId - ID de la máquina
 * @param {string} params.maquinaUid - UID de la máquina (para descripción)
 * @param {string} params.categoria - Categoría del ticket
 * @param {string} params.subcategoria - Subcategoría del ticket
 * @param {string} params.prioridad - Prioridad (baja, media, alta, critica)
 * @param {string} params.descripcionBase - Descripción base del problema
 * @param {string} params.estadoMaquina - Estado de la máquina (DAÑADA, MANTENIMIENTO, etc)
 * @param {number} params.reportanteId - ID del usuario reportante
 * @param {string} params.notasSeguimiento - Notas adicionales
 * @param {boolean} params.incrementarContador - Si debe incrementar contador de fallas (default: true)
 * @param {boolean} params.actualizarEstado - Si debe actualizar estado de máquina (default: true)
 * @returns {Promise<Object>} Respuesta con el ticket creado y estado
 */
export async function crearTicket({
    maquinaId,
    maquinaUid,
    categoria,
    subcategoria,
    prioridad = 'media',
    descripcionBase,
    estadoMaquina = 'DAÑADA',
    reportanteId,
    notasSeguimiento = '',
    incrementarContador = true,
    actualizarEstado = true
}) {
    try {
        // 1. Validar que la máquina existe y no tiene tickets abiertos
        const validacion = await validarMaquinaParaTicket(maquinaId, maquinaUid);
        if (!validacion.valido) {
            return {
                exito: false,
                error: validacion.error,
                detalle: validacion.detalle
            };
        }

        // 2. Construir descripción completa con UID de máquina
        const descripcionCompleta = `${descripcionBase} | Máquina: ${maquinaUid}`;

        // 3. Crear el ticket
        const ticketData = {
            maquina: maquinaId,
            categoria,
            subcategoria,
            prioridad,
            descripcion_problema: descripcionCompleta,
            estado_maquina_reportado: estadoMaquina,
            estado_ciclo: 'abierto',
            reportante: reportanteId,
            esta_activo: true,
            notas_seguimiento: notasSeguimiento
        };

        const responseTicket = await api.post('tickets/', ticketData);

        if (!responseTicket.data || !responseTicket.data.id) {
            return {
                exito: false,
                error: 'Error al crear ticket',
                detalle: 'El ticket no se creó correctamente'
            };
        }

        const ticketCreado = responseTicket.data;

        // 4. Incrementar contador de fallas
        let contadorActualizado = null;
        if (incrementarContador) {
            try {
                const fallasResponse = await api.post(`maquinas/${maquinaId}/incrementar-fallas/`);
                contadorActualizado = fallasResponse.data.contador_fallas;
            } catch (errorFallas) {
                console.error('Error al incrementar contador_fallas:', errorFallas);
                // No es crítico, continuar
            }
        }

        // 5. Actualizar estado de la máquina si es necesario
        if (actualizarEstado) {
            try {
                await api.patch(`maquinas/${maquinaId}/`, {
                    estado_actual: estadoMaquina
                });
            } catch (errorEstado) {
                console.error('Error al actualizar estado de máquina:', errorEstado);
                // Retornar con advertencia
                return {
                    exito: true,
                    ticket: ticketCreado,
                    advertencia: 'Ticket creado pero no se pudo actualizar el estado de la máquina',
                    contadorFallas: contadorActualizado
                };
            }
        }

        return {
            exito: true,
            ticket: ticketCreado,
            contadorFallas: contadorActualizado
        };

    } catch (error) {
        console.error('Error en crearTicket:', error);
        return {
            exito: false,
            error: error.response?.data?.error || 'Error al crear el ticket',
            detalle: error.response?.data?.mensaje || error.response?.data?.detail || error.message
        };
    }
}

/**
 * Valida si una máquina puede tener un nuevo ticket
 * @param {number} maquinaId - ID de la máquina
 * @param {string} maquinaUid - UID de la máquina (para mensajes)
 * @returns {Promise<Object>} Objeto con validación
 */
async function validarMaquinaParaTicket(maquinaId, maquinaUid) {
    try {
        const responseTickets = await api.get('tickets/', {
            params: {
                maquina: maquinaId,
                esta_activo: true
            }
        });

        // Extraer el array de tickets
        let tickets = [];
        if (responseTickets.data) {
            if (responseTickets.data.results && Array.isArray(responseTickets.data.results)) {
                tickets = responseTickets.data.results;
            } else if (Array.isArray(responseTickets.data)) {
                tickets = responseTickets.data;
            }
        }

        // Filtrar solo tickets que no estén cerrados
        const ticketsAbiertos = tickets.filter(t => t.estado_ciclo !== 'cerrado');

        if (ticketsAbiertos.length > 0) {
            const folios = ticketsAbiertos.map(t => t.folio).join(', ');
            const plural = ticketsAbiertos.length > 1 ? 's' : '';

            return {
                valido: false,
                error: `Ticket${plural} ya abierto${plural}`,
                detalle: `La máquina "${maquinaUid}" ya tiene ${ticketsAbiertos.length} ticket${plural} activo${plural} (${folios}). Debe cerrar el ticket existente antes de crear uno nuevo.`
            };
        }

        return { valido: true };

    } catch (error) {
        console.error('Error al validar tickets de máquina:', error);
        return {
            valido: false,
            error: 'Error de validación',
            detalle: 'No se pudo verificar tickets existentes'
        };
    }
}

/**
 * Crea una entrada de bitácora técnica con todas las actualizaciones necesarias
 * @param {Object} params - Parámetros de la bitácora
 * @param {number} params.ticketId - ID del ticket
 * @param {number} params.maquinaId - ID de la máquina
 * @param {number} params.usuarioTecnicoId - ID del técnico
 * @param {string} params.tipoIntervencion - Tipo de intervención
 * @param {string} params.descripcionTrabajo - Descripción del trabajo realizado
 * @param {string} params.resultadoIntervencion - Resultado (exitoso, parcial, pendiente, sin_exito)
 * @param {string} params.estadoMaquinaResultante - Estado de la máquina después
 * @param {boolean} params.finalizaTicket - Si cierra el ticket
 * @param {string} params.explicacionCierre - Explicación del cierre (si aplica)
 * @param {Object} params.ticketActual - Objeto del ticket actual (para actualización)
 * @returns {Promise<Object>} Respuesta con la bitácora creada
 */
export async function crearBitacoraTecnica({
    ticketId,
    maquinaId,
    usuarioTecnicoId,
    tipoIntervencion,
    descripcionTrabajo,
    resultadoIntervencion,
    estadoMaquinaResultante,
    finalizaTicket = false,
    explicacionCierre = '',
    ticketActual = null
}) {
    try {
        // 1. Validaciones previas
        if (finalizaTicket) {
            if (resultadoIntervencion !== 'exitosa') {
                return {
                    exito: false,
                    error: 'No se puede cerrar',
                    detalle: 'El resultado debe ser EXITOSO para cerrar el ticket'
                };
            }
            if (estadoMaquinaResultante !== 'operativa') {
                return {
                    exito: false,
                    error: 'No se puede cerrar',
                    detalle: 'La máquina debe quedar OPERATIVA para cerrar el ticket'
                };
            }
        }

        // 2. Crear entrada de bitácora
        const bitacoraData = {
            ticket: ticketId,
            usuario_tecnico: usuarioTecnicoId,
            tipo_intervencion: tipoIntervencion,
            descripcion_trabajo: descripcionTrabajo,
            resultado_intervencion: resultadoIntervencion,
            estado_maquina_resultante: estadoMaquinaResultante,
            finaliza_ticket: finalizaTicket
        };

        const responseBitacora = await api.post('bitacora-tecnica/', bitacoraData);

        // 3. Actualizar estado de la máquina
        const estadoMaquinaMapping = {
            'operativa': 'OPERATIVA',
            'dañada_operativa': 'DAÑADA_OPERATIVA',
            'dañada': 'DAÑADA',
            'mantenimiento': 'MANTENIMIENTO'
        };

        const estadoMaquinaFinal = finalizaTicket
            ? 'OPERATIVA'
            : estadoMaquinaMapping[estadoMaquinaResultante];

        if (!maquinaId || isNaN(Number(maquinaId))) {
            return {
                exito: false,
                error: 'Error de validación',
                detalle: 'ID de máquina no es válido'
            };
        }

        await api.patch(`maquinas/${maquinaId}/`, {
            estado_actual: estadoMaquinaFinal
        });

        // 4. Actualizar ticket si se cierra
        if (finalizaTicket) {
            const ticketUpdate = ticketActual ? {
                ...ticketActual,
                estado_ciclo: 'cerrado',
                explicacion_cierre: explicacionCierre
            } : {
                estado_ciclo: 'cerrado',
                explicacion_cierre: explicacionCierre
            };

            await api.put(`tickets/${ticketId}/`, ticketUpdate);
        } else {
            // Solo actualizar a 'proceso' si está en 'abierto'
            if (ticketActual && ticketActual.estado_ciclo === 'abierto') {
                await api.patch(`tickets/${ticketId}/`, {
                    estado_ciclo: 'proceso'
                });
            }
        }

        return {
            exito: true,
            bitacora: responseBitacora.data,
            mensaje: finalizaTicket
                ? 'Bitácora guardada y ticket cerrado correctamente'
                : 'Bitácora guardada correctamente'
        };

    } catch (error) {
        console.error('Error en crearBitacoraTecnica:', error);
        return {
            exito: false,
            error: error.response?.data?.error || 'Error al guardar la bitácora',
            detalle: error.response?.data?.mensaje || error.response?.data?.detail || error.message
        };
    }
}

/**
 * Función compuesta para el "Ticket Express / Cierre Rápido"
 * Levanta un ticket y acto seguido genera su bitácora de resolución o proceso.
 * Usado por Técnicos para agilizar operaciones en piso.
 */
export async function crearTicketConBitacora({
    maquinaId,
    maquinaUid,
    categoria,
    subcategoria = 'Ticket Express',
    descripcionProblema,
    usuarioTecnicoId,
    tipoIntervencion,
    descripcionTrabajo,
    resultadoIntervencion, // 'exitosa', 'parcial', 'pendiente'
    estadoMaquinaResultante, // 'OPERATIVA', 'DAÑADA', etc.
    finalizaTicket = true, // Por defecto se asume que un cierre express finaliza el ticket
    explicacionCierre = ''
}) {
    try {
        // 1. Crear el Ticket base (asumimos prioridad media inicial y estado dañado)
        const ticketRes = await crearTicket({
            maquinaId,
            maquinaUid,
            categoria,
            subcategoria,
            prioridad: 'media',
            descripcionBase: descripcionProblema,
            estadoMaquina: 'DAÑADA',
            reportanteId: usuarioTecnicoId,
            notasSeguimiento: 'Creado vía Cierre Express',
            incrementarContador: true,
            actualizarEstado: false // Lo actualizaremos al final con la bitácora
        });

        if (!ticketRes.exito) {
            return ticketRes; // Propagar error de validación (ej. Ticket abierto existente)
        }

        const nuevoTicket = ticketRes.ticket;

        // 2. Crear la Bitácora vinculada al ticket recién nacido
        const bitacoraRes = await crearBitacoraTecnica({
            ticketId: nuevoTicket.id,
            maquinaId: maquinaId,
            usuarioTecnicoId: usuarioTecnicoId,
            tipoIntervencion,
            descripcionTrabajo,
            resultadoIntervencion,
            estadoMaquinaResultante: estadoMaquinaResultante.toLowerCase(),
            finalizaTicket,
            explicacionCierre,
            ticketActual: nuevoTicket // Pasa el objeto para forzar la transición a cerrado o proceso
        });

        if (!bitacoraRes.exito) {
            // Si la bitácora falló, el ticket quedó huérfano y abierto. 
            // Retornamos exito parcial para que UI sepa
            return {
                exito: false,
                alerta: true,
                error: 'Ticket creado pero bitácora falló',
                detalle: bitacoraRes.detalle || 'El ticket se generó con Folio ' + nuevoTicket.folio + ' pero no se pudo adjuntar el reporte técnico. Hágalo manualmente.',
                ticketFallido: nuevoTicket
            };
        }

        return {
            exito: true,
            ticket: nuevoTicket,
            bitacora: bitacoraRes.bitacora,
            mensaje: bitacoraRes.mensaje
        };

    } catch (error) {
        console.error('Error en crearTicketConBitacora:', error);
        return {
            exito: false,
            error: 'Excepción de Red/Servidor',
            detalle: error.message
        };
    }
}

/**
 * Tipos de ticket predefinidos para facilitar la creación
 */
export const TIPOS_TICKET = {
    PANICO: {
        categoria: 'otros',
        subcategoria: 'Ticket de Pánico',
        prioridad: 'critica',
        descripcionBase: 'TICKET DE PÁNICO - Requiere revisión técnica inmediata. Situación crítica reportada.',
        notasSeguimiento: 'Ticket creado mediante botón de pánico. Se requiere diagnóstico completo por parte del técnico.'
    },
    INCIDENCIA_RAPIDA: {
        categoria: 'otros',
        subcategoria: 'Incidencia Rápida',
        prioridad: 'critica',
        descripcionBase: 'INCIDENCIA RÁPIDA - Requiere revisión técnica inmediata.',
        notasSeguimiento: 'Ticket generado desde el módulo de gestión de máquinas. Se requiere diagnóstico completo por parte del técnico.'
    },
    NORMAL: {
        categoria: 'otros',
        subcategoria: 'Incidencia General',
        prioridad: 'media',
        descripcionBase: 'Incidencia reportada',
        notasSeguimiento: ''
    }
};

/**
 * Obtener datos para las gráficas del dashboard con filtros avanzados
 * @param {number} casinoId - ID del casino
 * @param {Object} filtros - Opciones de filtrado
 * @param {string} filtros.filtroTipo - 'dia', 'semana' o 'mes'
 * @param {string} filtros.fecha - 'YYYY-MM-DD'
 * @param {number} filtros.mes - 1-12
 * @param {number} filtros.semana - 1-4
 * @param {number} filtros.anio - YYYY
 * @returns {Promise<Object>} Datos para las gráficas
 */
export async function getDashboardChartsData(casinoId, filtros = {}) {
    try {
        const { filtroTipo = 'mes', fecha, mes, semana, anio } = filtros;

        const params = { filtro_tipo: filtroTipo };
        if (fecha) params.fecha = fecha;
        if (mes) params.mes = mes;
        if (semana) params.semana = semana;
        if (anio) params.anio = anio;

        const response = await api.get(`tickets/dashboard-charts/${casinoId}/`, {
            params
        });
        return response.data;
    } catch (error) {
        console.error('Error al obtener datos de gráficas:', error);
        throw error;
    }
}

export default {
    crearTicket,
    crearBitacoraTecnica,
    getDashboardChartsData,
    TIPOS_TICKET
};
