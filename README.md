# エイチクリニック新宿 デモサイト（SP）

Figmaのワイヤーフレーム（ページ「v4_ワイヤー（SP） あしらい追加版」）を、実機確認用に書き出したデモサイトです。

- `public/` … 静的ファイル（Cloudflare Pages のビルド出力ディレクトリ）
- `functions/_middleware.js` … パスワード保護（パスワード本体は置かずハッシュのみ。Cloudflareの環境変数 `DEMO_PASSWORD` を設定するとそちらが優先）
- ページ画像は Figma から2倍で書き出し、セクション単位に分割したもの。リンク位置はFigmaの遷移先データから自動配置

Cloudflare Pages 設定：フレームワーク「なし」／ビルドコマンド なし／ビルド出力ディレクトリ `public`
