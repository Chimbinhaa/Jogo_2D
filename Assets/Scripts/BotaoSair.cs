using UnityEngine;

#if UNITY_EDITOR
using UnityEditor;
#endif

public class BotaoSair : MonoBehaviour
{
    public void Sair()
    {
#if UNITY_EDITOR
        // Dentro do editor da Unity: para o modo Play
        EditorApplication.isPlaying = false;
#else
        // No jogo exportado (build): fecha o jogo
        Application.Quit();
#endif
    }
}
