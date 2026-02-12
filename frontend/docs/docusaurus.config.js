// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

const EXTERNAL_URL =
  process.env.EXTERNAL_SITE_URL ?? 'https://www.example.com';

const BASE_URL =
  "/" + (process.env.EXTERNAL_BASE_URL ?? 'docs/');

console.log('BASE_URL =', BASE_URL);
console.log('EXTERNAL_URL =', EXTERNAL_URL);

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'I2WG Documentation',
  tagline: 'Documentation for I2WG framework',
  favicon: 'img/I2WG.png',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: EXTERNAL_URL,
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/intent2Workflow/docs/',//',//BASE_URL,

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'dtim-upc', // Usually your GitHub org/user name.
  projectName: 'Intents2Workflows', // Usually your repo name.

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          routeBasePath: '/'
        },
        theme: {
          customCss: './src/css/custom.css',
        },
        blog: false,
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'Intent2Workflows',
        logo: {
          alt: 'DTIM',
          src: 'img/I2WG.png',
          href: `${EXTERNAL_URL}/intent2Workflow`,
        },
        items: [
          {
            href: 'https://github.com/dtim-upc/Intents2Workflows',
            position: 'right',
            className: 'header-github-link',
          },
        ],
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
  stylesheets: [
  'https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap',
  'https://cdn.jsdelivr.net/npm/@mdi/font@7.2.96/css/materialdesignicons.min.css',
  'https://cdn.jsdelivr.net/npm/@quasar/extras@1.0.0/material-icons/material-icons.css',
],

};

export default config;
