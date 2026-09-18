// Streaming da resposta da IA (servico Python) pro cliente, com log
// assincrono da conversa no MySQL e controle de "uma pergunta de IA por vez"
// - o Ollama so roda uma geracao simultanea mesmo, entao uma segunda
// pergunta recebe 429 na hora em vez de esperar escondida (ver index.ts,
// rota POST /chat).

import { registrarConversa } from "../db/queries";

// So pode mudar atraves de marcarIaOcupada/liberarIa (nunca atribuicao
// externa direta) - fica module-scoped de proposito.
let ocupada = false;

export function iaEstaOcupada(): boolean {
  return ocupada;
}

export function marcarIaOcupada(): void {
  ocupada = true;
}

export function liberarIa(): void {
  ocupada = false;
}

// Envia cada pedaco pro cliente sem atraso nenhum, e acumula em paralelo pra
// logar no banco SO depois que o stream inteiro ja saiu (nao segura o cliente).
export function streamComLog(
  corpo: ReadableStream<Uint8Array>,
  sessionId: string,
  pergunta: string,
  canal: "mysql" | "ia"
) {
  const leitor = corpo.getReader();
  const decoder = new TextDecoder();
  let acumulado = "";

  return new ReadableStream<Uint8Array>({
    async pull(controller) {
      try {
        const { done, value } = await leitor.read();
        if (done) {
          controller.close();
          if (canal === "ia") {
            liberarIa();
          }
          registrarConversa(sessionId, pergunta, acumulado, canal).catch((erro) =>
            console.error("Falha ao registrar conversa:", erro)
          );
          return;
        }
        acumulado += decoder.decode(value, { stream: true });
        controller.enqueue(value);
      } catch (erro) {
        // A conexao com o Python pode cair NO MEIO do stream (ex: container
        // reiniciado durante uma resposta em andamento) - sem esse catch,
        // iaOcupada ficava travado em "true" pra sempre (o reset so rodava
        // no caminho feliz, dentro do "if (done)"), derrubando TODA pergunta
        // seguinte com 429 mesmo com o Python livre de novo - aconteceu na
        // pratica, so um restart manual da API destravava.
        if (canal === "ia") {
          liberarIa();
        }
        controller.error(erro);
      }
    },
  });
}
