using UnityEngine;
using UnityEngine.SceneManagement; // Necessário para carregar e recarregar cenas

// Script do botão "Jogar Novamente": reinicia a fase que está sendo jogada
public class BotaoJogarNovamente : MonoBehaviour
{
    // Método público para ser chamado pelo evento OnClick do botão na Unity
    public void JogarNovamente()
    {
        // Volta o tempo ao normal (caso o jogo estivesse pausado ou em Game Over com timeScale = 0)
        Time.timeScale = 1f;

        // Recarrega a cena atual pelo nome, reiniciando a fase do zero
        SceneManager.LoadScene(SceneManager.GetActiveScene().name);
    }
}