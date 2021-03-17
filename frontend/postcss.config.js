const autoprefixer = require("autoprefixer");
const cssnano = require("cssnano");
const purgecss = require("@fullhuman/postcss-purgecss");

const production = !process.env.ROLLUP_WATCH;

module.exports = {
  plugins: [
    autoprefixer(),
    production &&
      purgecss({
        content: ["./src/**/*.html", "./src/**/*.svelte"],
        defaultExtractor: (content) =>
          [...content.matchAll(/(?:class)*([\w\d-/:%.]+)/gm)].map(
            ([_match, group, ..._rest]) => group
          ),
      }),
    production &&
      cssnano({
        preset: [
          "default",
          {
            discardComments: {
              removeAll: true,
            },
          },
        ],
      }),
  ],
};
