<#
.SYNOPSIS
    Ejecuta el comando Django de limpieza de notificaciones obsoletas.
    Diseñado para programarse en el Programador de Tareas de Windows (diario a las 00:00).

.DESCRIPTION
    1. Activa el entorno virtual de Python del proyecto.
    2. Lanza: python manage.py limpiar_notificaciones
    3. Guarda un log con fecha en BackEnd\logs\notificaciones\

.NOTAS
    Configuración rápida del Programador de Tareas (desde PowerShell como Administrador):

        $action  = New-ScheduledTaskAction `
                        -Execute "powershell.exe" `
                        -Argument "-NonInteractive -File `"D:\OT\BackEnd\scripts\limpiar_notificaciones.ps1`""
        $trigger = New-ScheduledTaskTrigger -Daily -At "00:00"
        $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
        Register-ScheduledTask `
            -TaskName   "NEXUS - Limpieza Notificaciones" `
            -Action     $action `
            -Trigger    $trigger `
            -Settings   $settings `
            -RunLevel   Highest `
            -Force

    Para ejecutarlo manualmente:
        Start-ScheduledTask -TaskName "NEXUS - Limpieza Notificaciones"

    Para ver el resultado del último log:
        Get-Content (Get-ChildItem D:\OT\BackEnd\logs\notificaciones\ | Sort-Object LastWriteTime | Select-Object -Last 1).FullName
#>

# ── Configuración ────────────────────────────────────────────────────────────
$PROJECT_ROOT  = "D:\OT\BackEnd"
$VENV_PYTHON   = "D:\OT\.venv\Scripts\python.exe"   # ← Ajusta si tu venv está en otra ruta
$MANAGE_PY     = Join-Path $PROJECT_ROOT "manage.py"
$LOG_DIR       = Join-Path $PROJECT_ROOT "logs\notificaciones"
$TIMESTAMP     = Get-Date -Format "yyyy-MM-dd_HH-mm"
$LOG_FILE      = Join-Path $LOG_DIR "limpieza_$TIMESTAMP.log"

# ── Preparar directorio de logs ──────────────────────────────────────────────
if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
}

# ── Ejecutar el comando Django ────────────────────────────────────────────────
$inicio = Get-Date
"[${inicio}] Iniciando limpieza de notificaciones..." | Tee-Object -FilePath $LOG_FILE

try {
    & $VENV_PYTHON $MANAGE_PY limpiar_notificaciones 2>&1 | Tee-Object -FilePath $LOG_FILE -Append

    $fin = Get-Date
    "[${fin}] Limpieza finalizada correctamente." | Tee-Object -FilePath $LOG_FILE -Append
    exit 0
}
catch {
    $fin = Get-Date
    "[${fin}] ERROR durante la limpieza: $_" | Tee-Object -FilePath $LOG_FILE -Append
    exit 1
}
finally {
    # Rotar logs: conservar solo los últimos 30 archivos para no acumular
    $archivos = Get-ChildItem $LOG_DIR -Filter "limpieza_*.log" | Sort-Object LastWriteTime
    if ($archivos.Count -gt 30) {
        $archivos | Select-Object -First ($archivos.Count - 30) | Remove-Item -Force
    }
}
