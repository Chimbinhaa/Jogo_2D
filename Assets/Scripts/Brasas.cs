using UnityEngine;

/// <summary>
/// Brasas subindo pela tela (fica na câmera). Cria algumas brasinhas que sobem
/// balançando e piscando; quando saem da tela, voltam pelo outro lado.
/// Só visual: não têm colisor.
/// </summary>
[RequireComponent(typeof(Camera))]
public class Brasas : MonoBehaviour
{
    public Sprite[] quadros;          // brasa acesa / piscando
    public int quantidade = 28;
    public float velocidadeSubida = 0.9f;
    public int ordemDesenho = -50;     // na frente do fundo, atrás do chão e dos personagens

    private Camera cam;
    private SpriteRenderer[] brasas;
    private float[] velocidade, balanco, fase;

    void Start()
    {
        cam = GetComponent<Camera>();
        if (quadros == null || quadros.Length == 0) { enabled = false; return; }

        var pai = new GameObject("Brasas (pixel art)").transform; // fica na raiz da cena, não na câmera
        brasas = new SpriteRenderer[quantidade];
        velocidade = new float[quantidade];
        balanco = new float[quantidade];
        fase = new float[quantidade];

        Rect area = AreaDaCamera();
        for (int i = 0; i < quantidade; i++)
        {
            var go = new GameObject("Brasa");
            go.transform.SetParent(pai, false);
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = quadros[0];
            sr.sortingOrder = ordemDesenho;
            brasas[i] = sr;
            velocidade[i] = velocidadeSubida * Random.Range(0.5f, 1.5f);
            balanco[i] = Random.Range(0.2f, 0.6f);
            fase[i] = Random.Range(0f, 10f);
            go.transform.position = new Vector3(
                Random.Range(area.xMin, area.xMax), Random.Range(area.yMin, area.yMax), 0f);
        }
    }

    Rect AreaDaCamera()
    {
        float alt = cam.orthographicSize * 2f;
        float larg = alt * cam.aspect;
        Vector3 c = cam.transform.position;
        // um pouco maior que a tela, para as brasas não "nascerem" à vista
        return new Rect(c.x - larg / 2f - 1f, c.y - alt / 2f - 1f, larg + 2f, alt + 2f);
    }

    void Update()
    {
        if (Time.deltaTime <= 0f) return; // pausado
        Rect area = AreaDaCamera();
        float t = Time.time;

        for (int i = 0; i < brasas.Length; i++)
        {
            var tr = brasas[i].transform;
            Vector3 p = tr.position;
            p.y += velocidade[i] * Time.deltaTime;
            p.x += Mathf.Sin(t * 1.7f + fase[i]) * balanco[i] * Time.deltaTime;

            // saiu da área da câmera: volta pelo lado oposto
            if (p.y > area.yMax) { p.y = area.yMin; p.x = Random.Range(area.xMin, area.xMax); }
            if (p.y < area.yMin) p.y = area.yMax;
            if (p.x > area.xMax) p.x -= area.width;
            if (p.x < area.xMin) p.x += area.width;
            tr.position = p;

            // pisca de vez em quando
            brasas[i].sprite = quadros[(Mathf.Sin(t * 6f + fase[i] * 3f) > 0.6f && quadros.Length > 1) ? 1 : 0];
        }
    }
}
