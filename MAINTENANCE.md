# Arcade maintenance

This is the profile repository for [Nouvelle-Lune](https://github.com/Nouvelle-Lune). GitHub displays the root README on the profile.

## What updates

The **Refresh the arcade** workflow runs every day at 03:23 UTC, when its source files change on `main`, or when started manually in Actions. It regenerates the player card and contribution snakes, and commits changed assets to `main`. GitHub can delay scheduled runs, and scheduled workflows in inactive public repositories may be disabled by GitHub after 60 days without repository activity; re-enable the workflow in Actions if that happens.

The workflow uses the repository's automatic `GITHUB_TOKEN`; no personal token or extra secrets are needed. It reads public profile data and writes generated assets. The two external actions are pinned to full commit SHAs.

## Player card definitions

- **Contributions:** GitHub's `totalContributions` for the default rolling contribution calendar (the last year), not a commit count.
- **Active days:** dates in that same calendar with at least one contribution.
- **Original repos:** public repositories owned by the account, excluding forks; this includes the profile repository itself.
- **7D activity:** daily contribution counts for the seven complete UTC dates before the saved date. Each five-segment bar scales relative to the largest count in that seven-day window. No contributions means an empty bar.
- **Saved:** the UTC date when the assets were rendered.

Only GitHub's returned aggregate counts are used. The generated images contain no private repository names, credentials, or external image-service calls. API errors fail the workflow instead of substituting invented stats.

## Edit or regenerate

Edit `README.md` for copy, links and layout. Edit `scripts/render.py` for the palette, pixel font, mascot and cards. All art is native SVG with no remote fonts, scripts or raster dependencies. Wide and mobile variants are selected with `<picture>`; the snake also follows the viewer's light/dark preference. Custom animation stops when the viewer requests reduced motion; the third-party snake animation follows its upstream implementation.

With Python 3.10+ and an authenticated GitHub CLI:

```bash
gh api graphql -F query=@scripts/profile.graphql -f login=Nouvelle-Lune > /tmp/nouvelle-lune-profile.json
python3 scripts/render.py --data /tmp/nouvelle-lune-profile.json --date "$(date -u +%F)"
gh workflow run arcade.yml
```

The generator deliberately requires a data snapshot and its UTC date. Missing dates or fields fail visibly. Snake images are produced by the workflow with [Platane/snk](https://github.com/Platane/snk).
