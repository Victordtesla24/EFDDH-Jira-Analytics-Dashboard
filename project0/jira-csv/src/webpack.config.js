export default {
  mode: process.env.NODE_ENV || 'development',
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-react'],
            cacheDirectory: true, // Enable caching for faster rebuilds
          },
        },
      },
      // ...other rules...
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
};