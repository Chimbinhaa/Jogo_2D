using System.Collections.Generic;
using UnityEngine;

public class Player : MonoBehaviour
{
    public float speed = 5f;
    public float forcaPulo = 6f;
    public MenuScene tela;

    private Rigidbody2D rb;

    // Guarda quais "chãos" o player está pisando por cima.
    // Usar uma lista (em vez de true/false) evita o bug de perder o pulo
    // quando o player está encostado em dois blocos de chão ao mesmo tempo.
    private readonly HashSet<Collider2D> chaosTocando = new HashSet<Collider2D>();
    public bool IsGrounded => chaosTocando.Count > 0; // público para a animação saber se está no chão

    void Start()
    {
        rb = GetComponent<Rigidbody2D>();
    }

    void Update()
    {
        // Jogo pausado / game over / vitória: ignora os controles
        if (Time.timeScale == 0f) return;

        float moveHorizontal = Input.GetAxis("Horizontal");
        rb.linearVelocity = new Vector2(moveHorizontal * speed, rb.linearVelocity.y);

        if (Input.GetKeyDown(KeyCode.Space) && IsGrounded)
        {
            // Zera a velocidade vertical antes do pulo para ele ter sempre a mesma altura
            rb.linearVelocity = new Vector2(rb.linearVelocity.x, 0f);
            rb.AddForce(new Vector2(0f, forcaPulo), ForceMode2D.Impulse);
            Sons.Tocar("pulo");
        }
    }

    void OnCollisionEnter2D(Collision2D collision)
    {
        if (collision.gameObject.CompareTag("Ground") && TocandoPorCima(collision))
        {
            // Som de pouso só quando estava no ar e caiu com alguma velocidade
            if (!IsGrounded && collision.relativeVelocity.y > 2f) Sons.Tocar("aterrissar", 0.6f);
            chaosTocando.Add(collision.collider);
        }

        if (collision.gameObject.CompareTag("Dano Espinho") || collision.gameObject.CompareTag("Inimigo"))
        {
            if (tela != null) tela.MostrarGameOver();
        }
    }

    // Atualiza enquanto continua encostado (ex.: encostou na lateral e depois subiu em cima)
    void OnCollisionStay2D(Collision2D collision)
    {
        if (!collision.gameObject.CompareTag("Ground")) return;

        if (TocandoPorCima(collision)) chaosTocando.Add(collision.collider);
        else chaosTocando.Remove(collision.collider);
    }

    private void OnCollisionExit2D(Collision2D collision)
    {
        if (collision.gameObject.CompareTag("Ground"))
        {
            chaosTocando.Remove(collision.collider);
        }
    }

    // Só conta como chão se o player estiver EM CIMA do objeto
    // (evita pular grudado na lateral das paredes/plataformas).
    private bool TocandoPorCima(Collision2D collision)
    {
        foreach (ContactPoint2D contato in collision.contacts)
        {
            if (contato.normal.y > 0.5f) return true;
        }
        return false;
    }
}
