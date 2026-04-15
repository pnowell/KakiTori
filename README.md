# Kanji KakiTori : 漢字書き取り

[Try it](https://pnowell.github.io/KakiTori)
## Overview

KakiTori is a Japanese kanji writing practice app.  There are some hard-coded grade 1 and grade 2 kanji.  It randomly shows either an English meaning or hiragana reading and you attempt to write the kanji in the provided drawing canvas.

When you miss a stroke 3 times, it provides you with a hint, and that kanji is considered "missed".  If you can finish writing the kanji without needing any hints, it's counted as correct.

Missed kanji will show up more frequently to help you review kanji that are less familiar.  As you get kanji correct, it will gradually appear less and less frequently, allowing other kanji to be introduced.

Scoring and kanji selection is stored locally, so it should remember as long as you play on the same browser.  It does **not** do any cloud storage so those selections and scores won't synchronize with other browsers.
