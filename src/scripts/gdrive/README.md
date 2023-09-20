# What

Downloads the assets from Google Drive using the `gdrive` tool - this is used
over direct API access because `gdrive` offers a ready-made recursive download
option.

# Requirements

* [gdrive](https://github.com/glotlabs/gdrive)

# Authentication

You will need access to the Astro Pi GCP, and create a suitable
OAuth Client Id. Then, add the client id to `gdrive` using `gdrive account add` and enter
the relevant details. This will store your secrets in `~/.config/gdrive3/` so make sure this
file is protected.
