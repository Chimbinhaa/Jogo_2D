using UnityEngine;
using UnityEngine.SceneManagement; // Necessário para trocar de cena

// Script colocado em um objeto de chegada (trigger): leva o player para a próxima fase
public class Vitoria : MonoBehaviour
{
    public string proximaFase = ("Jogo2"); // Nome da próxima cena a ser carregada (pode ser alterado no Inspector)

    // Chamado quando algum objeto entra na área de trigger (colisor marcado como "Is Trigger")
    private void OnTriggerEnter2D(Collider2D other)
    {
        // Verifica se quem entrou na área foi o Player
        if (other.CompareTag("Player"))
        {
            Sons.Tocar("fase");                     // Toca o som de passagem de fase
            SceneManager.LoadScene(proximaFase);    // Carrega a próxima fase
        }
    }
}