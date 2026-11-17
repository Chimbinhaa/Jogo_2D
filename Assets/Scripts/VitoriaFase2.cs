using UnityEngine;

public class VitoriaFase2 : MonoBehaviour
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
