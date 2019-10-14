var path = require("path");
var webpack = require("webpack");
var BundleTracker = require("webpack-bundle-tracker");
var terserPlugin = require("terser-webpack-plugin");
var uglifyPlugin = require("uglifyjs-webpack-plugin");

module.exports = {

    context: __dirname,
    entry:  {
        invoicing: './js/invoicing',
        inventory: './js/inventory',
        widgets: './js/widgets',
    },
    output: {
        path: path.resolve('./bundles/'),
        filename: '[name].js',
    },
    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
    ],
    mode: 'development',

    module: {
        rules: [
            {
                test: /\.css$/,
                'loader': 'style-loader'
            },
            {
                test: /\.css$/,
                loader: 'css-loader',
                query: {
                    modules: true,
                    localIdentName: '[name]__[local]__[hash:64:5]'
                }
            },
            {
                test: /\.js$/,
                loader: 'babel-loader',
                exclude: /node_modules/,
                query: {
                    presets: ['stage-2','react']//stage 2 for class level attrs and autobind
                }
            }
        ]
    },

    resolve: {
        extensions: [ '.js', '.jsx']
    },
    /*
    optimization: {
        minimize:true,
        minimizer: [new terserPlugin()]
    }
    */
}