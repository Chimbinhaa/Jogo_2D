using UnityEngine;
using System.Collections; // Necessário para usar corrotinas (IEnumerator)

// Plataforma que some depois que o player pisa nela e reaparece depois de um tempo
public class PlataformaDissolvivel : MonoBehaviour
{
    public float tempoParaSumir = 2.5f;     // Tempo que a plataforma pisca antes de desaparecer
    public float tempoParaVoltar = 3f;      // Tempo que a plataforma fica invisível antes de reaparecer
    public float velocidadePiscada = 0.12f; // Intervalo (em segundos) entre cada piscada

    private bool ativada = true;            // Indica se a plataforma pode ser ativada (evita iniciar o processo duas vezes)
    private SpriteRenderer sprite;          // Referência ao componente visual da plataforma

    void Start()
    {
        // Pega o SpriteRenderer do próprio objeto para poder esconder/mostrar a plataforma
        sprite = GetComponent<SpriteRenderer>();
    }

    // Chamado quando algum objeto encosta (colide) na plataforma
    private void OnCollisionEnter2D(Collision2D collision)
    {
        // Só inicia se quem encostou for o Player e a plataforma ainda estiver ativa
        if (collision.gameObject.CompareTag("Player") && ativada)
        {
            // Inicia a sequência de piscar, sumir e voltar
            StartCoroutine(Desaparecer());
        }
    }

    // Corrotina: executa o processo passo a passo, com pausas entre as etapas
    IEnumerator Desaparecer()
    {
        // Marca como desativada para não reiniciar o processo enquanto ele já está acontecendo
        ativada = false;

        // Contador de quanto tempo já se passou piscando
        float tempo = 0;

        // Plataforma começa a piscar
        // Repete enquanto o tempo de piscada não chegar ao limite
        while (tempo < tempoParaSumir)
        {
            // Inverte a visibilidade do sprite (se estava visível, esconde; se estava escondido, mostra)
            sprite.enabled = !sprite.enabled;

            // Espera um pouco antes da próxima piscada
            yield return new WaitForSeconds(velocidadePiscada);

            // Soma o tempo esperado ao contador
            tempo += velocidadePiscada;
        }

        // Desaparece
        Sons.Tocar("plataforma");                       // Toca o som da plataforma sumindo
        sprite.enabled = false;                         // Deixa o sprite invisível
        GetComponent<Collider2D>().enabled = false;     // Desliga a colisão (o player passa a atravessar e cai)

        // Espera para reaparecer
        yield return new WaitForSeconds(tempoParaVoltar);

        // Reaparece
        sprite.enabled = true;                          // Torna o sprite visível de novo
        GetComponent<Collider2D>().enabled = true;      // Liga a colisão novamente (volta a ser sólida)

        // Libera a plataforma para ser ativada outra vez
        ativada = true;
    }
}