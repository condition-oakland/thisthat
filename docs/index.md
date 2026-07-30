# thisthatユーザーガイド

thisthatユーザーガイドへようこそ。

**thisthat** は、2 つのテキストを比較するデスクトップアプリです。左の **A** に *this*（元のテキスト）を貼り付け、右の **B** に *that*（変更後のテキスト）を貼り付けると、その差分が **1 つのペイン**に返ってきます。表示のしかたは Word の変更履歴と同じで、削除された文字は取り消し線、挿入された文字は下線です。

名前もそこから来ています。ワードマーク ~~this~~<u>that</u> がそのまま比較結果の凡例になっています。

<div class="tt-result" markdown="0">
<p>東京から<span class="tt-del">大阪</span><span class="tt-ins">京都</span>まで新幹線で行きます。</p>
</div>

## まずはここから

thisthat を初めて使う方は、以下のページからご覧ください。

- [はじめに](getting-started.md) — アプリの入手と起動、画面の構成
- [比較を実行する](comparing.md) — 貼り付けから比較までの基本操作
- [結果を読む](reading-the-result.md) — 色と記号の意味

## クイックリンク

| やりたいこと | 参照先 |
|---|---|
| テキストを比較する | [比較を実行する](comparing.md) |
| 文字単位・単語単位を切り替える | [比較のオプション](comparison-options.md) |
| 大小文字や空白の違いを無視する | [比較のオプション](comparison-options.md) |
| 変更箇所を順番に確認する | [変更箇所を移動する](navigating-changes.md) |
| 結果を人に渡す・保存する | [HTML で保存する](saving-html.md) |
| 表示言語・配色・テーマを変える | [設定](preferences.md) |
| 長い文書を比較する | [長いテキスト](long-texts.md) |
| 比較のしくみを知る | [比較エンジン](comparison-engine.md) |
| ショートカットキーを調べる | [キーボードショートカット](keyboard-shortcuts.md) |

!!! keypoint "覚えておきましょう"
    thisthat は、あなたが**比較を要求するまで何も比較しません**。テキストを入力したり貼り付けたりしただけでは結果は出ません。準備ができたら［**比較**］を押してください（**Ctrl+Enter**）。

## thisthat について

thisthat は [difff《デュフフ》](https://github.com/meso-cacase/difff) から着想を得たツールです。日本語と英語が混在したテキストでもうまく機能する、あのトークン分割の考え方を受け継いでいます。ただし difff とは別に書かれた独立した実装であり、difff の作者と関係はなく、その承認を受けたものでもありません。詳しくは[比較エンジン](comparison-engine.md)をご覧ください。
