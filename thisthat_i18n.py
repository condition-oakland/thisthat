"""Interface language for thisthat -- the string table and the current choice.

Every piece of text the app puts on screen lives here, in one table keyed by a
short name, with one column per language.  Nothing in this module touches
tkinter, so the HTML exporter can translate its own wording from the same
table without dragging the UI in with it.

The current language is module state rather than something threaded through
every call.  A one-window desktop app has exactly one interface language at a
time, and passing it into every label would cost far more than it could ever
buy: what matters is that ``t("compare")`` is short enough to use everywhere a
literal string would otherwise have been typed.

Switching language does not rebuild the window.  Widgets whose text comes from
here register themselves with a Localized (below), which re-reads the table on
demand -- so the choice takes effect the moment it is made, with the two texts
and the result still on screen.
"""

DEFAULT_LANGUAGE = "en"

# (code, name).  The names are endonyms and stay as they are in both
# languages: someone who has landed in the wrong one needs to recognise their
# own language in the list, not read a translation of its name.
LANGUAGES = (
    ("en", "English"),
    ("ja", "日本語"),
)

STRINGS = {
    "en": {
        # -- toolbar ---------------------------------------------------------
        "load_a": "Load A…",
        "load_b": "Load B…",
        "swap": "Swap",
        "clear": "Clear",
        "compare_by": "Compare by:",
        "mode_smart": "smart (words + characters)",
        "mode_char": "character",
        "mode_word": "word",
        "ignore_case": "Ignore case",
        "ignore_space": "Ignore spaces",
        "save_html": "Save HTML…",
        "compare": "Compare",
        # -- panes -----------------------------------------------------------
        "pane_a": "A  —  this",
        "pane_b": "B  —  that",
        "pane_result": "Result  —  single pane",
        "name_label": "Name:",
        "prev_change": "◀ Previous",
        "next_change": "Next ▶",
        "tip_prev": "Previous change  (Shift+F3)",
        "tip_next": "Next change  (F3)",
        "font_size": "Font size",
        # These two resize the result alone, which is not something the bar can
        # say in the space it has -- and the wheel, which resizes whichever
        # pane you are already reading, is worth more than either button.
        "tip_zoom_out": "Smaller result text  ·  "
                        "Ctrl+scroll resizes the pane under the pointer",
        "tip_zoom_in": "Larger result text  ·  "
                       "Ctrl+scroll resizes the pane under the pointer",
        "points": "%d pt",
        # -- status line and counter -----------------------------------------
        "ready": "Paste text into A and B, then press Compare (Ctrl+Enter).",
        "comparing": "Comparing…",
        "compare_failed_status": "Comparison failed.",
        "compare_cancelled": "Comparison cancelled.",
        "identical": "✓  The two texts are identical.",
        "summary": "%d change region(s)   —   %d character(s) deleted, "
                   "%d character(s) inserted",
        "no_jump": "There are no changes to jump to.",
        "wrapped_first": "Wrapped to the first change.",
        "wrapped_last": "Wrapped to the last change.",
        "loaded": "Loaded %s into %s. Press Compare when both sides are ready.",
        "saved": "Saved to %s",
        "prefs_save_failed": "Preferences could not be saved: %s",
        "no_changes": "✓  no changes",
        "change_count_one": "%d change",
        "change_count_many": "%d changes",
        "change_of": "change %d of %d",
        # -- progress --------------------------------------------------------
        "processing": "Processing…",
        "comparing_texts": "Comparing texts…",
        "rendering": "Rendering result…",
        # -- shared buttons --------------------------------------------------
        "ok": "OK",
        "cancel": "Cancel",
        # -- preferences -----------------------------------------------------
        "prefs_button": "Preferences…",
        "prefs_title": "Preferences",
        "theme_group": "Theme",
        "theme_light": "Light",
        "theme_dark": "Dark",
        # "UI language", not "Language": a diff tool asking about language
        # invites the reading that it is about the texts being compared -- a
        # setting for English prose versus Japanese -- which it is not.
        "language_group": "UI language",
        "colours_group": "Colours",
        "colour_del_fg": "Deleted text",
        "colour_del_bg": "Deleted highlight",
        "colour_ins_fg": "Inserted text",
        "colour_ins_bg": "Inserted highlight",
        "preview": "Preview",
        "preview_equal_1": "The quick brown fox ",
        "preview_delete": "jumped",
        "preview_insert": "leapt",
        "preview_equal_2": " over the lazy dog.",
        "reset_defaults": "Reset to defaults",
        "colour_picker_title": "%s — %s theme",
        "colours_not_saved": "Your colours are applied, but could not be "
                             "saved for next time:\n%s",
        # -- file commands ---------------------------------------------------
        "load_dialog_title": "Load text into %s",
        "save_dialog_title": "Save result as HTML",
        "filetype_text": "Text files",
        "filetype_html": "HTML file",
        "filetype_all": "All files",
        "could_not_read": "Could not read the file:\n%s",
        "could_not_save": "Could not save the file:\n%s",
        "nothing_to_save": "There is no result to save yet.",
        "compare_failed": "The comparison failed:\n%s",
        "saved_heading": "Saved %s",
        "open_file": "Open the file",
        "show_in_folder": "Show it in the folder",
        "could_not_open": "Could not open it:\n%s",
        # -- HTML export -----------------------------------------------------
        "html_heading": "result",
        "html_title_plain": "thisthat result",
        "html_title_named": "thisthat — %s vs %s",
        "html_side_a": "this",
        "html_side_b": "that",
        "html_label_a": "A (this)",
        "html_label_b": "B (that)",
        # The exported page navigates with n / p, not F3: F3 is the browser's
        # own Find, and the page has no business taking it away.  The tips
        # carry the click hint because a caret on a page you cannot type into
        # is not something anyone would think to look for.
        "html_tip_prev": "Previous change  (p)  ·  "
                         "click in the text to start somewhere else",
        "html_tip_next": "Next change  (n)  ·  "
                         "click in the text to start somewhere else",
        "html_legend_del": "deleted",
        "html_legend_ins": "inserted",
        "html_only_in": "text only in %s",
        "html_meta_identical": "identical",
        "html_meta_summary": "%d change region(s), %d character(s) deleted, "
                             "%d character(s) inserted",
    },
    "ja": {
        # -- toolbar ---------------------------------------------------------
        # Kept deliberately terse.  A kanji is two Latin characters wide, so a
        # toolbar translated at its natural length is half again as wide as
        # the English one and starts pushing controls off a narrow window --
        # and 読込 / 空白 on a button are ordinary Japanese UI wording, not an
        # abbreviation anyone has to decode.
        "load_a": "A を読込…",
        "load_b": "B を読込…",
        "swap": "入れ替え",
        "clear": "クリア",
        "compare_by": "比較単位:",
        "mode_smart": "スマート（単語＋文字）",
        "mode_char": "文字単位",
        "mode_word": "単語単位",
        "ignore_case": "大小文字を無視",
        "ignore_space": "空白を無視",
        "save_html": "HTML 保存…",
        "compare": "比較",
        # -- panes -----------------------------------------------------------
        "pane_a": "A  —  this",
        "pane_b": "B  —  that",
        "pane_result": "結果  —  1 つのペインに表示",
        "name_label": "名前:",
        "prev_change": "◀ 前の変更",
        "next_change": "次の変更 ▶",
        "tip_prev": "前の変更箇所へ  (Shift+F3)",
        "tip_next": "次の変更箇所へ  (F3)",
        "font_size": "文字サイズ",
        "tip_zoom_out": "結果の文字を小さく  ·  "
                        "Ctrl+スクロールでポインタのあるペインを拡大縮小",
        "tip_zoom_in": "結果の文字を大きく  ·  "
                       "Ctrl+スクロールでポインタのあるペインを拡大縮小",
        "points": "%d pt",
        # -- status line and counter -----------------------------------------
        "ready": "A と B にテキストを貼り付けて［比較］を押してください"
                 "（Ctrl+Enter）。",
        "comparing": "比較中…",
        "compare_failed_status": "比較に失敗しました。",
        "compare_cancelled": "比較を中止しました。",
        "identical": "✓  2 つのテキストは同一です。",
        "summary": "変更箇所 %d 件   —   削除 %d 文字、挿入 %d 文字",
        "no_jump": "移動できる変更箇所はありません。",
        "wrapped_first": "最初の変更箇所に戻りました。",
        "wrapped_last": "最後の変更箇所に戻りました。",
        "loaded": "%s を %s に読み込みました。"
                  "両方そろったら［比較］を押してください。",
        "saved": "%s に保存しました",
        "prefs_save_failed": "設定を保存できませんでした: %s",
        "no_changes": "✓  変更なし",
        "change_count_one": "変更 %d 件",
        "change_count_many": "変更 %d 件",
        "change_of": "変更 %d / %d 件",
        # -- progress --------------------------------------------------------
        "processing": "処理中…",
        "comparing_texts": "テキストを比較中…",
        "rendering": "結果を表示中…",
        # -- shared buttons --------------------------------------------------
        "ok": "OK",
        "cancel": "キャンセル",
        # -- preferences -----------------------------------------------------
        "prefs_button": "設定…",
        "prefs_title": "設定",
        "theme_group": "テーマ",
        "theme_light": "ライト",
        "theme_dark": "ダーク",
        "language_group": "表示言語",
        "colours_group": "色",
        "colour_del_fg": "削除された文字",
        "colour_del_bg": "削除のハイライト",
        "colour_ins_fg": "挿入された文字",
        "colour_ins_bg": "挿入のハイライト",
        "preview": "プレビュー",
        # A sentence with one word swapped for another, as in the English
        # preview -- but written out in Japanese, because what the preview is
        # for is judging the highlight colours against the script you will
        # actually be reading through them.
        "preview_equal_1": "東京から",
        "preview_delete": "大阪",
        "preview_insert": "京都",
        "preview_equal_2": "まで新幹線で行きます。",
        "reset_defaults": "既定値に戻す",
        "colour_picker_title": "%s — %s テーマ",
        "colours_not_saved": "色は適用されましたが、次回以降のために"
                             "保存できませんでした:\n%s",
        # -- file commands ---------------------------------------------------
        "load_dialog_title": "%s にテキストを読み込む",
        "save_dialog_title": "結果を HTML で保存",
        "filetype_text": "テキストファイル",
        "filetype_html": "HTML ファイル",
        "filetype_all": "すべてのファイル",
        "could_not_read": "ファイルを読み込めませんでした:\n%s",
        "could_not_save": "ファイルを保存できませんでした:\n%s",
        "nothing_to_save": "保存できる結果がまだありません。",
        "compare_failed": "比較に失敗しました:\n%s",
        "saved_heading": "%s を保存しました",
        "open_file": "ファイルを開く",
        "show_in_folder": "フォルダーで表示",
        "could_not_open": "開けませんでした:\n%s",
        # -- HTML export -----------------------------------------------------
        "html_heading": "比較結果",
        "html_title_plain": "thisthat 比較結果",
        "html_title_named": "thisthat — %s と %s",
        "html_side_a": "this",
        "html_side_b": "that",
        "html_label_a": "A（this）",
        "html_label_b": "B（that）",
        "html_tip_prev": "前の変更箇所へ  (p)  ·  "
                         "本文をクリックすると開始位置を変えられます",
        "html_tip_next": "次の変更箇所へ  (n)  ·  "
                         "本文をクリックすると開始位置を変えられます",
        "html_legend_del": "削除",
        "html_legend_ins": "挿入",
        "html_only_in": "%s にのみある文字",
        "html_meta_identical": "差分なし",
        "html_meta_summary": "変更箇所 %d 件、削除 %d 文字、挿入 %d 文字",
    },
}

_current = DEFAULT_LANGUAGE


def languages():
    return LANGUAGES


def is_language(code):
    return any(code == entry[0] for entry in LANGUAGES)


def language():
    return _current


def set_language(code):
    """Switch language.  Anything unrecognised falls back to the default."""
    global _current
    _current = code if is_language(code) else DEFAULT_LANGUAGE
    return _current


def t(key, *args):
    """The current language's wording for *key*, %-formatted with *args*.

    A key missing from the current language falls through to the default one
    rather than blanking the label, and a key missing everywhere shows itself
    -- an untranslated string should look wrong on screen, not disappear.
    """
    text = STRINGS.get(_current, {}).get(key)
    if text is None:
        text = STRINGS[DEFAULT_LANGUAGE].get(key, key)
    return text % args if args else text


class Localized:
    """The widgets in one window whose text comes from the string table.

    Each entry is a callable that re-applies one piece of text, so a language
    change is ``refresh()`` and nothing else -- no walking the widget tree, and
    no chance of a label that was set once at build time and then forgotten.

    A window owns its own registry and drops it when it closes, which is why
    entries never need removing: a dialog's list dies with the dialog.
    """

    def __init__(self):
        self._entries = []

    def add(self, apply, result=None):
        """Register *apply*, run it now, and hand back *result*."""
        apply()
        self._entries.append(apply)
        return result

    def widget(self, widget, key, *args, **kw):
        """Register a widget's -text (or another option, via option=...)."""
        option = kw.pop("option", "text")
        return self.add(
            lambda: widget.configure(**{option: t(key, *args)}), widget)

    def button(self, button, key, *args):
        """Register a FlatButton, which is a frame and has no -text of its own."""
        return self.add(lambda: button.set_text(t(key, *args)), button)

    def refresh(self):
        for apply in self._entries:
            apply()
