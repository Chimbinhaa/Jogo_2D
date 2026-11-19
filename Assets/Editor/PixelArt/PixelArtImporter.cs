using UnityEditor;
using UnityEngine;

namespace PixelArt
{
    /// <summary>
    /// Configura sozinho qualquer imagem colocada em "Assets/Art/Sprites" para pixel art:
    /// filtro Point (sem borrar), sem compressão, sem mipmaps e o PPU certo de cada sprite.
    /// (Só roda dentro do Editor da Unity, não vai para o jogo final.)
    /// </summary>
    public class PixelArtImporter : AssetPostprocessor
    {
        const string PastaSprites = "Assets/Art/Sprites/";

        // Pixels Per Unit de cada sprite. Os valores fazem o desenho novo ocupar
        // exatamente o mesmo tamanho do desenho antigo na cena, assim nenhum
        // Transform ou colisor precisou ser mexido.
        struct Config
        {
            public float ppu;
            public Vector4 borda; // 9-slice: esquerda, baixo, direita, cima (em pixels)
            public Config(float ppu, Vector4 borda = default) { this.ppu = ppu; this.borda = borda; }
        }

        static Config ConfigPara(string arquivo)
        {
            switch (arquivo)
            {
                case "agenor":                 return new Config(24.49f);         // 18x36 px -> 0.73 x 1.47
                case "demonio_coracao_0":
                case "demonio_coracao_1":      return new Config(15.67f);         // 21x14 px -> 1.34 x 0.89
                case "espinho":                return new Config(16.06f);         // 22x14 px -> 1.37 x 0.87
                case "estalagmite":            return new Config(166.4f);         // 228x142 px (pré-esticado)
                case "tile_rocha":             return new Config(16f, new Vector4(2, 2, 2, 4));
                case "plataforma_dissolvivel": return new Config(200f);           // 200x200 px -> 1 x 1
                case "trofeu_0":
                case "trofeu_1":
                case "trofeu_2":
                case "trofeu_3":               return new Config(10.49f);         // 30x31 px -> 2.86 x 2.96
                case "fundo_inferno":          return new Config(102.3f);         // 757x413 px -> 7.4 x 4.04
                case "botao":
                case "botao_hover":
                case "botao_press":            return new Config(100f, new Vector4(4, 4, 4, 4));
                case "painel":                 return new Config(100f, new Vector4(10, 10, 10, 10));
                case "faixa_titulo":           return new Config(100f, new Vector4(8, 5, 8, 5));
                case "fundo_menu":             return new Config(100f);
                default:                       return new Config(16f);            // padrão: 16 px = 1 unidade
            }
        }

        void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(PastaSprites)) return;

            var importer = (TextureImporter)assetImporter;
            var cfg = ConfigPara(System.IO.Path.GetFileNameWithoutExtension(assetPath));

            importer.textureType = TextureImporterType.Sprite;
            importer.spriteImportMode = SpriteImportMode.Single;
            importer.filterMode = FilterMode.Point;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.mipmapEnabled = false;
            importer.alphaIsTransparency = true;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.maxTextureSize = 2048;
            importer.spritePixelsPerUnit = cfg.ppu;

            var settings = new TextureImporterSettings();
            importer.ReadTextureSettings(settings);
            settings.spriteMeshType = SpriteMeshType.FullRect; // necessário para o modo Tiled
            settings.spriteBorder = cfg.borda;
            settings.spriteAlignment = (int)SpriteAlignment.Center;
            settings.spriteExtrude = 0;
            importer.SetTextureSettings(settings);
        }
    }
}
