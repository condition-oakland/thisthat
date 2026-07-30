# Keyboard Shortcuts

Every shortcut in thisthat. The ones in the first table work from anywhere in the window — you do not need to click into a particular pane first.

## In the app

### Comparing

| Shortcut | What it does |
|---|---|
| `Ctrl+Enter` | Compare |
| `F5` | Compare |
| `Ctrl+S` | [Save the result as HTML](saving-html.md) |

`Enter` in either **Name** field also runs the comparison, so you can type a name and go.

### Moving between changes

| Shortcut | What it does |
|---|---|
| `F3` | [Next change](navigating-changes.md) |
| `Shift+F3` | Previous change |
| `Ctrl+Down` | Next change |
| `Ctrl+Up` | Previous change |

Both directions wrap around at the ends. Each jump selects the whole change, so `Ctrl+C` straight afterwards copies exactly it.

### Text size

| Shortcut | What it does |
|---|---|
| `Ctrl+plus` or `Ctrl+=` | Larger — in whichever pane the cursor is in |
| `Ctrl+minus` | Smaller — likewise |
| `Ctrl+0` | Reset that pane to the default size |
| `Ctrl+scroll` | Larger / smaller — in whichever pane the **mouse** is over |

The result pane keeps its own size, separate from A and B; see [Reading the Result](reading-the-result.md#text-size). Both sizes are remembered between runs.

### In the result pane

The result pane is read-only, but selecting and copying work normally.

| Shortcut | What it does |
|---|---|
| `Ctrl+C` | Copy the selection |
| `Ctrl+A` | Select the whole result |
| Arrow keys | Move the caret |
| `Shift` + arrows | Extend the selection |

Typing and pasting are ignored.

### In dialogs

| Shortcut | What it does |
|---|---|
| `Enter` | OK / accept |
| `Escape` | Cancel |

This covers the [Preferences](preferences.md) dialog and the dialog that appears after saving.

## In the exported HTML page

The [saved page](saving-html.md) has its own navigation, and it deliberately does **not** use F3 — that belongs to the browser's own Find.

| Shortcut | What it does |
|---|---|
| `n` | Next change |
| `p` | Previous change |
| Click in the result | Set where `n` and `p` carry on from |
