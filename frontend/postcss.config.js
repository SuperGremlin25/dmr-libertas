module.exports = {
  plugins: {
    'postcss-import': {},
    'tailwindcss/nesting': {},
    'tailwindcss': {},
    'autoprefixer': {},
    'postcss-preset-env': {
      stage: 1,
      features: {
        'focus-visible-pseudo-class': false,
        'focus-within-pseudo-class': false,
      },
    },
    'cssnano': process.env.NODE_ENV === 'production' ? { preset: 'default' } : false,
  },
};
