using UnityEngine;
using UnityEngine.SceneManagement;

public class Vitoria : MonoBehaviour
{
    public string proximaFase = ("Jogo2");

    private void OnTriggerEnter2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
        {
            Sons.Tocar("fase");
            SceneManager.LoadScene(proximaFase);
        }
    }
}