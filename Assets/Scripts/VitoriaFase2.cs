using UnityEngine;

// Script colocado no objeto de chegada da última fase (Fase 2): ao chegar, mostra a tela de vitória
public class VitoriaFase2 : MonoBehaviour
{
    public TelaVitoria tela; // Referência ao script TelaVitoria (arrastado pelo Inspector)

    // Chamado quando algum objeto entra na área de trigger (colisor marcado como "Is Trigger")
    private void OnTriggerEnter2D(Collider2D other)
    {
        // Verifica se quem entrou na área foi o Player
        if (other.CompareTag("Player"))
        {
            // Pede para a tela de vitória aparecer (toca o som e pausa o jogo)
            tela.MostrarVitoria();
        }
    }
}