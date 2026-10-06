using UnityEngine;

public class Vitoria : MonoBehaviour
{
    public TelaVitoria tela;

    private void OnTriggerEnter2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
        {
            tela.MostrarVitoria();
        }
    }
}