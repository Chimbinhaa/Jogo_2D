using UnityEngine;
using UnityEngine.SceneManagement;
public class MenuScene : MonoBehaviour
{
    public GameObject painelPause;
    public GameObject painelGameOver;

    bool pausado = false;
    bool jogoAcabou = false;


    void Start()
    {
        painelPause.SetActive(false);
        painelGameOver.SetActive(false);
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            if (pausado)
            {
                Continuar();
            }
            else
            {
                Pausar();
            }
        }
    }

    public void Pausar()
    {
        // Não pausa se o jogo acabou ou se outra tela (ex.: vitória) já parou o tempo.
        // Sem isso, apertar ESC na tela de vitória e depois "Continuar" voltava o jogo a rodar por trás.
        if (jogoAcabou == false && Time.timeScale > 0f)
        {
            pausado = true;
            painelPause.SetActive(true);
            Time.timeScale = 0f;
        }
    }

    public void Continuar()
    {
        pausado = false;
        painelPause.SetActive(false);
        Time.timeScale = 1f;
    }

    public void MostrarGameOver()
    {
        if (jogoAcabou) return; // evita chamar duas vezes (ex.: tocou espinho e inimigo juntos)
        jogoAcabou = true;
        pausado = false;
        painelPause.SetActive(false);
        painelGameOver.SetActive(true);
        Time.timeScale = 0f;
    }

    public void Reiniciar()
    {
        Time.timeScale = 1f;
        SceneManager.LoadScene(SceneManager.GetActiveScene().name);
    }
    public void VoltarMenu() 
    {
        Time.timeScale = 1f;
        SceneManager.LoadScene(0);
    
    }
}