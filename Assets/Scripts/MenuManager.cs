using UnityEngine;
using UnityEngine.SceneManagement; // Necessário para trocar de cena

// Script do menu principal: controla os botões "Jogar" e "Sair"
public class MenuManager : MonoBehaviour
{
    // Chamado pelo botão "Jogar": carrega a cena do jogo
    public void StartGame()
    {
        // Carrega a cena chamada "Jogo" (ela precisa estar adicionada em File > Build Settings)
        SceneManager.LoadScene("Jogo");
    }

    // Chamado pelo botão "Sair": fecha o aplicativo
    public void QuitGame()
    {
        // Fecha o jogo exportado (no editor da Unity não faz nada, só funciona na build)
        Application.Quit();
    }
}