using UnityEngine;
using System.Collections;

public class PlataformaDissolvivel : MonoBehaviour
{
    public float tempoParaSumir = 2.5f;
    public float tempoParaVoltar = 3f;
    public float velocidadePiscada = 0.12f;

    private bool ativada = true;
    private SpriteRenderer sprite;

    void Start()
    {
        sprite = GetComponent<SpriteRenderer>();
    }

    private void OnCollisionEnter2D(Collision2D collision)
    {
        if (collision.gameObject.CompareTag("Player") && ativada)
        {
            StartCoroutine(Desaparecer());
        }
    }

    IEnumerator Desaparecer()
    {
        ativada = false;

        float tempo = 0;

        // Plataforma começa a piscar
        while (tempo < tempoParaSumir)
        {
            sprite.enabled = !sprite.enabled;

            yield return new WaitForSeconds(velocidadePiscada);

            tempo += velocidadePiscada;
        }

        // Desaparece
        sprite.enabled = false;
        GetComponent<Collider2D>().enabled = false;

        // Espera para reaparecer
        yield return new WaitForSeconds(tempoParaVoltar);

        // Reaparece
        sprite.enabled = true;
        GetComponent<Collider2D>().enabled = true;

        ativada = true;
    }
}