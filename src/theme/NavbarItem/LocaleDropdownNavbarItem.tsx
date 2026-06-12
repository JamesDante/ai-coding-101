/**
 * Swizzle: robust locale switcher.
 *
 * Problem 1 — The original Docusaurus component uses React Router <Link>,
 *   which does SPA navigation. Switching locales means switching builds,
 *   so SPA navigation silently fails or does nothing.
 *
 * Problem 2 — useAlternatePageUtils relies on siteConfig.baseUrl, but
 *   Docusaurus sets baseUrl to the locale-specific value in each build
 *   (e.g. '/ai-coding-101/zh-Hans/' in the zh-Hans build). This causes
 *   pathnameSuffix to be wrong, so the generated URL stays in zh-Hans
 *   regardless of which locale you click.
 *
 * Fix: derive the ROOT base URL by stripping the current locale suffix from
 *   siteConfig.baseUrl, then build the target URL manually using plain <a href>
 *   (which forces a full page reload).
 */
import React from 'react';
import type {ReactNode} from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import {useLocation} from '@docusaurus/router';

/**
 * Build the href for switching to targetLocale.
 *
 * Works regardless of whether siteConfig.baseUrl is root ('/ai-coding-101/')
 * or locale-specific ('/ai-coding-101/zh-Hans/').
 */
function buildLocaleHref(
  targetLocale: string,
  defaultLocale: string,
  currentLocale: string,
  locales: readonly string[],
  siteBaseUrl: string,  // may be '/ai-coding-101/' OR '/ai-coding-101/zh-Hans/'
  pathname: string,     // from useLocation()
): string {
  // ── Step 1: recover the ROOT base URL ─────────────────────────────────────
  // siteConfig.baseUrl may include the current locale path; strip it.
  let rootBase = siteBaseUrl.replace(/\/$/, ''); // '/ai-coding-101' or '/ai-coding-101/zh-Hans'
  if (currentLocale !== defaultLocale) {
    const suffix = '/' + currentLocale; // '/zh-Hans'
    if (rootBase.endsWith(suffix)) {
      rootBase = rootBase.slice(0, -suffix.length); // '/ai-coding-101'
    }
  }

  // ── Step 2: extract rel path from pathname ─────────────────────────────────
  let rel: string;
  if (pathname.startsWith(rootBase + '/')) {
    rel = pathname.slice(rootBase.length); // '/zh-Hans/docs/intro' or '/docs/intro'
  } else if (pathname === rootBase || pathname === rootBase + '/') {
    rel = '/';
  } else {
    // pathname may already be relative (no base prefix) — use as-is
    rel = pathname.startsWith('/') ? pathname : '/' + pathname;
  }

  // ── Step 3: strip any non-default locale prefix from rel ──────────────────
  for (const locale of locales) {
    if (locale === defaultLocale) continue;
    const p = '/' + locale;
    if (rel === p || rel === p + '/') { rel = '/'; break; }
    if (rel.startsWith(p + '/')) { rel = rel.slice(p.length); break; }
  }

  // ── Step 4: prepend target locale prefix ──────────────────────────────────
  const prefix = targetLocale === defaultLocale ? '' : '/' + targetLocale;
  return rootBase + prefix + rel;
}

interface Props {
  mobile?: boolean;
  [key: string]: unknown;
}

export default function LocaleDropdownNavbarItem({mobile}: Props): ReactNode {
  const {
    i18n: {currentLocale, locales, localeConfigs, defaultLocale},
    siteConfig: {baseUrl},
  } = useDocusaurusContext();

  const {pathname} = useLocation();
  const currentLabel = localeConfigs[currentLocale]?.label ?? currentLocale;

  // ── Mobile sidebar ─────────────────────────────────────────────────────────
  if (mobile) {
    return (
      <>
        {locales.map((locale) => {
          const label = localeConfigs[locale]?.label ?? locale;
          const href = buildLocaleHref(locale, defaultLocale, currentLocale, locales, baseUrl, pathname);
          return (
            <li key={locale} className="menu__list-item">
              <a
                href={href}
                className={`menu__link${locale === currentLocale ? ' menu__link--active' : ''}`}
              >
                {label}
              </a>
            </li>
          );
        })}
      </>
    );
  }

  // ── Desktop navbar dropdown ────────────────────────────────────────────────
  return (
    <div className="navbar__item dropdown dropdown--hoverable dropdown--right">
      <span className="navbar__link" style={{cursor: 'default'}}>
        {currentLabel}
      </span>
      <ul className="dropdown__menu">
        {locales.map((locale) => {
          const label = localeConfigs[locale]?.label ?? locale;
          const href = buildLocaleHref(locale, defaultLocale, currentLocale, locales, baseUrl, pathname);
          return (
            <li key={locale}>
              <a
                href={href}
                className={`dropdown__link${locale === currentLocale ? ' dropdown__link--active' : ''}`}
              >
                {label}
              </a>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
