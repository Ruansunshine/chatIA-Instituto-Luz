# Roda FORA do Docker, direto no Windows (host) - liga/desliga o plano de
# energia "Alto desempenho" sob pedido do backend Python (container), que
# alcanca o host via host.docker.internal (recurso do Docker Desktop).
#
# So' existe por causa do gargalo de CPU numa maquina sem GPU utilizavel: o
# Windows no plano "Equilibrado" limita a frequencia da CPU pra economizar
# energia, mesmo com o notebook na tomada - isso custa tok/s de verdade numa
# geracao longa e sustentada do Ollama. Enquanto essa janela ouve, ele liga
# "Alto desempenho" so' durante a geracao e volta pro "Equilibrado" assim que
# termina, sem deixar ligado o tempo todo a toa.
#
# Uso: abrir esse script numa janela do PowerShell (fica rodando, aberto)
# antes de testar o chat. Puramente opcional - se essa janela nao estiver
# aberta, o chat funciona normal, so' sem o boost (ver try/except no Python).
#
# Pra rodar: powershell -ExecutionPolicy Bypass -File power-boost-listener.ps1

$ALTO_DESEMPENHO = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
$EQUILIBRADO = "381b4222-f694-41f0-9685-ff5bb260df2e"
$PORTA = 5959

$listener = New-Object System.Net.HttpListener
# So "localhost" (ou "+"/"*", que exigem rodar como Administrador) e'
# aceito sem elevar permissao - por isso o lado Python forca o header
# "Host: localhost" na chamada, mesmo conectando via host.docker.internal
# (testado na pratica: registrar "host.docker.internal" direto quebra o
# Start() por falta de permissao).
$listener.Prefixes.Add("http://localhost:$PORTA/")
$listener.Start()
Write-Host "Power boost listener ouvindo em http://localhost:$PORTA (ligar/desligar) - deixa essa janela aberta." -ForegroundColor Green

try {
    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $caminho = $context.Request.Url.AbsolutePath

        if ($caminho -eq "/ligar") {
            powercfg /setactive $ALTO_DESEMPENHO
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Alto desempenho ligado (Ollama comecou a gerar)" -ForegroundColor Cyan
        } elseif ($caminho -eq "/desligar") {
            powercfg /setactive $EQUILIBRADO
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Voltou pro Equilibrado (Ollama terminou)" -ForegroundColor Cyan
        }

        $context.Response.StatusCode = 200
        $context.Response.Close()
    }
} finally {
    # Se a janela for fechada (Ctrl+C), garante que nao fica travado no
    # Alto desempenho ligado pra sempre.
    powercfg /setactive $EQUILIBRADO
    $listener.Stop()
}
