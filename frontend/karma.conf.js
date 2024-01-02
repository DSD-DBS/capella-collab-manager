/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

// Karma configuration file, see link for more information
// https://karma-runner.github.io/1.0/config/configuration-file.html

const webpack = require("webpack");
const path = require("path");

const webpackConfig = {
  mode: "development",
  module: {
    rules: [
      {
        test: /\.ts$/,
        loader: "tslint-loader",
        exclude: /node_modules/,
        enforce: "pre",
      },
      {
        test: /\.ts$/,
        loader: "ts-loader?silent=true",
        exclude: /node_modules/,
      },
      {
        test: /\.ts$/,
        exclude: /(node_modules|\.spec\.ts$)/,
        loader: "coverage-istanbul-loader",
        enforce: "post",
        options: {
          esModules: true,
        },
      },
    ],
  },
  plugins: [
    new webpack.SourceMapDevToolPlugin({
      filename: null,
      test: /\.(ts|js)($|\?)/i,
    }),
  ],
  resolve: {
    extensions: [".ts", ".js"],
  },
};

module.exports = function (config) {
  config.set({
    basePath: "",
    frameworks: ["jasmine", "@angular-devkit/build-angular"],
    plugins: [
      require("karma-jasmine"),
      require("karma-chrome-launcher"),
      require("karma-jasmine-html-reporter"),
      require("karma-coverage"),
      require("karma-coverage-istanbul-reporter"),
      require("@angular-devkit/build-angular/plugins/karma"),
      require("webpack"),
    ],
    client: {
      jasmine: {
        // you can add configuration options for Jasmine here
        // the possible options are listed at https://jasmine.github.io/api/edge/Configuration.html
        // for example, you can disable the random execution with `random: false`
        // or set a specific seed with `seed: 4321`
        failSpecWithNoExpectations: true,
        random: false,
      },
      clearContext: false, // leave Jasmine Spec Runner output visible in browser
    },
    jasmineHtmlReporter: {
      suppressAll: true, // removes the duplicated traces
    },
    coverageIstanbulReporter: {
      fixWebpackSourcePaths: true,
      reports: ["html", "text-summary"],
      dir: path.join(__dirname, "test-results", "istanbul-coverage"),
    },
    reporters: ["progress", "kjhtml", "coverage-istanbul"],
    port: 9876,
    colors: true,
    logLevel: config.LOG_INFO,
    autoWatch: true,
    browsers: ["Chrome"],
    singleRun: false,
    restartOnFileChange: true,
    webpackConfig: webpackConfig,
  });
};
