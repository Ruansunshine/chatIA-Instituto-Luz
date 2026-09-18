# Sobe o projeto inteiro detectando sozinho se tem GPU NVIDIA disponivel -
# nao precisa saber de antemao se a maquina tem GPU ou nao, roda esse
# script em qualquer lugar (com GPU NVIDIA, sem GPU, com GPU de outro
# fabricante que o Ollama ainda nao suporta - Intel Iris Xe, Qualcomm
# Adreno etc, ver documentacao/escopo.md).
$temGpuNvidia = $false
try {
    $null = Get-Command nvidia-smi -ErrorAction Stop
    nvidia-smi | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $temGpuNvidia = $true
    }
} catch {
    $temGpuNvidia = $false
}

if ($temGpuNvidia) {
    Write-Host "GPU NVIDIA detectada - subindo com aceleracao de GPU." -ForegroundColor Green
    docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
} else {
    Write-Host "Nenhuma GPU NVIDIA detectada - subindo em CPU (funciona igual, so mais lento na IA)." -ForegroundColor Yellow
    docker compose up -d --build
}
