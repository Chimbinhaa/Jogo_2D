using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

/// <summary>
/// Toca os efeitos sonoros do jogo. Não precisa colocar em nenhuma cena:
/// ele se cria sozinho quando o jogo começa e continua vivo ao trocar de cena
/// (assim o som não corta quando a fase recarrega).
///
/// Uso em qualquer script:  Sons.Tocar("pulo");
/// Os sons ficam em Assets/Audio/Resources/Sons (o nome é o nome do arquivo .wav).
/// Todos os botões das cenas tocam "clique" automaticamente.
/// </summary>
public class Sons : MonoBehaviour
{
    public static float volume = 0.7f; // volume geral dos efeitos (0 a 1)

    static Sons instancia;
    AudioSource fonte;
    readonly Dictionary<string, AudioClip> clips = new Dictionary<string, AudioClip>();

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
    static void Criar()
    {
        var go = new GameObject("Sons");
        DontDestroyOnLoad(go);
        instancia = go.AddComponent<Sons>();
        instancia.fonte = go.AddComponent<AudioSource>();
        instancia.fonte.playOnAwake = false;
        instancia.fonte.spatialBlend = 0f; // som 2D (mesmo volume em qualquer lugar)

        foreach (var clip in Resources.LoadAll<AudioClip>("Sons"))
            instancia.clips[clip.name] = clip;

        SceneManager.sceneLoaded += (cena, modo) => instancia.LigarBotoes();
    }

    public static void Tocar(string nome, float vol = 1f)
    {
        if (instancia == null) return;
        if (instancia.clips.TryGetValue(nome, out var clip))
            instancia.fonte.PlayOneShot(clip, vol * volume);
        else
            Debug.LogWarning("Som não encontrado: " + nome);
    }

    // Coloca o som de clique em todos os botões da cena (inclusive os de telas escondidas)
    void LigarBotoes()
    {
        foreach (var botao in FindObjectsByType<Button>(FindObjectsInactive.Include, FindObjectsSortMode.None))
            botao.onClick.AddListener(() => Tocar("clique"));
    }
}
