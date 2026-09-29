using UnityEngine;
using UnityEngine.SceneManagement;

public class Inimigo : MonoBehaviour
{
    public float velocidade = 2f;
    public float distancia = 3f;

    private Vector3 inicio;
    private bool indo = true;

    void Start()
    {
        inicio = transform.position;
    }

    void Update()
    {
        if (indo)
        {
            transform.Translate(Vector2.right * velocidade * Time.deltaTime);

            if (transform.position.x >= inicio.x + distancia)
                indo = false;
        }
        else
        {
            transform.Translate(Vector2.left * velocidade * Time.deltaTime);

            if (transform.position.x <= inicio.x - distancia)
                indo = true;
        }
    }

    private void OnCollisionEnter2D(Collision2D collision)
    {
        if (collision.gameObject.CompareTag("Player"))
        {
            SceneManager.LoadScene(0);
        }
    }
}