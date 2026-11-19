using UnityEngine;

/// <summary>
/// Efeito de paralaxe: a camada acompanha uma parte do movimento da câmera.
///   fator = 0   -> fica parada no mundo (anda junto com o cenário)
///   fator = 1   -> anda junto com a câmera (parece infinitamente longe)
/// Camadas "longe" usam fator alto e camadas "perto" usam fator baixo,
/// e isso dá a sensação de profundidade. Só visual.
/// </summary>
public class Paralaxe : MonoBehaviour
{
    [Range(0f, 1f)] public float fatorX = 0.5f;
    [Range(0f, 1f)] public float fatorY = 0.5f;

    private Transform cam;
    private Vector3 inicioCamada;
    private Vector3 inicioCamera;

    void Start()
    {
        if (Camera.main == null) { enabled = false; return; }
        cam = Camera.main.transform;
        inicioCamada = transform.position;
        inicioCamera = cam.position;
    }

    // LateUpdate: roda depois que a câmera já se mexeu neste quadro
    void LateUpdate()
    {
        Vector3 andou = cam.position - inicioCamera;
        transform.position = new Vector3(
            inicioCamada.x + andou.x * fatorX,
            inicioCamada.y + andou.y * fatorY,
            inicioCamada.z);
    }
}
