using UnityEngine;

// Script da câmera: faz ela seguir um alvo (normalmente o player)
public class CameraFollow : MonoBehaviour
{
    public Transform alvo;                                  // Objeto que a câmera vai seguir (arrastar o player no Inspector)
    public Vector3 distancia = new Vector3(0f, 0f, -10f);   // Distância da câmera em relação ao alvo (o Z = -10 mantém a câmera 2D afastada da cena)
    public bool movimentoSuave = true;                      // Se true, a câmera acompanha com suavidade; se false, fica grudada no alvo
    public float velocidade = 5f;                           // Velocidade da suavização (quanto maior, mais rápido a câmera alcança o alvo)

    // LateUpdate roda depois de todos os Updates, evitando "tremida" porque o player já se moveu neste frame
    private void LateUpdate()
    {
        // Calcula a posição onde a câmera deveria estar: posição do alvo + a distância configurada
        Vector3 posicaoDesejada = alvo.position + distancia;

        // Verifica se o movimento suave está ligado
        if (movimentoSuave)
        {
            // Move a câmera gradualmente até a posição desejada (Lerp = interpolação linear)
            // Time.deltaTime deixa o movimento independente da taxa de quadros (FPS)
            transform.position = Vector3.Lerp(transform.position, posicaoDesejada, velocidade * Time.deltaTime);
        }
        else
        {
            // Sem suavização: a câmera vai direto para a posição desejada, acompanhando o alvo instantaneamente
            transform.position = posicaoDesejada;
        }
    }
}