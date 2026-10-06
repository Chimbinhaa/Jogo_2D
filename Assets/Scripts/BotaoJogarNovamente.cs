using UnityEngine;
using UnityEngine.SceneManagement;

public class BotaoJogarNovamente : MonoBehaviour
{
    public void JogarNovamente()
    {
        Time.timeScale = 1f;
        SceneManager.LoadScene(SceneManager.GetActiveScene().name);
    }
}