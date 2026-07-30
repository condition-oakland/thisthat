# Preferences

**Preferences…** at the bottom right of the window opens a dialog with three things: the interface **language**, the **light / dark** switch, and a **colour** picker for each of the four diff colours.

Changes apply to the window **as you make them**, so you can judge them against whatever comparison you already have on screen.

| Button | Effect |
|---|---|
| **OK** | Keep the changes |
| **Cancel** | Put back exactly what you started with |
| **Reset to defaults** | Restore the shipped colours **for the theme you are editing** |

**Escape** cancels and **Enter** accepts, as usual.

## Language

The interface is available in **English** and **日本語**.

The choice takes effect **immediately** — the window is relabelled around whatever you have in it, so nothing is lost. Your two texts and your result stay exactly where they are. It is remembered for next time.

The language also reaches the **HTML export**: a comparison saved while the app is in Japanese has a Japanese title, header and legend, so the page reads the way the window read when you saved it. See [Saving as HTML](saving-html.md#the-language-is-baked-in-too).

What the setting never touches is the text being compared, which is only ever your own.

!!! keypoint "Good to know"
    The app ships in **English** and stays there until you choose otherwise. It does not guess from your system locale — which language the buttons are in is a preference of the person reading, not a property of the machine.

## Theme

**Light** and **Dark**.

Switching the theme also swaps the **window icon** between its black and white inks, so the mark stays visible against the title bar rather than sinking into it. On Windows the title bar itself follows the theme too.

The theme is what the [exported page](saving-html.md#the-colours-are-baked-in) is written in, so it is worth setting before you save rather than after.

## Colours

Four colours are yours to change:

| Setting | What it colours |
|---|---|
| **Deleted text** | The struck-through characters |
| **Deleted highlight** | The band behind them |
| **Inserted text** | The underlined characters |
| **Inserted highlight** | The band behind them |

Clicking any of them opens the system colour picker, titled with which colour and which theme you are editing.

!!! keypoint "Keep in mind"
    **Light and dark keep their own colours.** Setting one does not disturb the other, and **Reset to defaults** only resets the theme you are currently editing. If you want both back as shipped, reset each one.

### The preview

A **Preview** line in the dialog shows a short sentence with one word deleted and another inserted, so you can see how the four colours read *together* rather than one at a time — which is the only way to tell whether the ink is legible over its own highlight.

The preview sentence is written in the interface language, because what it is for is judging the highlight colours against the script you will actually be reading through them.

### Why the defaults are loud

The shipped colours are deliberately vivid. Muted pastels read as tasteful and scan badly: at a glance down a long comparison you want the changed runs to shout. The ink over each highlight is a deep tint of the highlight itself rather than plain black, so a run stays legible as text and not just as a marked band.

If they are too much for you, change them — that is what the setting is for.

## Where your choices are stored

Everything — language, theme, colours, and both [text sizes](reading-the-result.md#text-size) — is remembered between runs in:

```
%APPDATA%\thisthat\settings.json
```

On platforms without `%APPDATA%`, it goes to `~/.config/thisthat/settings.json` instead.

**Delete that file to go back to the defaults.** A corrupt or hand-edited one is ignored rather than fatal: every value is validated on load and anything unrecognised is quietly dropped, so bad settings can never stop the app starting.

!!! keypoint "Good to know"
    If you used this app when it was called **difff**, your colours are still in `%APPDATA%\difff-desktop\`. thisthat reads them once, the first time it finds nothing under its own name, and writes them forward. The old file is left on disk rather than deleted — an older copy of the app may still be installed, and settings are not ours to throw away.

If the settings file cannot be written — a locked profile, a full disk — thisthat tells you so and carries on. Your choices still apply to the session you are in; they just will not survive it.
