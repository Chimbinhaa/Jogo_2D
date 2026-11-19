# Análise do projeto e próximos passos

## Como o jogo está organizado

- **Motor:** Unity 6 (6000.1.4f1), URP 2D. Input: modo "Both" (o código usa o Input antigo `Input.GetAxis` / `Input.GetKeyDown`).
- **Cenas (ordem do Build):** `Menu` (0) → `Jogo` (1, fase 1) → `Jogo2` (2, fase 2).

| Script | Onde é usado | O que faz |
|---|---|---|
| `MenuManager` | Menu | Botões Jogar (carrega "Jogo") e Sair |
| `Player` | Jogo, Jogo2 | Andar, pular, morrer em espinho/inimigo |
| `MenuScene` | Jogo, Jogo2 | Pause (ESC), Game Over, Reiniciar, Voltar ao menu |
| `Inimigo` | Jogo (3x) | Patrulha de um lado pro outro |
| `PlataformaDissolvivel` | Jogo (2x) | Pisca e some, depois volta |
| `Vitoria` | Jogo | Ao tocar na casinha, vai pra fase 2 |
| `VitoriaFase2` + `TelaVitoria` | Jogo2 | Mostra a tela de vitória final |
| `BotaoJogarNovamente`, `BotaoSair` | Jogo | Botões da tela de vitória antiga da fase 1 |

Tags usadas: `Ground`, `Dano Espinho`, `Inimigo`, `Player`.

## Erros corrigidos

1. **Botão Sair não fechava o jogo exportado** (`BotaoSair.cs`) – só funcionava no editor. Agora chama `Application.Quit()` na build.
2. **Pulo falhando / pulo na parede** (`Player.cs`) – o `isGrounded` virava `false` ao sair de *qualquer* bloco de chão, mesmo estando em cima de outro; e encostar na lateral de um bloco `Ground` deixava pular de novo. Agora o player guarda os chãos que está pisando **por cima** (normal do contato).
3. **Pulo com altura diferente** – o pulo somava força à velocidade de queda. Agora a velocidade vertical é zerada antes do pulo (força em `forcaPulo`, editável no Inspector).
4. **Controles funcionando com o jogo pausado** – apertar Espaço no pause "guardava" um pulo para quando voltasse. Agora o Player ignora input com `Time.timeScale == 0`.
5. **ESC na tela de vitória destravava o jogo** (`MenuScene.cs`) – ESC → Continuar colocava o tempo em 1 por trás da vitória. O pause agora não abre se outra tela já parou o jogo.
6. **Game Over por cima do pause / chamado duas vezes** – agora fecha o painel de pause e só roda uma vez.
7. **Acentos quebrados** no comentário de `PlataformaDissolvivel.cs` (arquivo estava em ANSI, convertido para UTF‑8).
8. `using` desnecessários removidos (`Unity.VisualScripting.FullSerializer` no Player, `SceneManagement` no Inimigo).

> Abra o projeto na Unity e teste: andar, pular em plataformas lado a lado, encostar em paredes, pausar, morrer, vencer.

## Próximos passos (sugestão em ordem)

### 1. Arrumação (rápido)
- Renomear `MenuScene` para algo como `GerenciadorDeTelas` (ele não é o menu, é o pause/game over). Renomeie **pela Unity** para não perder as referências nas cenas.
- Em `Jogo.unity` ainda existe a tela de vitória antiga (`TelaVitoria` + botões) que não é mais usada, já que a casinha agora leva para a fase 2. Apagar ou reaproveitar.
- `Vitoria` e `VitoriaFase2` podem virar um único script com a opção "próxima fase ou tela de vitória".
- Dar nomes melhores aos sprites (`image-removebg-preview (8).png`, etc.).

### 2. Sensação de jogo (game feel)
- **Coyote time** (pular alguns milissegundos depois de sair da beirada) e **jump buffer**.
- Pulo de altura variável (soltar o Espaço cedo = pulo menor).
- Virar o sprite do Agenor para o lado que ele anda (`flipX`).
- Mover a física para `FixedUpdate` e usar `Rigidbody2D` nos inimigos.

### 3. Conteúdo e mecânicas
- Animações (parado, andando, pulando) com o Animator.
- Sons: pulo, morte, vitória, música de fundo (AudioSource).
- Checkpoints no meio da fase.
- Coletáveis (moedas) + contador na tela (UI com TextMeshPro).
- Vidas em vez de morrer direto; pular em cima do inimigo para matá-lo.
- Câmera com Cinemachine (segue suave e tem limites do mapa) em vez de ficar dentro do Player.

### 4. Organização do código
- Trocar o Input antigo pelo **novo Input System** (o arquivo `InputSystem_Actions` já existe no projeto) – permite usar controle.
- Criar um `GameManager` (Singleton) para controlar estado do jogo (jogando / pausado / game over / vitória) num lugar só.

### 5. Entrega
- Gerar a build (File → Build Profiles) para Windows ou WebGL e publicar no itch.io.
- Continuar o diário no README a cada aula e commitar com frequência.
