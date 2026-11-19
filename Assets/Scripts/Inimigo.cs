using UnityEngine;

// Script do inimigo: ele patrulha, andando para a direita e para a esquerda em um trecho fixo
public class Inimigo : MonoBehaviour
{
    public float velocidade = 2f;   // Velocidade com que o inimigo anda
    public float distancia = 3f;    // Distância máxima que ele anda para cada lado a partir do ponto inicial

    private Vector3 inicio;         // Guarda a posição inicial do inimigo (centro da patrulha)
    private bool indo = true;       // Controla a direção: true = indo para a direita, false = voltando para a esquerda

    void Start()
    {
        // Salva a posição onde o inimigo começa, para usar como referência da patrulha
        inicio = transform.position;
    }

    void Update()
    {
        // Se o inimigo está indo para a direita
        if (indo)
        {
            // Move o inimigo para a direita (Time.deltaTime deixa o movimento suave em qualquer FPS)
            transform.Translate(Vector2.right * velocidade * Time.deltaTime);

            // Se chegou (ou passou) do limite direito da patrulha, passa a voltar para a esquerda
            if (transform.position.x >= inicio.x + distancia)
                indo = false;
        }
        // Se não, ele está voltando para a esquerda
        else
        {
            // Move o inimigo para a esquerda
            transform.Translate(Vector2.left * velocidade * Time.deltaTime);

            // Se chegou (ou passou) do limite esquerdo da patrulha, passa a ir para a direita novamente
            if (transform.position.x <= inicio.x - distancia)
                indo = true;
        }
    }
}