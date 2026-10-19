# Lune profile maintenance

This is the profile repository for [Nouvelle-Lune](https://github.com/Nouvelle-Lune). GitHub displays the root README on the profile.

## What updates

The **Refresh the profile** workflow runs every day at 03:23 UTC, when its source files change on `main`, or when started manually in Actions. It regenerates the activity card and contribution snakes, and commits changed assets to `main`. GitHub can delay scheduled runs, and scheduled workflows in inactive public repositories may be disabled by GitHub after 60 days without repository activity; re-enable the workflow in Actions if that happens.

The workflow uses the repository's automatic `GITHUB_TOKEN`; no personal token or extra secrets are needed. It reads public profile data and writes generated assets. The two external actions are pinned to full commit SHAs.

## Activity card definitions

- **Contributions:** GitHub's `totalContributions` for the default rolling contribution calendar (the last year), not a commit count.
- **Active days:** dates in that same calendar with at least one contribution.
- **Original repos:** public repositories owned by the account, excluding forks; this includes the profile repository itself.
- **7D activity:** daily contribution counts for the seven complete UTC dates before the update date. Bar heights scale relative to the largest count in that seven-day window. No contributions means an empty bar.
- **Updated:** the UTC date when the assets were rendered.

Only GitHub's returned aggregate counts are used. The generated images contain no private repository names, credentials, or external image-service calls. API errors fail the workflow instead of substituting invented stats.

## Edit or regenerate

Edit `README.md` for copy, links and layout. `scripts/palette.json` is the shared source of colors for the SVG renderer and the snake action. The selected design is **A / Native Blue**, using the [Lune dark palette](https://github.com/Nouvelle-Lune/lune-pi/blob/main/packages/pi-core-theme/src/palettes/pi-core-dark.json). The light contribution trail uses the matching Lune light palette. These are explicit palette snapshots; upstream theme changes do not silently restyle the profile.

Edit `scripts/render.py` for the native terminal header, the ten-row Lune crescent, responsive activity cards and contribution panels. Wide and mobile variants are selected with `<picture>`. The contribution animation follows the viewer's light/dark preference. All art is native SVG with no remote fonts, scripts or raster dependencies. The header and activity cards are static; the third-party snake animation follows its upstream implementation.

To regenerate and publish using the repository workflow:

```bash
gh workflow run profile.yml
```

For local rendering, Python 3.10+ is sufficient. The generator requires `--data` with the GraphQL JSON response, `--date` with its UTC snapshot date, and `--snakes` with a directory containing raw `snake.svg` and `snake-dark.svg` from [Platane/snk](https://github.com/Platane/snk). Missing files, dates or fields fail visibly. The renderer embeds the original snake SVG and its animation inside matching Lune panels.
