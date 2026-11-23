const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');
const CopyPlugin = require('copy-webpack-plugin');

module.exports = merge(common, {
  mode: 'production',
  plugins: [
    new CopyPlugin({
      patterns: [
        { from: 'index.html', to: 'index.html' },
        { from: 'en', to: 'en', globOptions: { ignore: ['**/sonder_kaco_light.html'] } },
        { from: 'fi', to: 'fi' },
        { from: 'img', to: 'img' },
        { from: 'css/weddings.css', to: 'css/weddings.css' },
        { from: 'js/analytics.js', to: 'js/analytics.js' },
        { from: 'fonts', to: 'fonts' },
        { from: 'download', to: 'download' },
        { from: 'icon.svg', to: 'icon.svg' },
        { from: 'favicon_*.png', to: '[name][ext]' },
        { from: 'sonder-moments-*.webp', to: '[name][ext]' },
        { from: 'robots.txt', to: 'robots.txt' },
        { from: 'sitemap.xml', to: 'sitemap.xml' },
        { from: '404.html', to: '404.html' },
        { from: 'site.webmanifest', to: 'site.webmanifest' },
      ],
    }),
  ],
});
