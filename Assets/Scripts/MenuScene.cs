using UnityEngine;
using UnityEngine.SceneManagement; // Necessário para reiniciar a fase e voltar ao menu

// Script que controla os painéis de Pause e Game Over durante a fase
public class MenuScene : MonoBehaviour
{
    public GameObject painelPause;      // Painel (UI) que aparece quando o jogo é pausado
    public GameObject painelGameOver;   // Painel (UI) que aparece quando o player morre

    bool pausado = false;       // Indica se o jogo está pausado no momento
    bool jogoAcabou = false;    // Indica se o jogo já terminou (Game Over)

    void Start()
    {
        // Garante que os dois painéis comecem escondidos quando a fase iniciar
        painelPause.SetActive(false);
        painelGameOver.SetActive(false);
    }

    // Update is called once per frame
    // (Update é chamado uma vez por frame: aqui ele verifica se o jogador apertou ESC)
    void Update()
    {
        // Se o jogador apertou a tecla ESC neste frame
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            // Se já está pausado, o ESC despausa o jogo
            if (pausado)
            {
                Continuar();
            }
            // Se não está pausado, o ESC pausa o jogo
            else
            {
                Pausar();
            }
        }
    }

    // Pausa o jogo e mostra o painel de pause
    public void Pausar()
    {
        // Não pausa se o jogo acabou ou se outra tela (ex.: vitória) já parou o tempo.
        // Sem isso, apertar ESC na tela de vitória e depois "Continuar" voltava o jogo a rodar por trás.
        if (jogoAcabou == false && Time.timeScale > 0f)
        {
            pausado = true;                 // Marca que o jogo está pausado
            Sons.Tocar("pause");            // Toca o som de pause
            painelPause.SetActive(true);    // Mostra o painel de pause
            Time.timeScale = 0f;            // Congela o tempo do jogo (movimentos e física param)
        }
    }

    // Despausa o jogo e esconde o painel de pause (usado pelo botão "Continuar")
    public void Continuar()
    {
        pausado = false;                // Marca que o jogo não está mais pausado
        painelPause.SetActive(false);   // Esconde o painel de pause
        Time.timeScale = 1f;            // Devolve o tempo ao normal
    }

    // Mostra a tela de Game Over (chamado quando o player morre)
    public void MostrarGameOver()
    {
        if (jogoAcabou) return; // evita chamar duas vezes (ex.: tocou espinho e inimigo juntos)

        jogoAcabou = true;                  // Marca que o jogo acabou
        Sons.Tocar("morte");                // Toca o som de morte
        pausado = false;                    // Garante que não fique marcado como pausado
        painelPause.SetActive(false);       // Esconde o painel de pause, caso estivesse aberto
        painelGameOver.SetActive(true);     // Mostra o painel de Game Over
        Time.timeScale = 0f;                // Congela o jogo
    }

    // Reinicia a fase atual (usado por um botão de reiniciar)
    public void Reiniciar()
    {
        Time.timeScale = 1f; // Volta o tempo ao normal, senão a fase recarregaria congelada
        SceneManager.LoadScene(SceneManager.GetActiveScene().name); // Recarrega a cena atual
    }

    // Volta para o menu principal (usado por um botão de voltar ao menu)
    public void VoltarMenu()
    {
        Time.timeScale = 1f;            // Volta o tempo ao normal antes de trocar de cena
        SceneManager.LoadScene(0);      // Carrega a cena de índice 0 (menu principal, primeira no Build Settings)
    }
}