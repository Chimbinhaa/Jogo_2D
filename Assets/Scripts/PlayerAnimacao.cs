using UnityEngine;

/// <summary>
/// Anima o sprite do player trocando os quadros conforme o que ele está fazendo:
/// parado (respirando), andando ou no ar (pulando/caindo).
/// Também vira o desenho para o lado em que ele anda.
/// Só mexe no visual: não altera física nem controles.
/// </summary>
[RequireComponent(typeof(SpriteRenderer))]
public class PlayerAnimacao : MonoBehaviour
{
    public Sprite[] parado;   // quadros parado (respiração)
    public Sprite[] andando;  // quadros andando
    public Sprite pulo;       // quadro no ar

    public float fpsParado = 2f;
    public float fpsAndando = 10f;

    private SpriteRenderer sr;
    private Rigidbody2D rb;
    private Player player;
    private float tempo;

    void Start()
    {
        sr = GetComponent<SpriteRenderer>();
        rb = GetComponent<Rigidbody2D>();
        player = GetComponent<Player>();
    }

    void Update()
    {
        if (rb == null) return;
        tempo += Time.deltaTime; // para sozinho quando o jogo é pausado (timeScale = 0)

        Vector2 v = rb.linearVelocity;
        // No chão = pisando num "Ground" ou parado na vertical (ex.: em cima de uma plataforma que some)
        bool noChao = (player != null && player.IsGrounded) || Mathf.Abs(v.y) < 0.05f;

        if (!noChao && pulo != null)
        {
            sr.sprite = pulo;
        }
        else if (Mathf.Abs(v.x) > 0.1f && andando != null && andando.Length > 0)
        {
            sr.sprite = andando[(int)(tempo * fpsAndando) % andando.Length];
        }
        else if (parado != null && parado.Length > 0)
        {
            sr.sprite = parado[(int)(tempo * fpsParado) % parado.Length];
        }

        // Vira para o lado do movimento (o nó da bandana fica para trás)
        if (v.x > 0.1f) sr.flipX = true;
        else if (v.x < -0.1f) sr.flipX = false;
    }
}
