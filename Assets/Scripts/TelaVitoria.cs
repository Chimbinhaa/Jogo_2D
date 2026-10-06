using UnityEngine;

public class TelaVitoria : MonoBehaviour
{
    public GameObject telaVitoria;

    public void MostrarVitoria()
    {
        telaVitoria.SetActive(true);
        Time.timeScale = 0f;
    }
}