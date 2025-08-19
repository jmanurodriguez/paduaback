# Script para probar todos los endpoints del backend
# Ejecutar desde PowerShell en la carpeta del backend

Write-Host "=== PROBANDO BACKEND CASA DE PADUA ===" -ForegroundColor Green
Write-Host ""

# Endpoint raíz
Write-Host "1. Probando endpoint raíz..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/" -Method Get
    Write-Host "✓ Respuesta: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Endpoints de básquet
Write-Host "2. Probando endpoints de básquet..." -ForegroundColor Yellow
try {
    $basquet = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/standings/basquet" -Method Get
    if ($basquet.standings) {
        Write-Host "✓ Posiciones de básquet: $($basquet.standings.Count) equipos encontrados" -ForegroundColor Green
        Write-Host "  Última actualización: $($basquet.last_update)" -ForegroundColor Cyan
    } else {
        Write-Host "✗ No se encontraron datos de posiciones" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Error en básquet: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Endpoints de voley
Write-Host "3. Probando endpoints de voley..." -ForegroundColor Yellow

$voley_endpoints = @(
    @{name="Tira A"; url="http://127.0.0.1:8000/api/standings/voley/tira-a"},
    @{name="Tira B"; url="http://127.0.0.1:8000/api/standings/voley/tira-b"},
    @{name="Primera"; url="http://127.0.0.1:8000/api/standings/voley/primera"}
)

foreach ($endpoint in $voley_endpoints) {
    try {
        $response = Invoke-RestMethod -Uri $endpoint.url -Method Get
        if ($response.standings) {
            Write-Host "✓ $($endpoint.name): $($response.standings.Count) equipos" -ForegroundColor Green
        } else {
            Write-Host "△ $($endpoint.name): Sin datos disponibles" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "✗ $($endpoint.name): Error - $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host ""

# Endpoints de fixtures
Write-Host "4. Probando endpoints de fixtures..." -ForegroundColor Yellow

$fixture_endpoints = @(
    @{name="Básquet"; url="http://127.0.0.1:8000/api/fixtures/basquet"},
    @{name="Voley Tira A"; url="http://127.0.0.1:8000/api/fixtures/voley/tira-a"},
    @{name="Voley Tira B"; url="http://127.0.0.1:8000/api/fixtures/voley/tira-b"},
    @{name="Voley Primera"; url="http://127.0.0.1:8000/api/fixtures/voley/primera"}
)

foreach ($endpoint in $fixture_endpoints) {
    try {
        $response = Invoke-RestMethod -Uri $endpoint.url -Method Get
        if ($response.fixtures) {
            Write-Host "✓ $($endpoint.name): $($response.fixtures.Count) próximos partidos" -ForegroundColor Green
        } else {
            Write-Host "△ $($endpoint.name): Sin próximos partidos" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "✗ $($endpoint.name): Error - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== PRUEBA COMPLETADA ===" -ForegroundColor Green
Write-Host "El backend está disponible en: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Documentación automática en: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
