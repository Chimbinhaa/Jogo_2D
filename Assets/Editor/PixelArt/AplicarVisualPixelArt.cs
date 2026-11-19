using System.Collections.Generic;
using System.IO;
using System.Linq;
using TMPro;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TextCore.LowLevel;
using UnityEngine.UI;

namespace PixelArt
{
    /// <summary>
    /// Ferramenta de Editor que aplica o visual em pixel art nas cenas.
    /// Menu: Ferramentas > Pixel Art > Aplicar visual nas cenas
    ///
    /// Ela SÓ mexe em coisas visuais (sprites, cores, fontes, UI, animações de sprite).
    /// Não altera Transforms, colisores, Rigidbodies, tags nem scripts do jogo.
    /// Pode ser executada de novo sem problema (não duplica nada).
    /// </summary>
    public static class AplicarVisualPixelArt
    {
        const string Art = "Assets/Art";
        const string Sprites = Art + "/Sprites";
        const string Fontes = Art + "/Fontes";
        const string Animacoes = Art + "/Animacoes";
        const string NomeVisual = "Visual (pixel art)";

        static readonly string[] Cenas = { "Assets/Scenes/Menu.unity", "Assets/Scenes/Jogo.unity", "Assets/Scenes/Jogo2.unity" };

        // Cores da paleta (iguais às do gerador em Python)
        static readonly Color Creme = Hex("f4e6c8");
        static readonly Color Preto = Hex("1a0a12");
        static readonly Color Ouro = Hex("eab83a");
        static readonly Color Lava = Hex("ffa030");

        [MenuItem("Ferramentas/Pixel Art/Aplicar visual nas cenas")]
        public static void Executar()
        {
            AssetDatabase.Refresh();
            var fonte = CriarFonte();
            var matTitulo = CriarMaterialFonte(fonte, "Titulo", 0.18f, new Color(0.93f, 0.36f, 0.13f, 0.9f), 0.9f);
            var matSombra = CriarMaterialFonte(fonte, "Sombra", 0f, new Color(0.1f, 0.04f, 0.07f, 1f), 0.6f);
            var animDemonio = CriarAnimacao("Demonio", new[] { "Inimigos/demonio_coracao_0", "Inimigos/demonio_coracao_1" }, 6f);
            var animTrofeu = CriarAnimacao("Trofeu", new[] { "Objetos/trofeu_0", "Objetos/trofeu_0", "Objetos/trofeu_0",
                                                             "Objetos/trofeu_0", "Objetos/trofeu_1", "Objetos/trofeu_2", "Objetos/trofeu_3" }, 10f);

            foreach (var caminho in Cenas)
            {
                var cena = EditorSceneManager.OpenScene(caminho, OpenSceneMode.Single);
                AplicarNaCena(fonte, matTitulo, matSombra, animDemonio, animTrofeu);
                EditorSceneManager.MarkSceneDirty(cena);
                EditorSceneManager.SaveScene(cena);
                Debug.Log("[PixelArt] Cena atualizada: " + caminho);
            }

            OrganizarSpritesAntigos();
            AssetDatabase.SaveAssets();
            Debug.Log("[PixelArt] Pronto!");
        }

        // Usado pela linha de comando (batchmode)
        public static void ExecutarBatch()
        {
            Executar();
            CapturarTelas();
        }

        // ------------------------------------------------------------------
        static void AplicarNaCena(TMP_FontAsset fonte, Material matTitulo, Material matSombra,
                                  RuntimeAnimatorController animDemonio, RuntimeAnimatorController animTrofeu)
        {
            var spr = new Dictionary<string, Sprite>();
            Sprite S(string nome)
            {
                if (!spr.TryGetValue(nome, out var s))
                {
                    s = AssetDatabase.LoadAssetAtPath<Sprite>($"{Sprites}/{nome}.png");
                    if (s == null) Debug.LogError("[PixelArt] Sprite não encontrado: " + nome);
                    spr[nome] = s;
                }
                return s;
            }

            // --- Sprites do mundo -----------------------------------------
            foreach (var sr in Object.FindObjectsByType<SpriteRenderer>(FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                if (sr.gameObject.name == NomeVisual || sr.sprite == null) continue;
                string caminho = AssetDatabase.GetAssetPath(sr.sprite);
                string nome = sr.sprite.name;
                var go = sr.gameObject;

                if (nome == "Square" || (go.CompareTag("Ground") && !caminho.StartsWith(Sprites)))
                {
                    if (go.GetComponent<PlataformaDissolvivel>() != null)
                    {
                        // O script da plataforma pisca ESTE SpriteRenderer, então o visual fica nele mesmo.
                        Trocar(sr, S("Cenario/plataforma_dissolvivel"));
                    }
                    else
                    {
                        CriarVisualLadrilhado(sr, S("Cenario/tile_rocha"));
                    }
                }
                else if (caminho.Contains("image-removebg-preview (8)"))
                    Trocar(sr, S("Personagens/agenor"));
                else if (caminho.Contains("SpriteInimigo"))
                {
                    Trocar(sr, S("Inimigos/demonio_coracao_0"));
                    Animar(go, animDemonio);
                }
                else if (caminho.Contains("SpriteEspinho"))
                {
                    var esc = go.transform.localScale;
                    bool gigante = esc.y / Mathf.Max(0.01f, esc.x) > 3f;
                    Trocar(sr, S(gigante ? "Cenario/estalagmite" : "Cenario/espinho"));
                }
                else if (caminho.Contains("Trof"))
                {
                    Trocar(sr, S("Objetos/trofeu_0"));
                    Animar(go, animTrofeu);
                }
                else if (caminho.Contains("BackgroundHell"))
                {
                    Trocar(sr, S("Cenario/fundo_inferno"));
                    sr.sortingOrder = -100; // sempre atrás de tudo
                }
            }

            // Cor de fundo da câmera combinando com o topo do cenário
            foreach (var cam in Object.FindObjectsByType<Camera>(FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                Undo.RecordObject(cam, "Pixel Art");
                cam.backgroundColor = Preto;
            }

            // --- Interface (UI) -------------------------------------------
            foreach (var img in Object.FindObjectsByType<Image>(FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                Undo.RecordObject(img, "Pixel Art");
                var nomeSprite = img.sprite != null ? img.sprite.name : "";
                var botao = img.GetComponent<Button>();
                float altura = ((RectTransform)img.transform).rect.height;

                if (botao != null)
                {
                    img.sprite = S("UI/botao");
                    img.type = Image.Type.Sliced;
                    img.pixelsPerUnitMultiplier = altura >= 60 ? 1f / 3f : 1f / 2f; // 1 pixel da arte = 2 ou 3 pixels de tela
                    img.color = Color.white;
                    Undo.RecordObject(botao, "Pixel Art");
                    var cores = botao.colors;
                    cores.normalColor = Color.white;
                    cores.highlightedColor = new Color(1f, 0.82f, 0.62f);
                    cores.selectedColor = new Color(1f, 0.9f, 0.8f);
                    cores.pressedColor = new Color(0.7f, 0.55f, 0.5f);
                    cores.fadeDuration = 0.05f;
                    botao.colors = cores;
                }
                else if (nomeSprite == "Background" || nomeSprite == "painel")
                {
                    img.sprite = S("UI/painel");
                    img.type = Image.Type.Sliced;
                    img.pixelsPerUnitMultiplier = 1f / 3f;
                    var n = img.gameObject.name;
                    img.color = n.Contains("Gameover") ? new Color(1f, 0.55f, 0.55f)
                              : n.Contains("Vitoria") ? new Color(1f, 0.9f, 0.55f)
                              : Color.white;
                }
                else if (nomeSprite.Contains("background do menu") || nomeSprite == "fundo_menu")
                {
                    img.sprite = S("UI/fundo_menu");
                    img.color = Color.white;
                }
            }

            foreach (var txt in Object.FindObjectsByType<TMP_Text>(FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                Undo.RecordObject(txt, "Pixel Art");
                bool emBotao = txt.GetComponentInParent<Button>(true) != null;
                txt.font = fonte;
                txt.characterSpacing = 0;
                AjustarTamanho(txt, emBotao);

                if (emBotao)
                {
                    txt.fontSharedMaterial = matSombra;
                    txt.color = Creme;
                }
                else
                {
                    txt.fontSharedMaterial = matTitulo;
                    var cor = txt.color;
                    if (txt.text.Contains("Hell"))                            // título do menu
                        txt.color = Hex("ffe27a");
                    else if (txt.text.Contains("Venceu"))
                        txt.color = Ouro;
                    else if (cor.r > 0.9f && cor.g > 0.9f && cor.b > 0.9f)  // texto branco
                        txt.color = Creme;
                    else if (cor.r > 0.6f && cor.g < 0.3f || txt.text.Contains("morreu")) // texto vermelho
                        txt.color = Hex("ff7486");
                }
            }
        }

        /// <summary>
        /// Escolhe o tamanho da fonte: começa pelo maior múltiplo de 8 que cabe na altura da
        /// caixa do texto e vai diminuindo de 8 em 8 até caber na largura (mínimo 16).
        /// Títulos ficam em 1 linha só (sem quebrar "Game / over"); os longos podem passar
        /// um pouco da caixa (até 560 px, que ainda fica dentro do painel).
        /// </summary>
        static void AjustarTamanho(TMP_Text txt, bool emBotao)
        {
            var rect = ((RectTransform)txt.transform).rect;
            if (rect.width <= 1 && txt.transform.parent is RectTransform pai) rect = pai.rect;
            float largura = rect.width - txt.margin.x - txt.margin.z;
            if (largura <= 1 || rect.height <= 1) return;

            // Botões: o texto cabe dentro do botão. Título do menu: dentro da própria caixa.
            // Outros títulos (pause, game over, vitória): até 560 px, que fica dentro do painel.
            float limite = emBotao ? largura - 8f : (txt.text.Contains("Hell") ? rect.width : 560f);
            if (!emBotao) txt.textWrappingMode = TextWrappingModes.NoWrap;

            float maximo = emBotao ? 40f : 56f;
            txt.fontSize = Mathf.Clamp(Mathf.Floor(rect.height / 1.2f / 8f) * 8f, 16f, maximo);
            while (txt.fontSize > 16)
            {
                txt.ForceMeshUpdate();
                float w = txt.GetPreferredValues(txt.text, 10000f, 10000f).x;
                if (w <= limite) break;
                txt.fontSize -= 8;
            }
            Debug.Log($"[PixelArt] Texto '{txt.text}' -> tamanho {txt.fontSize} (caixa {rect.width:0}x{rect.height:0}, limite {limite:0})");
        }

        // ------------------------------------------------------------------
        static void Trocar(SpriteRenderer sr, Sprite novo)
        {
            Undo.RecordObject(sr, "Pixel Art");
            sr.sprite = novo;
            sr.color = Color.white;
            sr.drawMode = SpriteDrawMode.Simple;
        }

        /// <summary>
        /// Os blocos de chão/parede são quadrados esticados (escala tipo 18 x 1).
        /// Para os ladrilhos não ficarem esticados, o desenho vai num objeto filho
        /// só de visual, com escala inversa e modo "Tiled". O colisor continua no pai.
        /// </summary>
        static void CriarVisualLadrilhado(SpriteRenderer pai, Sprite tile)
        {
            var t = pai.transform;
            var existente = t.Find(NomeVisual);
            GameObject go = existente != null ? existente.gameObject : new GameObject(NomeVisual);
            if (existente == null) Undo.RegisterCreatedObjectUndo(go, "Pixel Art");
            go.transform.SetParent(t, false);
            var esc = t.localScale;
            Vector2 tamanhoAntigo = pai.sprite != null && pai.sprite.name != tile.name ? (Vector2)pai.sprite.bounds.size : Vector2.one;
            float largura = tamanhoAntigo.x * esc.x, altura = tamanhoAntigo.y * esc.y;

            // Paredes giradas em 90/180/270 graus: o visual "desgira" para a crosta de lava
            // ficar sempre em cima. Rampas (ângulos pequenos) acompanham a inclinação.
            float angulo = t.eulerAngles.z;
            int quartos = Mathf.RoundToInt(angulo / 90f);
            if (Mathf.Abs(Mathf.DeltaAngle(angulo, quartos * 90f)) > 5f) quartos = 0;
            bool trocaEixos = quartos % 2 != 0;

            go.transform.localPosition = Vector3.zero;
            go.transform.localRotation = Quaternion.Euler(0, 0, -quartos * 90f);
            go.transform.localScale = trocaEixos
                ? new Vector3(1f / esc.y, 1f / esc.x, 1f)
                : new Vector3(1f / esc.x, 1f / esc.y, 1f);

            var sr = go.GetComponent<SpriteRenderer>();
            if (sr == null) sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = tile;
            sr.drawMode = SpriteDrawMode.Tiled;
            sr.tileMode = SpriteTileMode.Continuous;
            sr.size = trocaEixos ? new Vector2(altura, largura) : new Vector2(largura, altura);
            sr.sortingLayerID = pai.sortingLayerID;
            sr.sortingOrder = pai.sortingOrder;

            Undo.RecordObject(pai, "Pixel Art");
            pai.enabled = false; // o quadrado antigo fica desligado (o colisor continua funcionando)
        }

        static void Animar(GameObject go, RuntimeAnimatorController ctrl)
        {
            var anim = go.GetComponent<Animator>();
            if (anim == null) anim = Undo.AddComponent<Animator>(go);
            anim.runtimeAnimatorController = ctrl;
            anim.applyRootMotion = false;
        }

        static RuntimeAnimatorController CriarAnimacao(string nome, string[] quadros, float fps)
        {
            Directory.CreateDirectory(Animacoes);
            string pathClip = $"{Animacoes}/{nome}_Loop.anim";
            string pathCtrl = $"{Animacoes}/{nome}.controller";

            var clip = AssetDatabase.LoadAssetAtPath<AnimationClip>(pathClip);
            if (clip == null)
            {
                clip = new AnimationClip { frameRate = fps };
                AssetDatabase.CreateAsset(clip, pathClip);
            }
            var binding = EditorCurveBinding.PPtrCurve("", typeof(SpriteRenderer), "m_Sprite");
            var keys = new ObjectReferenceKeyframe[quadros.Length + 1];
            for (int i = 0; i <= quadros.Length; i++)
            {
                var q = quadros[i % quadros.Length];
                keys[i] = new ObjectReferenceKeyframe
                {
                    time = i / fps,
                    value = AssetDatabase.LoadAssetAtPath<Sprite>($"{Sprites}/{q}.png")
                };
            }
            AnimationUtility.SetObjectReferenceCurve(clip, binding, keys);
            var cfg = AnimationUtility.GetAnimationClipSettings(clip);
            cfg.loopTime = true;
            AnimationUtility.SetAnimationClipSettings(clip, cfg);
            EditorUtility.SetDirty(clip);

            var ctrl = AssetDatabase.LoadAssetAtPath<AnimatorController>(pathCtrl);
            if (ctrl == null) ctrl = AnimatorController.CreateAnimatorControllerAtPathWithClip(pathCtrl, clip);
            return ctrl;
        }

        // ------------------------------------------------------------------
        static TMP_FontAsset CriarFonte()
        {
            string pathAsset = $"{Fontes}/PixelInferno SDF.asset";
            const string caracteres =
                " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]_abcdefghijklmnopqrstuvwxyz|" +
                "áàâãäéêèíóôõöúüçÁÀÂÃÉÊÍÓÔÕÚÇ";

            var existente = AssetDatabase.LoadAssetAtPath<TMP_FontAsset>(pathAsset);
            if (existente != null)
            {
                // Já existe: refaz o atlas com o .ttf atual (caso os glifos tenham mudado)
                existente.atlasPopulationMode = AtlasPopulationMode.Dynamic;
                existente.ClearFontAssetData();
                existente.TryAddCharacters(caracteres, out _);
                existente.atlasPopulationMode = AtlasPopulationMode.Static;
                EditorUtility.SetDirty(existente);
                AssetDatabase.SaveAssets();
                return existente;
            }

            var ttf = AssetDatabase.LoadAssetAtPath<Font>($"{Fontes}/PixelInferno.ttf");
            // 64 de amostragem: cada pixel da fonte (1/8 do 'em') vira 8 pixels no atlas
            var fa = TMP_FontAsset.CreateFontAsset(ttf, 64, 8, GlyphRenderMode.SDFAA, 1024, 1024,
                                                   AtlasPopulationMode.Dynamic, false);
            fa.name = "PixelInferno SDF";
            AssetDatabase.CreateAsset(fa, pathAsset);
            fa.material.name = "PixelInferno SDF Material";
            AssetDatabase.AddObjectToAsset(fa.material, fa);
            fa.atlasTexture.name = "PixelInferno SDF Atlas";
            AssetDatabase.AddObjectToAsset(fa.atlasTexture, fa);

            fa.TryAddCharacters(caracteres, out string faltando);
            if (!string.IsNullOrEmpty(faltando)) Debug.LogWarning("[PixelArt] Caracteres sem glifo: " + faltando);
            fa.atlasPopulationMode = AtlasPopulationMode.Static; // atlas pronto, não precisa do .ttf no jogo
            EditorUtility.SetDirty(fa);
            AssetDatabase.SaveAssets();
            return fa;
        }

        static Material CriarMaterialFonte(TMP_FontAsset fonte, string sufixo, float contorno, Color corSombra, float deslocSombra)
        {
            string path = $"{Fontes}/PixelInferno SDF - {sufixo}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(fonte.material);
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.CopyPropertiesFromMaterial(fonte.material);
            mat.SetFloat("_FaceDilate", contorno > 0 ? 0.1f : 0f);
            mat.SetFloat("_OutlineWidth", contorno);
            mat.SetColor("_OutlineColor", Preto);
            if (contorno > 0) mat.EnableKeyword("OUTLINE_ON");
            mat.EnableKeyword("UNDERLAY_ON");
            mat.SetColor("_UnderlayColor", corSombra);
            mat.SetFloat("_UnderlayOffsetX", deslocSombra);
            mat.SetFloat("_UnderlayOffsetY", -deslocSombra);
            mat.SetFloat("_UnderlayDilate", contorno > 0 ? 0.3f : 0.1f);
            mat.SetFloat("_UnderlaySoftness", 0f);
            EditorUtility.SetDirty(mat);
            return mat;
        }

        // ------------------------------------------------------------------
        static void OrganizarSpritesAntigos()
        {
            const string antigos = Art + "/_Antigos";
            if (!AssetDatabase.IsValidFolder("Assets/Sprites")) return;
            if (!AssetDatabase.IsValidFolder(antigos)) AssetDatabase.CreateFolder(Art, "_Antigos");
            foreach (var guid in AssetDatabase.FindAssets("", new[] { "Assets/Sprites" }))
            {
                var p = AssetDatabase.GUIDToAssetPath(guid);
                if (AssetDatabase.IsValidFolder(p)) continue;
                var erro = AssetDatabase.MoveAsset(p, $"{antigos}/{Path.GetFileName(p)}");
                if (!string.IsNullOrEmpty(erro)) Debug.LogWarning("[PixelArt] " + erro);
            }
            if (!AssetDatabase.FindAssets("", new[] { "Assets/Sprites" }).Any())
                AssetDatabase.DeleteAsset("Assets/Sprites");
        }

        // ------------------------------------------------------------------
        // Fotos das cenas para a documentação (Docs/screenshots). Não salva nada nas cenas.
        [MenuItem("Ferramentas/Pixel Art/Capturar telas para a documentação")]
        public static void CapturarTelas()
        {
            string pasta = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "Docs", "screenshots"));
            Directory.CreateDirectory(pasta);

            // (cena, arquivo, objeto onde a câmera foca, painel de UI a mostrar)
            var fotos = new (string cena, string arquivo, string alvo, string ui)[]
            {
                ("Menu", "01_menu", null, "menu"),
                ("Jogo", "02_fase1_inicio", "Player", null),
                ("Jogo", "03_fase1_inimigos", "Inimigo2", null),
                ("Jogo", "04_fase1_plataformas", "Plataforma1", null),
                ("Jogo", "05_fase1_espinhos", "EspinhoGrande", null),
                ("Jogo", "06_fase1_rampa", "Espinho2", null),
                ("Jogo", "07_fase1_saida", "ObjetoVitoria", null),
                ("Jogo2", "08_fase2_inicio", "Player", null),
                ("Jogo2", "09_fase2_trofeu", "ObjetoVitoria", null),
                ("Jogo", "10_pause", "Player", "Pause"),
                ("Jogo", "11_game_over", "Player", "GameoverMenu"),
                ("Jogo2", "12_vitoria", "ObjetoVitoria", "TelaVitoria"),
            };
            const int W = 960, H = 540;
            const float Longe = 5000f; // a UI é fotografada longe do cenário e depois sobreposta

            foreach (var f in fotos)
            {
                EditorSceneManager.OpenScene($"Assets/Scenes/{f.cena}.unity", OpenSceneMode.Single);
                var cam = Camera.main;
                if (f.alvo != null)
                {
                    var alvo = GameObject.Find(f.alvo);
                    if (alvo != null) cam.transform.position = new Vector3(alvo.transform.position.x, alvo.transform.position.y, -10f);
                }

                foreach (var canvas in Object.FindObjectsByType<Canvas>(FindObjectsInactive.Include, FindObjectsSortMode.None))
                {
                    if (canvas.transform.parent != null && canvas.transform.parent.GetComponentInParent<Canvas>(true) != null) continue;
                    bool mostrar = f.ui != null;
                    canvas.gameObject.SetActive(mostrar);
                    if (!mostrar) continue;
                    // Coloca a UI na frente da câmera como se fosse a tela (W x H pixels)
                    canvas.renderMode = RenderMode.WorldSpace;
                    canvas.worldCamera = cam;
                    canvas.sortingOrder = 1000; // na frente de todos os sprites
                    var rt = (RectTransform)canvas.transform;
                    rt.sizeDelta = new Vector2(W, H);
                    float escala = cam.orthographicSize * 2f / H;
                    rt.localScale = Vector3.one * escala / (rt.parent != null ? rt.parent.lossyScale.x : 1f);
                    rt.position = new Vector3(cam.transform.position.x + Longe, cam.transform.position.y, cam.transform.position.z + 1f);
                    rt.rotation = cam.transform.rotation;
                    var scaler = canvas.GetComponent<CanvasScaler>();
                    if (scaler != null) scaler.enabled = false;
                    if (f.ui == "menu") continue;
                    foreach (Transform filho in canvas.transform)
                    {
                        var painel = filho.name == f.ui ? filho : filho.Find(f.ui);
                        filho.gameObject.SetActive(painel != null);
                        if (painel != null) painel.gameObject.SetActive(true);
                    }
                }
                Canvas.ForceUpdateCanvases();
                var cena = Render(cam, W, H);
                if (f.ui != null)
                {
                    var camUI = new GameObject("CamUI").AddComponent<Camera>();
                    camUI.CopyFrom(cam);
                    camUI.transform.position = cam.transform.position + Vector3.right * Longe;
                    camUI.clearFlags = CameraClearFlags.SolidColor;
                    camUI.backgroundColor = new Color(0, 0, 0, 0);
                    var ui = Render(camUI, W, H);
                    var a = cena.GetPixels();
                    var b = ui.GetPixels();
                    for (int i = 0; i < a.Length; i++) a[i] = Color.Lerp(a[i], b[i], b[i].a);
                    cena.SetPixels(a);
                    Object.DestroyImmediate(camUI.gameObject);
                    Object.DestroyImmediate(ui);
                }
                File.WriteAllBytes(Path.Combine(pasta, f.arquivo + ".png"), cena.EncodeToPNG());
                Object.DestroyImmediate(cena);
            }
            EditorSceneManager.OpenScene(Cenas[0], OpenSceneMode.Single);
            Debug.Log("[PixelArt] Capturas salvas em " + pasta);
        }

        static Texture2D Render(Camera cam, int w, int h)
        {
            var rt = new RenderTexture(w, h, 24, RenderTextureFormat.ARGB32);
            var antes = cam.targetTexture;
            cam.targetTexture = rt;
            cam.Render();
            RenderTexture.active = rt;
            var tex = new Texture2D(w, h, TextureFormat.RGBA32, false);
            tex.ReadPixels(new Rect(0, 0, w, h), 0, 0);
            tex.Apply();
            cam.targetTexture = antes;
            RenderTexture.active = null;
            rt.Release();
            return tex;
        }

        static Color Hex(string h)
        {
            ColorUtility.TryParseHtmlString("#" + h, out var c);
            return c;
        }
    }
}
