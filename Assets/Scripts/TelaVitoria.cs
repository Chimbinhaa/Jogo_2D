using UnityEngine;

// Script que controla a tela de vitória (painel que aparece ao vencer o jogo)
public class TelaVitoria : MonoBehaviour
{
    public GameObject telaVitoria; // Painel (UI) de vitória, arrastado pelo Inspector

    // Chamado por outros scripts (ex.: VitoriaFase2) quando o player vence
    public void MostrarVitoria()
    {
        Sons.Tocar("vitoria");          // Toca o som de vitória
        telaVitoria.SetActive(true);    // Mostra o painel de vitória na tela
        Time.timeScale = 0f;            // Congela o jogo para o player não continuar se movendo
    }
}