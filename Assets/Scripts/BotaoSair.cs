using UnityEngine;

// Esse bloco só existe dentro do editor da Unity, pois a biblioteca UnityEditor não existe em builds
#if UNITY_EDITOR
using UnityEditor;
#endif

// Script do botão "Sair": fecha o jogo (ou para o modo Play quando está no editor)
public class BotaoSair : MonoBehaviour
{
    // Método público para ser chamado pelo evento OnClick do botão na Unity
    public void Sair()
    {
        // Compilação condicional: este trecho só é usado se estiver rodando dentro do editor
#if UNITY_EDITOR
        // Dentro do editor da Unity: para o modo Play
        EditorApplication.isPlaying = false;
        // Caso contrário (jogo exportado), usa o trecho abaixo
#else
        // No jogo exportado (build): fecha o jogo
        Application.Quit();
#endif
    }
}