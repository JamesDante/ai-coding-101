import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';

import styles from './index.module.css';

type LocaleContent = {
  eyebrow: string;
  title: ReactNode;
  subtitle: string;
  cta: string;
  layoutTitle: string;
  layoutDesc: string;
};

const content: Record<string, LocaleContent> = {
  en: {
    eyebrow: 'AI Coding Tutorial',
    title: <>Build Smarter<br />with AI</>,
    subtitle: 'From prompt engineering to multi-agent systems — a practical guide for developers.',
    cta: 'Start Learning →',
    layoutTitle: 'AI Coding 101',
    layoutDesc: 'From prompt engineering to multi-agent systems — a practical guide for developers.',
  },
  'zh-Hans': {
    eyebrow: 'AI 编程教程',
    title: <>用 AI 写出<br />更好的代码</>,
    subtitle: '从提示词工程到多智能体系统，面向开发者的 AI 辅助编程实践指南。',
    cta: '开始学习 →',
    layoutTitle: 'AI Coding 101 · AI 编程教程',
    layoutDesc: '从提示词工程到多智能体系统，面向开发者的 AI 辅助编程实践指南。',
  },
};

function HomepageHeader() {
  const {i18n: {currentLocale}} = useDocusaurusContext();
  const t = content[currentLocale] ?? content['en'];

  return (
    <header className={styles.heroBanner}>
      <div className={styles.heroInner}>
        {/* Left: Text */}
        <div className={styles.heroText}>
          <span className={styles.eyebrow}>{t.eyebrow}</span>
          <h1 className={styles.heroTitle}>{t.title}</h1>
          <p className={styles.heroSubtitle}>{t.subtitle}</p>
          <div className={styles.heroCtas}>
            <Link className={styles.ctaPrimary} to="/docs/intro">
              {t.cta}
            </Link>
            <a
              className={styles.ctaSecondary}
              href="https://github.com/JamesDante/ai-coding-101"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
          </div>
        </div>

        {/* Right: Terminal */}
        <div className={styles.terminalWrap}>
          <div className={styles.terminal}>
            <div className={styles.terminalBar}>
              <span className={styles.dot} style={{background: '#ff5f57'}} />
              <span className={styles.dot} style={{background: '#febc2e'}} />
              <span className={styles.dot} style={{background: '#28c840'}} />
              <span className={styles.terminalTitle}>claude — zsh</span>
            </div>
            <pre className={styles.terminalBody}>
              <code>
                <span className={styles.prompt}>$ </span>
                <span className={styles.cmd}>claude "build a REST API with JWT auth"</span>
                {'\n\n'}
                <span className={styles.success}>✓</span>
                <span className={styles.step}> Analyzing requirements...</span>
                {'\n'}
                <span className={styles.success}>✓</span>
                <span className={styles.step}> Scaffolding Express project</span>
                {'\n'}
                <span className={styles.success}>✓</span>
                <span className={styles.step}> Adding JWT middleware</span>
                {'\n'}
                <span className={styles.success}>✓</span>
                <span className={styles.step}> Writing unit tests</span>
                {'\n\n'}
                <span className={styles.done}>Done in 3.8s</span>
                <span className={styles.cursor}> ▌</span>
              </code>
            </pre>
          </div>
        </div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const {i18n: {currentLocale}} = useDocusaurusContext();
  const t = content[currentLocale] ?? content['en'];

  return (
    <Layout title={t.layoutTitle} description={t.layoutDesc}>
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
