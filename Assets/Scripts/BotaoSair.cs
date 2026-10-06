using UnityEngine;

#if UNITY_EDITOR
using UnityEditor;
#endif

public class BotaoSair : MonoBehaviour
{
    public void Sair()
    {
#if UNITY_EDITOR
        EditorApplication.isPlaying = false;
#endif
    }
}