# Font sources

The dashboard uses **Plus Jakarta Sans** as its application typeface. It was chosen to complement the supplied MENTARI logo; an official MENTARI typeface specification was not supplied. The logo image itself is unmodified.

| Asset | Details |
| --- | --- |
| Font | `public/fonts/PlusJakartaSans-Latin-Variable.woff2` |
| Size | 27,348 bytes |
| Format | WOFF2, upright Latin subset, variable weight 200–800 |
| SHA-256 | `153fc85b70298beeb1d61a5f723331649e7f23bb77302a66e61cb3e2fbdb5e79` |
| Retrieved | 4 November 2026 |
| Provider | [Google Fonts CSS distribution](https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@200..800&display=swap) |
| Exact font source | [Google Fonts WOFF2, versioned v12 URL](https://fonts.gstatic.com/s/plusjakartasans/v12/LDIoaomQNQcsA88c7O9yZ4KMCoOg4Ko20yw.woff2) |
| Upstream project | [Tokotype / Plus Jakarta Sans](https://github.com/tokotype/PlusJakartaSans) |
| License source | [Google Fonts OFL notice](https://raw.githubusercontent.com/google/fonts/main/ofl/plusjakartasans/OFL.txt) |
| Included notice | [PlusJakartaSans-OFL.txt](../public/fonts/PlusJakartaSans-OFL.txt), 4,402 bytes |

The included SIL Open Font License 1.1 notice retains the project authors' copyright. Both font and notice are copied to the static build. The original downloaded font binary is retained without editing or conversion.

`index.html` preloads the local file. `src/style.css` declares the 200–800 weight range and `font-display: swap`, with Segoe UI/system fallbacks for unavailable glyphs or a failed font request. No font npm package, CDN stylesheet or runtime Google Fonts request is required. Source names and other data text are unchanged.

The primary theme colors, blue `#0d4c8f` and red `#d02030`, were sampled from solid-color areas of `public/images/Mentari Logo_Tagline Revamp_Color.png`. These colors style the interface; the existing voltage classes and map asset/status symbols retain their original colors.
