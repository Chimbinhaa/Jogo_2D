# Jogo_2D
Jogo para treinar versionamento de código com Git.

📄 Documentação: [Estética, animação, sons e hitboxes](Docs/ESTETICA_PIXEL_ART.md) · [Análise e próximos passos](PROXIMOS_PASSOS.md)

25/08 - Aprendi a usar os comandos e o Github, como por exemplo pull, commit, branch, repositórios e etc. Comecei um projeto na unity de um jogo plataforma 2D usando o Git. Adicionei um player (triangulo), um objeto quadrado (square) e adicionei um chão. Fizemos também uma branch pra testes no git e usamos merge para mesclar na main.

27/08 - Na aula de hoje aprendemos mais sobre Game Desing e UI, principalmente sobre mecânicas básicas, vi um vídeo sobre tais mecânicas aplicadas de diversas formas em jogos diferentes para compreendermos mais como elas funcionam e são usadas em jogos reais/famosos, e iremos começar a fazer o GDD (Game Desing Document) para nosso jogo manualmente no papel.

17/09 - Na aula de hoje criamos os primeiros scripts envolvendo a movimentação do player, a física dele e do chão, adicionando gravidade ao player e colisões nele e no chão, criando a base do nosso jogo, além de criarmos o pulo pro nosso player, porém ainda pulando infinitamente pois não definimos um limite.

22/09 - Hoje começamos a aula corrigindo o script da movimentação que erramos aula passada, também colocando a câmera dentro do player para quando o player andar a câmera segui-lo, também adicionamos o limite para o pulo do player, pois ele tava pulando infinitamente e conseguindo voar pelo mapa, então fizemos o script para ele pular apenas no chão, corrigindo assim esse problema.

24/09 - Na aula de hoje iremos acrescentar mais objetos e mais plataformas para o nosso mapa, aumentando nosso jogo e começando a polir ele, adicionando pequenos pulos e obstáculos, consequentemente aumentando o tamanho do mapa e a dificuldade do jogo. Assim começaremos a ter jogos "distintos" um dos outros, cada um com seu mapa e peculiaridades. No meu jogo em específico fiz as plataformas com espinhos (tem script) que matam o player e resetam o jogo, coloquei também uma imagem de background e um sprite pro personagem (Agenor).

29/09 - Na aula de hoje fiz muita coisa, adicionei sprite aos inimigos e aos espinhos, corrigi a hitbox deles, aumentei um pouco mais o tamanho da fase e fiz uma "casinha" no final dela onde terá a vitória, coloquei também 3 inimigos e fiz o script para eles andarem entre as plataformas, também aprendemos como usar PreFabs. Arrumei alguns bugs envolvendo as hitboxes e coloquei algumas paredes pra evitar que o player vá direto para o fim do jogo.

06/10 - Hoje continue codando e melhorando o jogo na unity, coloquei um "final" pra fase que quando o player chega aparece uma simples tela de vitória, também coloquei 2 botões nessa tela, o jogar novamente que funciona e reinicia o jogo do começo e o botão sair que também funciona e fecha o player no unity hub, fora que coloquei um sprite de troféu no final e um sprite mais bonito no player (Agenor). No final da aula consegui "finalizar" o jogo, Vinícius vistou e eu adicionei uma mecanica de plataformas que somem em 2 segundos e começam a piscar quando o player pisa nela.

15/10 Nesse dia de hoje foi adicionada ao projeto a cena de Game Over, que no meu projeto significa que o player alcançou o objetivo para subir de nível. Também foi criado o botão LEVEL UP, que permite ao jogador avançar para a próxima etapa do jogo depois de cumprir o objetivo da fase.

19/10 Neste dia começamos a desenvolver o HUD, o PAUSE e as TELAS DE MENU, além de dar continuidade ao GDD (Game Design Document). Todo esse planejamento foi feito no PAPEL, com rascunhos da organização dos elementos na tela e do funcionamento de cada interface antes de levar para a Unity.

20/10 Foram cedidas aulas para realizar o término das interfaces, ajustando o que havia sido planejado no papel e finalizando o visual e a organização das telas do projeto.

21/10 Início da Lista de Game Design, que foi copiada conforme o modelo passado em aula, para registrar as definições e características do jogo que estamos desenvolvendo.

22/10 O professor Vinicius visou (conferiu) a lista dos alunos, verificando quem já havia feito a atividade e o andamento de cada um.

23/10 Aulão de revisão da Avalia II, realizado no auditório, para revisar os conteúdos que seriam cobrados na avaliação.

03/11 Foram feitas mudanças e ajustes no projeto, corrigindo detalhes e melhorando partes do jogo que já estavam desenvolvidas.

05/11 Mundo Senai.

06/11 Mundo Senai.

10/11 Foram adicionadas ao jogo a cena de pause e a cena de game over, além da função no botão ESC, que pausa o jogo e abre o painel de pause. Ao apertar ESC novamente, o jogo é retomado.

12/11 Desenvolvemos no jogo a tela de menu, com os botões já com resultado explícito (por exemplo, “Jogar” inicia o jogo e “Sair” fecha o aplicativo). Também começamos a desenvolver a cena 2 e os atributos para expressar o fim do game, que indicam quando o jogador chegou ao final.

17/11 Foi desenvolvida no jogo a tela de vitória, que aparece quando o player chega ao objetivo final. Também foi feita a transição da cena 1 para a cena de vitória, passando pela cena 2, e outros ajustes necessários para o funcionamento dessas telas.

19/11 Hoje finalizamos o projeto do jogo para mostrar para o Vinícius, adicionando comentários nos scripts, retirando os bugs, lapidando o final do jogo e atualizando este README.
